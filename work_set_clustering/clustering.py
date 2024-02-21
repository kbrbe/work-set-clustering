#
# (c) 2023 Sven Lieber
# KBR Brussels
#

import csv
import argparse
import work_set_clustering.lib as lib
import uuid
import time

# -----------------------------------------------------------------------------
def clusterFromScratch(inputFilenames, outputFilename, idColumnName, keyColumnName, delimiter):
  """This script performs a clustering of the input data based on common descriptive keys."""

  with open(outputFilename, 'w') as outFile:

    elementIDs = set()
    descriptiveKeys = {}

    for inputFilename in inputFilenames:
      with open(inputFilename, 'r') as inFile: 
        inputReader = csv.DictReader(inFile, delimiter=delimiter)
        lib.checkIfColumnsExist(inputReader.fieldnames, [idColumnName, keyColumnName])


        # Populate elementIDs and descriptiveKeys with values from the input file
        # A sorted list of element identifiers is returned based on the given elementIDs set
        currentElementIDs = readElements(inputReader, elementIDs, descriptiveKeys, idColumnName, keyColumnName)

        # update the list of all elements with the ones from the current file
        elementIDs.update(currentElementIDs)

    keysToElements = createInvertedIndexAndLogTime(descriptiveKeys)

    # for initial clustering these two should be empty
    clusters = {}
    elementToCluster = {}

    clusterInvertedIndex(elementIDs, descriptiveKeys, clusters, elementToCluster, keysToElements, outFile)

# -----------------------------------------------------------------------------
def updateClusters(inputFilenames, outputFilename, idColumnName, keyColumnName, delimiter, existingClustersFilename, existingClusterKeysFilename):
  """This script performs a clustering of the input data based on common descriptive keys."""

  with open(existingClustersFilename, 'r') as existingClustersFile, \
       open(existingClusterKeysFilename, 'r') as existingClusterKeysFile, \
       open(outputFilename, 'w') as outFile:

    elementIDs = set()
    descriptiveKeys = {}

    for inputFilename in inputFilenames:
      with open(inputFilename, 'r') as inFile: 
        inputReader = csv.DictReader(inFile, delimiter=delimiter)
        lib.checkIfColumnsExist(inputReader.fieldnames, [idColumnName, keyColumnName])

        # Populate elementIDs and descriptiveKeys with values from the input file
        # A sorted list of element identifiers is returned based on the given elementIDs set
        currentElementIDs = set(readElements(inputReader, elementIDs, descriptiveKeys, idColumnName, keyColumnName))

        # update the list of all elements with the ones from the current file
        elementIDs.update(currentElementIDs)

    existingClustersReader = csv.DictReader(existingClustersFile, delimiter=delimiter)
    existingClusterKeysReader = csv.DictReader(existingClusterKeysFile, delimiter=delimiter)

    lib.checkIfColumnsExist(existingClustersReader.fieldnames, ['elementID','clusterID'])
    lib.checkIfColumnsExist(existingClusterKeysReader.fieldnames, [idColumnName, keyColumnName])

    # Add descriptive key data from existing clusters
    allElementIDs = readElements(existingClusterKeysReader, elementIDs, descriptiveKeys, idColumnName, keyColumnName)
    keysToElements = createInvertedIndexAndLogTime(descriptiveKeys)

    clusters = {}
    elementToCluster = {}
    readClusters(existingClustersReader, clusters, elementToCluster)

    clusterInvertedIndex(allElementIDs, descriptiveKeys, clusters, elementToCluster, keysToElements, outFile)




# -----------------------------------------------------------------------------
def createInvertedIndexAndLogTime(descriptiveKeys):
  start_time_index = time.time()
  keysToElements = lib.buildInvertedIndex(descriptiveKeys)
  end_time_index = time.time()
  diffTimeIndex = time.strftime('%H:%M:%S', time.gmtime(end_time_index - start_time_index))
  print(f'Inverted index computed in {diffTimeIndex}')
  return keysToElements

# -----------------------------------------------------------------------------
def clusterInvertedIndex(elementIDs, descriptiveKeys, clusters, elementToCluster, keysToElements, outFile):

  start_time_clustering = time.time()

  for dKey, elementIDs in keysToElements.items():

    # two helper data structures for the current iteration
    existingClusters = set()
    elementsInNoCluster = set()

    for element in elementIDs:
      if element in elementToCluster:
        existingClusters.add(elementToCluster[element])
      else:
        # those have to be added to a cluster
        elementsInNoCluster.add(element)

    if len(existingClusters) == 1:
      # sets have unique members: one or more of the elements are in the same cluster
      if len(elementsInNoCluster) > 0:
        # some of the elements are not yet in the cluster
        clusterID = existingClusters.pop()
        lib.addElementsToCluster(elementsInNoCluster, clusterID, clusters, elementToCluster)
    else:
      newClusterID = str(uuid.uuid4())

      if len(existingClusters) == 0:
        # no existing clusters found, create a new one
        clusters[newClusterID] = elementIDs
        for element in elementIDs:
          elementToCluster[element] = newClusterID

        if len(elementsInNoCluster) > 0:
          lib.addElementsToCluster(elementsInNoCluster, newClusterID, clusters, elementToCluster)

      elif len(existingClusters) > 1:
        # the members are in more than one cluster, so those clusters should be merged
        # 1. get elements of all identified clusters
        combinedElements = set()
        for cluster in existingClusters:
          combinedElements.update(clusters[cluster])
        # 2. remove old clusters
        [clusters.pop(clusterID) for clusterID in existingClusters]
        # 3. add new merged cluster
        clusters[newClusterID] = combinedElements
        # 4. update elementToCluster (overwrite if exists, otherwise create)
        for element in combinedElements:
          elementToCluster[element] = newClusterID

        # 5. now that the new cluster is created we can add eventually clusterless elements
        if len(elementsInNoCluster) > 0:
          lib.addElementsToCluster(elementsInNoCluster, newClusterID, clusters, elementToCluster)

  end_time_clustering = time.time()
  diffTimeClustering = time.strftime('%H:%M:%S', time.gmtime(end_time_clustering - start_time_clustering))
  print(f'Clusters computed in {diffTimeClustering}')

  # write cluster assignment to the output file
  outputWriter = csv.DictWriter(outFile, fieldnames=['elementID', 'clusterID'])
  outputWriter.writeheader()

  for clusterID, memberIDSet in clusters.items():
    for memberID in memberIDSet:
      outputWriter.writerow({'elementID': memberID, 'clusterID': clusterID})
 

# -----------------------------------------------------------------------------
def readElements(inputReader, elementIDs, descriptiveKeys, idColumnName, keyColumnName):

  for row in inputReader:
    eID = row[idColumnName]
    key = row[keyColumnName]

    if eID != '' and key != '':
      elementIDs.add(eID)
      if eID in descriptiveKeys:
        descriptiveKeys[eID].add(key)
      else:
        descriptiveKeys[eID] = set([key])

  return sorted(elementIDs)

# -----------------------------------------------------------------------------
def readClusters(inputReader, clusters, elementToCluster):

  for row in inputReader:
    eID = row['elementID']
    cID = row['clusterID']
    if cID not in clusters:
      clusters[cID] = set()
    lib.addElementsToCluster([eID], cID, clusters, elementToCluster)


# -----------------------------------------------------------------------------
def parseArguments():

  parser = argparse.ArgumentParser()
  parser.add_argument('-i', '--input-file', action='append', required=True, help="The CSV file(s) with columns for elements and descriptive keys, one row is one element and descriptive key relationship")
  parser.add_argument('-o', '--output-file', action='store', required=True, help='The name of the output CSV file containing two columns: elementID and clusterID')
  parser.add_argument('--id-column', action='store', required=True, help='The name of the column with element identifiers')
  parser.add_argument('--key-column', action='store', required=True, help="The name of the column that contains a descriptive key")
  parser.add_argument('--delimiter', action='store', default=',', help="Optional delimiter of the input/output CSV, default is ','")
  parser.add_argument('--existing-clusters', action='store', help="Optional file with existing element-cluster mapping")
  parser.add_argument('--existing-clusters-keys', action='store', help="Optional file with element-descriptive key mapping for existing clusters mapping")
  options = parser.parse_args()

  if options.existing_clusters and not options.existing_clusters_keys:
    print()
    print(f'Existing clusters provided, but no file with descriptive keys for its elements')
    exit(1)

  if options.existing_clusters_keys and not options.existing_clusters:
    print()
    print(f'Descriptive keys for elements of existing clusters provided, but no file with existing cluster keys')
    exit(1)

  return options

# -----------------------------------------------------------------------------
if __name__ == '__main__':
  options = parseArguments()
  if options.existing_clusters:
    updateClusters(options.input_file, options.output_file, options.id_column, options.key_column, options.delimiter, options.existing_clusters, options.existing_clusters_keys)
  else:
    clusterFromScratch(options.input_file, options.output_file, options.id_column, options.key_column, options.delimiter)
 
