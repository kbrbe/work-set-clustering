# Explanation of test cases

> [!NOTE]
> For an explanation of test data, please consult the README file in the directory `resources`.

## Reusable test case functions
Reusable test cases grouped in classes are defined in the file `test_cases.py`

* InitialClusteringSize
* InitialElementsTogether
* UpdateClusteringSize
* UpdateClusteringElementsTogether
* UpdateClusteringSizeReusing
* UpdateClusteringNotReusingKeysElementsTogether


## Test cases
The following test cases exist in the file `test_clustering.py`
Each test case reuses actual test functions via inheritance from test case functions in `test_cases.py` (see above) and/or defines their own additional test cases

### TestClusteringSingleInput
Initial clustering with a single descriptive key file (`cluster-input-1.csv`)

### TestUpdateClusteringSingleInput
Update of clustering with `cluster-input-2.csv`

### TestClusteringMultipleInput
Initial clustering with multiple descriptive key files (`cluster-input-1.1.csv`, `cluster-input-1.2.csv`)

### TestClusterOverlappingKeysDifferentClusters
Update of clusters `clusters-1-overlap.csv` with `cluster-input-2.csv`

### TestClusterOverlappingKeysDifferentClustersReusingKeys
Update of clusters `clusters-1-overlap.csv` with `cluster-input-2.csv` by also reusing descriptive keys `cluster-input-1.csv`

