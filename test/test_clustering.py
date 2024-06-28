import csv
import unittest
import os
import tempfile
from work_set_clustering.clustering import clusterFromScratch as initialClustering
from work_set_clustering.clustering import updateClusters as updateClusters
from test.test_cases import InitialClusteringSize, InitialElementsTogether, UpdateClusteringSize, UpdateClusteringElementsTogether

# Don't show the traceback of an AssertionError, because the AssertionError already says what the issue is!
__unittest = True

# ---------------------------------------------------------------------------
def readOutput(filename):
  """This helper function reads the output of a clusterin run and creates a data structure with cluster assignments."""

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
class TestClusteringSingleInput(InitialClusteringSize, InitialElementsTogether, unittest.TestCase):
  """A concrete integration test class that executes tests of the TestClustering class for a clustering with a single input files."""

  # ---------------------------------------------------------------------------
  def getInitialClusterData(self):
    return TestClusteringSingleInput.initialClusterData

  # ---------------------------------------------------------------------------
  @classmethod
  def setUpClass(cls):
    cls.tempInitialClusters = os.path.join(tempfile.gettempdir(), 'initial-clusters.csv')

    # Cluster from scratch
    #
    initialClustering(
      inputFilenames=["test/resources/cluster-input-1.csv"],
      outputFilename=cls.tempInitialClusters,
      idColumnName="elementID",
      keyColumnName="descriptiveKey",
      delimiter=","
    )

    # read the script output into an internal data structure
    #
    cls.initialClusterData = readOutput(cls.tempInitialClusters)

   # ---------------------------------------------------------------------------
  @classmethod
  def tearDownClass(cls):
    if os.path.isfile(cls.tempInitialClusters):
      os.remove(cls.tempInitialClusters)


# -----------------------------------------------------------------------------
class TestUpdateClusteringSingleInput(UpdateClusteringSize,UpdateClusteringElementsTogether, unittest.TestCase):
  """A concrete integration test class that executes tests for the update of clusters with a single input files."""

  # ---------------------------------------------------------------------------
  def getUpdatedClusterData(self):
    return TestUpdateClusteringSingleInput.updatedClusterData

  # ---------------------------------------------------------------------------
  @classmethod
  def setUpClass(cls):
    cls.tempNewClusters = os.path.join(tempfile.gettempdir(), 'updated-clusters.csv')

    # Cluster
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
    cls.updatedClusterData = readOutput(cls.tempNewClusters)

   # ---------------------------------------------------------------------------
  @classmethod
  def tearDownClass(cls):
    if os.path.isfile(cls.tempNewClusters):
      os.remove(cls.tempNewClusters)



# -----------------------------------------------------------------------------
class TestClusteringMultipleInput(InitialClusteringSize, InitialElementsTogether, unittest.TestCase):
  """A concrete integration test class that executes tests for a clustering with several input files."""

  # ---------------------------------------------------------------------------
  def getInitialClusterData(self):
    return TestClusteringMultipleInput.initialClusterData

  # ---------------------------------------------------------------------------
  @classmethod
  def setUpClass(cls):
    cls.tempInitialClusters = os.path.join(tempfile.gettempdir(), 'initial-clusters-multiple-input-files.csv')

    # Cluster from scratch
    #
    initialClustering(
      inputFilenames=["test/resources/cluster-input-1.1.csv", "test/resources/cluster-input-1.2.csv"],
      outputFilename=cls.tempInitialClusters,
      idColumnName="elementID",
      keyColumnName="descriptiveKey",
      delimiter=","
    )

    # read the script output into an internal data structure
    #
    cls.initialClusterData = readOutput(cls.tempInitialClusters)

   # ---------------------------------------------------------------------------
  @classmethod
  def tearDownClass(cls):
    if os.path.isfile(cls.tempInitialClusters):
      os.remove(cls.tempInitialClusters)

# -----------------------------------------------------------------------------
class TestClusteringOverlappingKeysDifferentClustersReusingKeys(UpdateClusteringSize, UpdateClusteringElementsTogether, unittest.TestCase):
  """A concrete integration test class that executes tests of the TestClustering class for a clustering with a single input file an."""

  # ---------------------------------------------------------------------------
  def getUpdatedClusterData(self):
    return TestClusteringOverlappingKeysDifferentClustersReusingKeys.updatedClusterData

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
