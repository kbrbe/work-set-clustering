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
class TestClustering():
  """A class with integration test cases for different implementations."""

  # ---------------------------------------------------------------------------
  def testCorrectNumberOfClusters(self):
    """With given cluster input, two clusters should be found"""
    numberFoundClusters = len(self.getInitialClusterData()['clusterIdentifiers'])
    numberExpectedClusters = 2
    self.assertEqual(numberFoundClusters, numberExpectedClusters, msg=f'Found {numberFoundClusters} clusters instead of {numberExpectedClusters}')

  # ---------------------------------------------------------------------------
  def testElement1And2Together(self):
    """Element e1 and e2 should be clustered together"""
    clusterE1 = self.getInitialClusterData()['elementToCluster']['e1']
    clusterE2 = self.getInitialClusterData()['elementToCluster']['e2']
    self.assertEqual(clusterE1, clusterE2, msg=f'Different clusters for e1 and e2 ({clusterE1} != {clusterE2})')

  # ---------------------------------------------------------------------------
  def testElement3And4Together(self):
    """Element e3 and e4 should be clustered together"""
    clusterE3 = self.getInitialClusterData()['elementToCluster']['e3']
    clusterE4 = self.getInitialClusterData()['elementToCluster']['e4']
    self.assertEqual(clusterE3, clusterE4, msg=f'Different clusters for e3 and e4 ({clusterE3} != {clusterE4})')

  # ---------------------------------------------------------------------------
  def testElement1And5Together(self):
    """Element e5 should be clustered together with the initial e1 and e2"""
    clusterInitial = self.getUpdatedClusterData()['elementToCluster']['e1']
    clusterNew = self.getUpdatedClusterData()['elementToCluster']['e5']
    self.assertEqual(clusterInitial, clusterNew, msg=f'Different clusters for initial e1 and updated e5 ({clusterInitial} != {clusterNew})')

  # ---------------------------------------------------------------------------
  def testElement1SameClusterAfterUpdate(self):
    """Element e1 should have the same clusterID after update when e5 was added"""
    clusterInitial = self.getUpdatedClusterData()['elementToCluster']['e1']
    clusterNew = "c1"
    self.assertEqual(clusterInitial, clusterNew, msg=f'Initial cluster of e1 has changed after update ({clusterInitial} != {clusterNew})')

  # ---------------------------------------------------------------------------
  def testElement5SameClusterAfterUpdate(self):
    """Element e5 should be in the same clusterID as the initial e1"""
    clusterID = self.getUpdatedClusterData()['elementToCluster']['e5']
    clusterExpected = "c1"
    self.assertEqual(clusterID, clusterExpected, msg=f'Element e5 was not added to the existing clusterID of e1 ({clusterID} != {clusterExpected})')

  # ---------------------------------------------------------------------------
  def testElement2And5Together(self):
    """Element e5 should be clustered together with the initial e1 and e2"""
    clusterInitial = self.getUpdatedClusterData()['elementToCluster']['e2']
    clusterNew = self.getUpdatedClusterData()['elementToCluster']['e5']
    self.assertEqual(clusterInitial, clusterNew, msg=f'Different clusters for initial e2 and updated e5 ({clusterInitial} != {clusterNew})')

  # ---------------------------------------------------------------------------
  def testElement7InNewCluster(self):
    """Element e7 should be clustered in a new cluster (no overlap with initial clusters)"""
    clusterOfE7 = self.getUpdatedClusterData()['elementToCluster']['e7']
    elementsOfCluster = self.getUpdatedClusterData()['clusterToElement'][clusterOfE7]
    self.assertEqual(len(elementsOfCluster), 1, msg=f'Other elements in the cluster of e7: {elementsOfCluster}')


# -----------------------------------------------------------------------------
class TestClusteringSingleInput(TestClustering, unittest.TestCase):
  """A concrete integration test class that executes tests of the TestClustering class for a clustering with a single input files."""

  # ---------------------------------------------------------------------------
  def getInitialClusterData(self):
    return TestClusteringSingleInput.initialClusterData

  # ---------------------------------------------------------------------------
  def getUpdatedClusterData(self):
    return TestClusteringSingleInput.updatedClusterData

  # ---------------------------------------------------------------------------
  @classmethod
  def setUpClass(cls):
    cls.tempInitialClusters = os.path.join(tempfile.gettempdir(), 'initial-clusters.csv')
    cls.tempNewClusters = os.path.join(tempfile.gettempdir(), 'updated-clusters.csv')

    print('Initial clustering ...')
    # Cluster from scratch
    #
    initialClustering(
      inputFilenames=["test/resources/cluster-input-1.csv"],
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
      inputFilenames=["test/resources/cluster-input-2.csv"],
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



# -----------------------------------------------------------------------------
class TestClusteringMultipleInput(TestClustering, unittest.TestCase):
  """A concrete integration test class that executes tests of the TestClustering class for a clustering with several input files."""

  # ---------------------------------------------------------------------------
  def getInitialClusterData(self):
    return TestClusteringMultipleInput.initialClusterData

  # ---------------------------------------------------------------------------
  def getUpdatedClusterData(self):
    return TestClusteringMultipleInput.updatedClusterData

  # ---------------------------------------------------------------------------
  @classmethod
  def setUpClass(cls):
    cls.tempInitialClusters = os.path.join(tempfile.gettempdir(), 'initial-clusters-multiple-input-files.csv')
    cls.tempNewClusters = os.path.join(tempfile.gettempdir(), 'updated-clusters-multiple-input-files.csv')

    print('Initial clustering with several descriptive key input files ...')
    # Cluster from scratch
    #
    initialClustering(
      inputFilenames=["test/resources/cluster-input-1.1.csv", "test/resources/cluster-input-1.2.csv"],
      outputFilename=cls.tempInitialClusters,
      idColumnName="elementID",
      keyColumnName="descriptiveKey",
      delimiter=","
    )

    print()
    print('Update clusters created with several descriptive key input files ...')
    # Cluster more
    #
    updateClusters(
      inputFilenames=["test/resources/cluster-input-2.csv"],
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




if __name__ == '__main__':
  unittest.main()
