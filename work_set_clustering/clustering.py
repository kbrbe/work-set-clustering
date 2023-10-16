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
def main(inputFilename, outputFilename, idColumnName, keyColumnName, delimiter):
  """This script performs a clustering of the input data based on common descriptive keys."""

  with open(inputFilename, 'r') as inFile, \
       open(outputFilename, 'w') as outFile:

    inputReader = csv.DictReader(inFile, delimiter=delimiter)
    lib.checkIfColumnsExist(inputReader.fieldnames, [idColumnName, keyColumnName])

    elementIDs = set()
    descriptiveKeys = {}

    # Populate the two data structures above with values from the input file
    # A sorted list of element identifiers is returned based on the given elementIDs set
    elementIDs = readElements(inputReader, elementIDs, descriptiveKeys, idColumnName, keyColumnName)

    clusterInvertedIndex(elementIDs, descriptiveKeys, outFile)

    print("finished")


# -----------------------------------------------------------------------------
def addElementsToCluster(elements, clusterID, clusters, elementToCluster):
  clusters[clusterID].update(elements)
  for element in elements:
    elementToCluster[element] = clusterID

# -----------------------------------------------------------------------------
def clusterInvertedIndex(elementIDs, descriptiveKeys, outFile):

  start_time_index = time.time()
  keysToElements = {}
  for elementID, dKeys in descriptiveKeys.items():
    for dKey in dKeys:
      if dKey in keysToElements:
        keysToElements[dKey].add(elementID)
      else:
        keysToElements[dKey] = set([elementID])

  end_time_index = time.time()
  diffTimeIndex = time.strftime('%H:%M:%S', time.gmtime(end_time_index - start_time_index))
  print(f'Inverted index computed in {diffTimeIndex}')

  start_time_clustering = time.time()
  clusters = {}
  elementToCluster = {}

  for dKey, elementIDs in keysToElements.items():
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
        addElementsToCluster(elementsInNoCluster, clusterID, clusters, elementToCluster)
    else:
      newClusterID = str(uuid.uuid4())

      if len(existingClusters) == 0:
        # no existing clusters found, create a new one
        clusters[newClusterID] = elementIDs
        for element in elementIDs:
          elementToCluster[element] = newClusterID

        if len(elementsInNoCluster) > 0:
          addElementsToCluster(elementsInNoCluster, newClusterID, clusters, elementToCluster)

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
          addElementsToCluster(elementsInNoCluster, newClusterID, clusters, elementToCluster)

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
def parseArguments():

  parser = argparse.ArgumentParser()
  parser.add_argument('-i', '--input-file', action='store', required=True, help="The CSV file with columns for elements and descriptive keys, one row is one element and descriptive key relationship")
  parser.add_argument('-o', '--output-file', action='store', required=True, help='The name of the output CSV file containing two columns: elementID and clusterID')
  parser.add_argument('--id-column', action='store', required=True, help='The name of the column with element identifiers')
  parser.add_argument('--key-column', action='store', required=True, help="The name of the column that contains a descriptive key")
  parser.add_argument('--delimiter', action='store', default=',', help="Optional delimiter of the input/output CSV, default is ','")
  options = parser.parse_args()

  return options

# -----------------------------------------------------------------------------
if __name__ == '__main__':
  options = parseArguments()
  main(options.input_file, options.output_file, options.id_column, options.key_column, options.delimiter)
 
