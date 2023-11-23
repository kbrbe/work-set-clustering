# Work-set Clustering

[![DOI](https://zenodo.org/badge/705721988.svg)](https://zenodo.org/doi/10.5281/zenodo.10011416)

A Python script to perform a clustering based on descriptive keys.
It can be used to identify _work_ clusters for _manifestations_ according to the FRBR (IFLA-LRM) model.

This tool only performs the clustering. It needs a list of manifestation identifiers and their descriptive keys as input.
If already computed cluster identifiers and descriptive keys from a previous run are provided, they can be reused.


## Usage via the command line

Create and activate a Python virtual environment
```bash

# Create a new Python virtual environment
python3 -m venv py-request-isni-env

# Activate the virtual environment
source py-request-isni-env/bin/activate

# There are no depdendenies to install

# install the tool
pip install .
```

Available options:

```
usage: clustering.py [-h] -i INPUT_FILE -o OUTPUT_FILE --id-column ID_COLUMN --key-column KEY_COLUMN [--delimiter DELIMITER] [--existing-clusters EXISTING_CLUSTERS]
                     [--existing-clusters-keys EXISTING_CLUSTERS_KEYS]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_FILE, --input-file INPUT_FILE
                        The CSV file with columns for elements and descriptive keys, one row is one element and descriptive key relationship
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
                        The name of the output CSV file containing two columns: elementID and clusterID
  --id-column ID_COLUMN
                        The name of the column with element identifiers
  --key-column KEY_COLUMN
                        The name of the column that contains a descriptive key
  --delimiter DELIMITER
                        Optional delimiter of the input/output CSV, default is ','
  --existing-clusters EXISTING_CLUSTERS
                        Optional file with existing element-cluster mapping
  --existing-clusters-keys EXISTING_CLUSTERS_KEYS
                        Optional file with element-descriptive key mapping for existing clusters mapping

```

### Clustering from scratch
Given a CSV file where each row contains the relationship
between one manifestation identifier and one descriptive key,
the tool can be called the following to create cluster assignments.

```python
python -m work_set_clustering.clustering \
  --input-file "descriptive-keys.csv" \
  --output-file "clusters.csv" \
  --id-column "elementID" \
  --key-column "descriptiveKey"
```

Example CSV which should result in two clusters, one for book1 and book2 (due to a similar key) and one for book3:

|elementID|descriptiveKey|
|---------|--------------|
|book1|theTitle/author1|
|book1|isbnOfTheBook/author1|
|book2|isbnOfTheBook/author1|
|book3|otherBookTitle/author1|

You can find more examples of cluster input in the `test/resources` directory.

### Reuse existing clusters

You can reuse the clusters created from an earlier run,
but you also have to provide the mapping between the previous elements and their descriptive keys.


```python
python -m work_set_clustering.clustering \
  --input-file "descriptive-keys.csv" \
  --output-file "clusters.csv" \
  --id-column "elementID" \
  --key-column "descriptiveKey" \
  --existing-clusters "existing-clusters.csv" \
  --existing-cluster-keys "initial-descriptive-keys.csv"
```

Please note that with the two parameters `--existing-clusters` and `--existing-cluster-keys`
the data from a previous run are provided.

## Usage as a library

The tool can also be used as a library within another Python script or a Jupyter notebook.

```python
from work_set_clustering.clustering import clusterFromScratch as clustering

clustering(
  inputFilename="descriptive-keys.csv",
  outputFilename="cluster-assignments.csv",
  idColumnName="elementID",
  keyColumnName="descriptiveKey",
  delimiter=',')
```

Or if you want to reuse existing clusters:

```python
from work_set_clustering.clustering import updateClusters as clustering

clustering(
  inputFilename="descriptive-keys.csv",
  outputFilename="cluster-assignments.csv",
  idColumnName="elementID",
  keyColumnName="descriptiveKey",
  delimiter=',',
  existingClustersFilename="existing-clusters.csv",
  existingClusterKeysFilename="initial-descriptive-keys.csv")
```


## Contact

Sven Lieber - Sven.Lieber@kbr.be - Royal Library of Belgium (KBR) - https://www.kbr.be/en/

