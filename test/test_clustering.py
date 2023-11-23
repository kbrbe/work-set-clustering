import unittest
import tempfile
import csv
import os
from work_set_clustering.clustering import main as clustering

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
      if elementID in data['elementToCluster']:
        data['elementToCluster'][elementID].add(clusterID)
      else:
        data['elementToCluster'][elementID] = set([clusterID])
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

    # Cluster from scratch
    #
    clustering(
      inputFilename="test/resources/cluster-input-1.csv",
      outputFilename=cls.tempInitialClusters,
      idColumnName="elementID",
      keyColumnName="descriptiveKey",
      delimiter=","
    )

    # Cluster more
    #
    clustering(
      inputFilename="test/resources/cluster-input-2.csv",
      outputFilename=cls.tempNewClusters,
      idColumnName="elementID",
      keyColumnName="descriptiveKey",
      delimiter=","
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


if __name__ == '__main__':
  unittest.main()
