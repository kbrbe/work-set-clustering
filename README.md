# Work-set Clustering

A Python script to perform a clustering based on descriptive keys.
It can be used to identify _work_ clusters for _manifestations_ according to the FRBR (IFLA-LRM) model.

This tool only performs the clustering. It needs a list of manifestation identifiers and their descriptive keys as input.


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

Available options:

```python
python -m work_set_clustering.clustering --help
usage: clustering.py [-h] -i INPUT_FILE -o OUTPUT_FILE --id-column ID_COLUMN --key-column KEY_COLUMN [--delimiter DELIMITER]

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
```


## Usage as a library

The tool can also be used as a library within another Python script or a Jupyter notebook.

```python
from work_set_clustering.clustering import main as clustering

clustering(
  inputFilename="descriptive-keys.csv",
  outputFilename="cluster-assignments.csv",
  idColumnName="elementID",
  keyColumnName="descriptiveKey",
  delimiter=',')
```

## Contact

Sven Lieber - Sven.Lieber@kbr.be - Royal Library of Belgium (KBR) - https://www.kbr.be/en/

