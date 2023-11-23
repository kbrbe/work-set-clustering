import unittest
import tempfile
import csv
import os
from work_set_clustering.clustering import clusterFromScratch as initialClustering
from work_set_clustering.clustering import updateClusters as updateClusters

# Don't show the traceback of an AssertionError, because the AssertionError already says what the issue is!
__unittest = True

# ---------------------------------------------------------------------------
def readOutput(filename):
 with open(filename, 'r') as fileIn:
    csvReader = csv.DictReader(fileIn, delimiter=',')

    data = {
      'clusterIdentifiers': set(),
      'elementIdentifiers': set(),
      'elementToCluster': {},
      'clusterToElement': {}
    }

    for row in csvReader:
      elementID = row['elementID']
      clusterID = row['clusterID']
      data['elementIdentifiers'].add(elementID)
      data['clusterIdentifiers'].add(clusterID)
      data['elementToCluster'][elementID] = clusterID
      if clusterID in data['clusterToElement']:
        data['clusterToElement'][clusterID].add(elementID)
      else:
        data['clusterToElement'][clusterID] = set([elementID])

    return data


# -----------------------------------------------------------------------------
class TestClustering(unittest.TestCase):

  # ---------------------------------------------------------------------------
  @classmethod
  def setUpClass(cls):
    cls.tempInitialClusters = os.path.join(tempfile.gettempdir(), 'initial-clusters.csv')
    cls.tempNewClusters = os.path.join(tempfile.gettempdir(), 'updated-clusters.csv')

    print('Initial clustering ...')
    # Cluster from scratch
    #
    initialClustering(
      inputFilename="test/resources/cluster-input-1.csv",
      outputFilename=cls.tempInitialClusters,
      idColumnName="elementID",
      keyColumnName="descriptiveKey",
      delimiter=","
    )

    print()
    print('Update clusters ...')
    # Cluster more
    #
    updateClusters(
      inputFilename="test/resources/cluster-input-2.csv",
      outputFilename=cls.tempNewClusters,
      idColumnName="elementID",
      keyColumnName="descriptiveKey",
      delimiter=",",
      existingClustersFilename="test/resources/clusters-1.csv",
      existingClusterKeysFilename="test/resources/cluster-input-1.csv"
    )

    # read the script output into an internal data structure
    #
    cls.initialClusterData = readOutput(cls.tempInitialClusters)
    cls.updatedClusterData = readOutput(cls.tempNewClusters)

   # ---------------------------------------------------------------------------
  @classmethod
  def tearDownClass(cls):
    if os.path.isfile(cls.tempInitialClusters):
      os.remove(cls.tempInitialClusters)
    if os.path.isfile(cls.tempNewClusters):
      os.remove(cls.tempNewClusters)

  # ---------------------------------------------------------------------------
  def testCorrectNumberOfClusters(self):
    """With given cluster input, two clusters should be found"""
    numberFoundClusters = len(TestClustering.initialClusterData['clusterIdentifiers'])
    numberExpectedClusters = 2
    self.assertEqual(numberFoundClusters, numberExpectedClusters, msg=f'Found {numberFoundClusters} clusters instead of {numberExpectedClusters}')

  # ---------------------------------------------------------------------------
  def testElement1And2Together(self):
    """Element e1 and e2 should be clustered together"""
    clusterE1 = TestClustering.initialClusterData['elementToCluster']['e1']
    clusterE2 = TestClustering.initialClusterData['elementToCluster']['e2']
    self.assertEqual(clusterE1, clusterE2, msg=f'Different clusters for e1 and e2 ({clusterE1} != {clusterE2})')

  # ---------------------------------------------------------------------------
  def testElement3And4Together(self):
    """Element e3 and e4 should be clustered together"""
    clusterE3 = TestClustering.initialClusterData['elementToCluster']['e3']
    clusterE4 = TestClustering.initialClusterData['elementToCluster']['e4']
    self.assertEqual(clusterE3, clusterE4, msg=f'Different clusters for e3 and e4 ({clusterE3} != {clusterE4})')

  # ---------------------------------------------------------------------------
  def testElement1And5Together(self):
    """Element e5 should be clustered together with the initial e1 and e2"""
    clusterInitial = TestClustering.updatedClusterData['elementToCluster']['e1']
    clusterNew = TestClustering.updatedClusterData['elementToCluster']['e5']
    self.assertEqual(clusterInitial, clusterNew, msg=f'Different clusters for initial e1 and updated e5 ({clusterInitial} != {clusterNew})')

  # ---------------------------------------------------------------------------
  def testElement2And5Together(self):
    """Element e5 should be clustered together with the initial e1 and e2"""
    clusterInitial = TestClustering.updatedClusterData['elementToCluster']['e2']
    clusterNew = TestClustering.updatedClusterData['elementToCluster']['e5']
    self.assertEqual(clusterInitial, clusterNew, msg=f'Different clusters for initial e2 and updated e5 ({clusterInitial} != {clusterNew})')

  # ---------------------------------------------------------------------------
  def testElement7InNewCluster(self):
    """Element e7 should be clustered in a new cluster (no overlap with initial clusters)"""
    clusterOfE7 = TestClustering.updatedClusterData['elementToCluster']['e7']
    elementsOfCluster = TestClustering.updatedClusterData['clusterToElement'][clusterOfE7]
    self.assertEqual(len(elementsOfCluster), 1, msg=f'Other elements in the cluster of e7: {elementsOfCluster}')


if __name__ == '__main__':
  unittest.main()
