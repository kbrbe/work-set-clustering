# Explanation of test data

* For an initial clustering we have the elements `e1, e2, e3, e4` and their descriptive keys in the file `cluster-input-1.csv`
* For an update of clusters we have the new elements `e5, e6, e7` and their descriptive keys in the file `cluster-input-2.csv`

Initially, `e1` and `e2`  share at least one descriptive key as well as `e3` and `e4`.
Hence there will be two clusters with random unique identifiers: `(e1, e2)`  and `(e3, e4)`

When considering the second file to update the clusters, `e5` will be merged with `(e1, e2)` due to an overlapping descriptive key,
`e6` will be merged with `(e3, e4)` due to an overlapping descriptive key,
and `e7` will form its own cluster with a single element `(e7)`, because it does not share a descriptive key with any other element.

When for an update we consider the file `clusters-1.csv` (representing a correct clustering of the first input) with the following clusters and identifiers `c1: (e1, e2)` and `c2: (e3, e4)`
we expect that the mentioned cluster identifiers `c1` and `c2` are reused.

# Different clusters based on human judgement, despite overlapping descriptive keys

However, we also want to test what happens if due to a human assignment, elements are clustered differently despite of overlapping descriptive keys (https://github.com/kbrbe/work-set-clustering/issues/9)

Therefore we use the file `clusters-1-overlap.csv` where we get the clusters `c1: (e1, e2)`, `c2: (e3)` and `c3: (e4)`.

Please note that `e3` and `e4` still share descriptive keys according to the file `cluster-input-1.csv`.
Whether or not we reuse the existing keys will influence the outcome.
