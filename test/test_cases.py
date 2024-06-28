import unittest
import csv

# -----------------------------------------------------------------------------
class InitialClusteringSize():
  """A class with integration tests covering the number of clusters for the initial clustering"""

  # ---------------------------------------------------------------------------
  def testCorrectNumberOfClusters(self):
    """With given cluster input, two clusters should be found"""
    numberFoundClusters = len(self.getInitialClusterData()['clusterIdentifiers'])
    numberExpectedClusters = 2
    self.assertEqual(numberFoundClusters, numberExpectedClusters, msg=f'Found {numberFoundClusters} clusters instead of {numberExpectedClusters}')

# -----------------------------------------------------------------------------
class UpdateClusteringSize():
  """A class with integration tests covering the number of clusters for the initial clustering"""

  # ---------------------------------------------------------------------------
  def testCorrectNumberOfClusters(self):
    """With given cluster input, three clusters should be found"""
    numberFoundClusters = len(self.getUpdatedClusterData()['clusterIdentifiers'])
    numberExpectedClusters = 3
    self.assertEqual(numberFoundClusters, numberExpectedClusters, msg=f'Found {numberFoundClusters} clusters instead of {numberExpectedClusters}')


# -----------------------------------------------------------------------------
class InitialElementsTogether():
  """A class with integration test cases in case only the initial clustering is performed."""

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

# -----------------------------------------------------------------------------
class UpdateClusteringElementsTogether():
  """A class with integration test cases for updated clusters."""

  # ---------------------------------------------------------------------------
  def testElement1And5Together(self):
    """New element e5 should be clustered together with the initial e1 and e2"""
    clusterInitial = self.getUpdatedClusterData()['elementToCluster']['e1']
    clusterNew = self.getUpdatedClusterData()['elementToCluster']['e5']
    self.assertEqual(clusterInitial, clusterNew, msg=f'Different clusters for initial e1 and updated e5 ({clusterInitial} != {clusterNew})')

  # ---------------------------------------------------------------------------
  def testElement1SameClusterIDAfterUpdate(self):
    """Element e1 should have the same clusterID after update when e5 was added"""
    clusterInitial = self.getUpdatedClusterData()['elementToCluster']['e1']
    clusterNew = "c1"
    self.assertEqual(clusterInitial, clusterNew, msg=f'Initial cluster of e1 has changed after update ({clusterInitial} != {clusterNew})')

  # ---------------------------------------------------------------------------
  def testElement5SameClusterIDAfterUpdate(self):
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


