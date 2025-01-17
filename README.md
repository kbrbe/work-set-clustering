# Work-set Clustering

[![DOI](https://zenodo.org/badge/705721988.svg)](https://zenodo.org/doi/10.5281/zenodo.10011416)

A Python script to perform a clustering based on descriptive keys.
It can be used to identify _work_ clusters for _manifestations_ according to the FRBR (IFLA-LRM) model. Alternatively it can be used to cluster authority records.

This repository contains several scripts:

* `clustering` to perform the clustering based on a list of manifestation identifiers and their descriptive keys
* `get-descriptive-keys-xml` to extract manifestation identifiers and description keys directly from MARCXML files
* `get-descriptive-keys-csv` to extract manifestation identifiers and description keys from CSV files containing Python lists

If already computed cluster identifiers and descriptive keys from a previous run are provided, they can be reused to extend the initial clustering.


## Usage via the command line

Create and activate a Python virtual environment
```bash

# Create a new Python virtual environment
python3 -m venv py-request-isni-env

# Activate the virtual environment
source py-request-isni-env/bin/activate

# Install dependencies
pip install -r requirements.txt

# install the tool
pip install .
```

## descriptive key extraction

The command-line parameters for both the XML and the CSV extraction script are the same, only the JSON configuration looks slightly different. Please have a look at the provided example configurations.

Descriptive keys are created of combinations between combinations of the datafields specified in `part1`  and `part2` in the config, e.g. names and dates like `john doe/birthdate/1970-01-01`. Data fields specified in `singlePart` form a descriptive key on their own, e.g. the ISNI identifier of a person, created with a prefix, e.g. `isni/0000000000000001`

If one specifies the `dataType` `date`, additional `year` descriptive keys are created. For example `john doe/birthyear/1970`.


Available options

```
usage: get_descriptive_keys_from_xml.py [-h] -c CONFIG_FILE -o OUTPUT_FILE inputFiles [inputFiles ...]

This script reads one or more XML files and based on a config creates descriptive keys of available field values

positional arguments:
  inputFiles            The inputs file containing XML records

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG_FILE, --config-file CONFIG_FILE
                        The config file with XPath expressions to extract
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
                        The output CSV file containing possible descriptive keys based on the key composition config

```

### clustering script

Available options:

```
usage: clustering.py [-h] -i INPUT_FILE -o OUTPUT_FILE --id-column ID_COLUMN --key-column KEY_COLUMN [--delimiter DELIMITER] [--existing-clusters EXISTING_CLUSTERS]
                     [--existing-clusters-keys EXISTING_CLUSTERS_KEYS]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_FILE, --input-file INPUT_FILE
                        The CSV file(s) with columns for elements and descriptive keys, one row is one element and descriptive key relationship
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

#### Clustering from scratch
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

The script can also read descriptive keys that are distributed across several files.
Therefore you only have to use the `--input-file` parameter several times.
Please note that all of those input files should have the same column names specified with `--id-column` and `--key-column`.

You can find more examples of cluster input in the `test/resources` directory.

#### Reuse existing clusters

You can reuse the clusters created from an earlier run,
but you also have to provide the mapping between the previous elements and optionally their descriptive keys.


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

Similar to the initial clustering, you can provide several input files.

> [!NOTE]
> When skipping existing descriptive keys, existing cluster identifiers and assigments are kept, even if their elements have overlapping descriptive keys. Additionally, none of the new elements can be mapped to the existing clusters, because no descriptive keys are provided (more info in https://github.com/kbrbe/work-set-clustering/issues/9)

## Usage as a library

The tool can also be used as a library within another Python script or a Jupyter notebook.

### clustering script

```python
from work_set_clustering.clustering import clusterFromScratch as clustering

clustering(
  inputFilename=["descriptive-keys.csv"],
  outputFilename="cluster-assignments.csv",
  idColumnName="elementID",
  keyColumnName="descriptiveKey",
  delimiter=',')
```

Or if you want to reuse existing clusters:

```python
from work_set_clustering.clustering import updateClusters as clustering

clustering(
  inputFilename=["descriptive-keys.csv"],
  outputFilename="cluster-assignments.csv",
  idColumnName="elementID",
  keyColumnName="descriptiveKey",
  delimiter=',',
  existingClustersFilename="existing-clusters.csv",
  existingClusterKeysFilename="initial-descriptive-keys.csv")
```

## Software Tests

* You can execute the unit tests of the `lib.py` file with the following command: `python work_set_clustering.lib`.
* You can execute the integration tests with the following command: `python -m unittest discover -s test`

## Contact

Sven Lieber - Sven.Lieber@kbr.be - Royal Library of Belgium (KBR) - https://www.kbr.be/en/

