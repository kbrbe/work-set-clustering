# -----------------------------------------------------------------------------
def checkIfColumnsExist(inputColumnNames, outputColumnNames):
    """This function checks if all names of the second list are present in the first, if not an Error is raised.

    The function simply returns true if all names are present
    >>> checkIfColumnsExist(['a', 'b', 'c'], ['a', 'c'])
    True

    If a name is missing an Exception is thrown mentioning which names are missing
    >>> checkIfColumnsExist(['a', 'b', 'c'], ['a', 'd'])
    Traceback (most recent call last):
        ...
    Exception: The following requested column is not in the input: {'d'}
    """
    inputColumns = set(inputColumnNames)
    outputColumns = set(outputColumnNames)
    nonExistentColumns = outputColumns.difference(inputColumns)
    if len(nonExistentColumns) > 0:
      text = 'columns are' if len(nonExistentColumns) > 1 else 'column is'
      raise Exception(f'The following requested {text} not in the input: {nonExistentColumns}')
    else:
        return True


