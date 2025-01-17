from datetime import datetime
import itertools
import xml.etree.ElementTree as ET
import unicodedata as ud
import ast
import enchant
import re

# -----------------------------------------------------------------------------
def parseYear(year, patterns):
  """"This function returns a string representing a year based on the input and a list of possible patterns.

  >>> parseYear('2021', ['%Y'])
  '2021'
  >>> parseYear('2021', ['(%Y)', '%Y'])
  '2021'
  >>> parseYear('(2021)', ['%Y', '(%Y)'])
  '2021'
  """

  parsedYear = None
  for p in patterns:

    try:
      tmp = datetime.strptime(year, p).date().year
      parsedYear = str(tmp)
      break
    except ValueError:
      pass

  if parsedYear == None:
    return year
  else:
    return parsedYear

# -----------------------------------------------------------------------------
def parseDate(date, patterns):
  """"This function returns a string representing a date based on the input and a list of possible patterns.

  >>> parseDate('2021', ['%Y'])
  '2021'
  >>> parseDate('2021', ['(%Y)', '%Y'])
  '2021'
  >>> parseDate('(2021)', ['%Y', '(%Y)'])
  '2021'

  A correct date string for a correct input.
  >>> parseDate('1988-04-25', ['%Y-%m-%d'])
  '1988-04-25'

  A correct date string for dates with slash.
  >>> parseDate('25/04/1988', ['%Y-%m-%d', '%Y/%m/%d', '%Y/%m/%d', '%d/%m/%Y'])
  '1988-04-25'

  An empty value if the pattern is not found.
  >>> parseDate('25/04/1988', ['%Y-%m-%d', '%Y/%m/%d'])
  ''

  A correct date string for dates without delimiter.
  >>> parseDate('19880425', ['%Y-%m-%d', '%Y%m%d'])
  '1988-04-25'

  Only year and month are invalid.
  >>> parseDate('1988-04', ['%Y%m', '%Y-%m'])
  ''
  >>> parseDate('198804', ['%Y-%m', '%Y%m'])
  ''

  Keep year if this is the only provided information.
  >>> parseDate('1988', ['%Y-%m-%d', '%Y'])
  '1988'

  Keep year if it is in round or square brackets or has a trailing dot.
  >>> parseDate('[1988]', ['%Y', '[%Y]'])
  '1988'
  >>> parseDate('(1988)', ['(%Y)'])
  '1988'
  >>> parseDate('1988.', ['%Y', '%Y.'])
  '1988'


  """

  parsedDate = None
  for p in patterns:

    try:
      # try if the value is a year
      tmp = datetime.strptime(date, p).date()
      if len(date) == 4:
        parsedDate = str(tmp.year)
      elif len(date) > 4 and len(date) <= 7:
        if any(ele in date for ele in ['(', '[', ')', ']', '.']):
          parsedDate = str(tmp.year)
        else:
          parsedDate = ''
      else:
        parsedDate = str(tmp)
      break
    except ValueError:
      pass

  if parsedDate == None:
    return ''
  else:
    return parsedDate



# -----------------------------------------------------------------------------
def getElementValue(elem, sep=';'):
  """This function returns the value of the element if it is not None, otherwise an empty string.

  The function returns the 'text' value if there is one
  >>> class Test: text = 'hello'
  >>> obj = Test()
  >>> getElementValue(obj)
  'hello'

  It returns nothing if there is no text value
  >>> class Test: pass
  >>> obj = Test()
  >>> getElementValue(obj)
  ''

  And the function returns a semicolon separated list in case the argument is a list of objects with a 'text' attribute
  >>> class Test: text = 'hello'
  >>> obj1 = Test()
  >>> obj2 = Test()
  >>> getElementValue([obj1,obj2])
  'hello;hello'

  In case one of the list values is empty
  >>> class WithContent: text = 'hello'
  >>> class WithoutContent: text = None
  >>> obj1 = WithContent()
  >>> obj2 = WithoutContent()
  >>> getElementValue([obj1,obj2])
  'hello'
  """
  if elem is not None:
    if isinstance(elem, list):
      valueList = list()
      for e in elem:
        if hasattr(e, 'text'):
          if e.text is not None:
            valueList.append(e.text)
      return sep.join(valueList)
    else:
      if hasattr(elem, 'text'):
        return elem.text
  
  return ''


# -----------------------------------------------------------------------------
def getNormalizedString(s):
  """This function returns a normalized copy of the given string.

  >>> getNormalizedString("HeLlO")
  'hello'
  >>> getNormalizedString("judaïsme, islam, christianisme, ET sectes apparentées")
  'judaisme islam christianisme et sectes apparentees'
  >>> getNormalizedString("chamanisme, de l’Antiquité…)")
  'chamanisme de lantiquite)'

  >>> getNormalizedString("Abe Ce De ?")
  'abe ce de'
  >>> getNormalizedString("Abe Ce De !")
  'abe ce de'
  >>> getNormalizedString("Abe Ce De :")
  'abe ce de'

  >>> getNormalizedString("A. W. Bruna & zoon")
  'a w bruna & zoon'
  >>> getNormalizedString("A.W. Bruna & Zoon")
  'aw bruna & zoon'

  #>>> getNormalizedString("---")
  #''

  #>>> getNormalizedString("c----- leopard")
  #'c leopard'
  
  """
  charReplacements = {
    '.': '',
    ',': '',
    '?': '',
    '!': '',
    ':': '',
    ';': ''
  }

  # by the way: only after asci normalization the UTF character for ... becomes ...
  asciiNormalized = ud.normalize('NFKD', s).encode('ASCII', 'ignore').lower().strip().decode("utf-8")

  normalized = ''.join([charReplacements.get(char, char) for char in asciiNormalized])
  noDots = normalized.replace('...', '')
  # remove double whitespaces using trick from stackoverflow.com/questions/8270092/remove-all-whitespace-in-a-string
  return " ".join(noDots.split())
  
  
# -----------------------------------------------------------------------------
def addDescriptiveKeyValue(value, configEntry, keyValues, prefixSuffix=''):
  """This function adds the value to found values based on some rules found in configEntry.

  >>> keys = set(['existingKey'])
  >>> addDescriptiveKeyValue("myKey",{"prefix": "myPrefix"}, keys)
  >>> sorted(keys)[1]
  'myPrefix/myKey'

  >>> addDescriptiveKeyValue("myKey2",{"prefix": "myPrefix"}, keys, prefixSuffix='Extra')
  >>> sorted(keys)[2]
  'myPrefixExtra/myKey2'
 
  """
  if value != '':
    if 'prefix' in configEntry:
      prefix = configEntry["prefix"] + prefixSuffix
      value = value.replace(' ','') if prefix == 'isni' else value
      keyValues.add(f'{prefix}/{value}')
    else:
      keyValues.add(f'{value}')

# -----------------------------------------------------------------------------
def passFilter(elem, filterConfig):
  """This function checks if the given element passes the specified filter condition.
     If the expression of the filter finds several elements, all have to pass the filter.

  The filter expression equals checks for equality
  >>> filterPseudonym = {"expression":"./datafield", "condition": "equals", "value": "p"}
  >>> elem0 = ET.fromstring("<root><datafield>p</datafield></root>")
  >>> passFilter(elem0, filterPseudonym)
  True

  >>> elem1 = ET.fromstring("<root><datafield>other value</datafield></root>")
  >>> passFilter(elem1, filterPseudonym)
  False

  An exception is thrown if the filter expression is not found
  >>> elem2 = ET.fromstring("<root><otherField>other value</otherField></root>")
  >>> passFilter(elem2, filterPseudonym)
  Traceback (most recent call last):
      ...
  Exception: Element with filter criteria not found, expected ./datafield

  An exception is thrown if multiple elements where found, but not all match the filter criteria
  >>> elem3 = ET.fromstring("<root><datafield>p</datafield><datafield>o</datafield></root>")
  >>> passFilter(elem3, filterPseudonym)
  Traceback (most recent call last):
      ...
  Exception: Multiple elements found and not all of them passed the filter: ['p', 'o'], equals p

  >>> elem4 = ET.fromstring("<root><datafield>o</datafield><datafield>p</datafield></root>")
  >>> passFilter(elem4, filterPseudonym)
  Traceback (most recent call last):
      ...
  Exception: Multiple elements found and not all of them passed the filter: ['o', 'p'], equals p

  If multiple elements where found, but all match the criteria all is good
  >>> elem5 = ET.fromstring("<root><datafield>p</datafield><datafield>p</datafield></root>")
  >>> passFilter(elem5, filterPseudonym)
  True

  The filter expression exists checks if the given element exists
  >>> filterExist = {"expression":"./datafield", "condition": "exists"}
  >>> elem6 = ET.fromstring("<root><datafield>p</datafield></root>")
  >>> passFilter(elem6, filterExist)
  True

  >>> elem7 = ET.fromstring("<root><otherField>p</otherField></root>")
  >>> passFilter(elem7, filterExist)
  False
  """

  filterExpression = filterConfig["expression"]
  condition = filterConfig["condition"]

  values = elem.xpath(filterExpression, namespaces=ALL_NS)
  if condition == "exists" or condition == "exist":
    if values:
      return True
    else:
      return False
  else:
    if values:
      filterPassed = []
      foundValues = []
      for value in values:
        foundValues.append(value.text)
        if condition == "equals" or condition == "equal":
          expectedValue = filterConfig["value"]
          if value.text == expectedValue:
            filterPassed.append(True)
          else:
            filterPassed.append(False)
          
      if all(filterPassed):
        return True
      else:
        if len(filterPassed) > 1:
          raise Exception(f'Multiple elements found and not all of them passed the filter: {foundValues}, {condition} {expectedValue}')
        else:
          return filterPassed[0]
    else:
      raise Exception(f'Element with filter criteria not found, expected {filterExpression}')

# -----------------------------------------------------------------------------
def fast_iter(context, func, pbar, config, outputWriter, updateFrequency=100, *args, **kwargs):
  """
  Adapted from http://stackoverflow.com/questions/12160418

  This function calls "func" for each parsed record in context.
  All name parameters of this function are used to initialize and update a progress bar.
  Other non-keyword arguments (args) and keyword arguments (kwargs) are provided to "func".
  """

  # We assume that context is configured to only fire 'end' events for tagName
  #
  for event, record in context:

    # call the given function and provide it the given parameters
    func(record, config, outputWriter, *args, **kwargs)

    # Update progress bar
    config['counters']['recordCounter'] += 1

    # clear to save RAM
    record.clear()
    # delete preceding siblings to save memory (https://lxml.de/3.2/parsing.html)
    while record.getprevious() is not None:
      del record.getparent()[0]

    if config['counters']['recordCounter'] % updateFrequency == 0:
      updateProgressBar(pbar, config, updateFrequency)

  # update the remaining count after the loop has ended
  updateProgressBar(pbar, config, updateFrequency)

  # We are done
  del context

# -----------------------------------------------------------------------------
def updateProgressBar(pbar, config, updateFrequency):
  """This function updates the given progress bar based on the given update frequency."""

  message = "##### get_descriptive_keys_from_xml #####"
  if "recordFilter" in config:
    passedFilter = config['counters']['recordCounter'] - config['counters']['filteredRecordCounter']
    pbar.set_description(f'{message} files: {config["counters"]["fileCounter"]}; records total: {config["counters"]["recordCounter"]}; passed filter: {passedFilter}; not passed filter: {config["counters"]["filteredRecordCounter"]}; could not apply filter: {config["counters"]["filteredRecordExceptionCounter"]}')
  else:
    pbar.set_description(f'{message} files: {config["counters"]["fileCounter"]}; records total: {config["counters"]["recordCounter"]}')
  pbar.update(updateFrequency)

# -----------------------------------------------------------------------------
def handleDictionary(vText, columnConfig, allValues, maxPermutations):
  if 'permutations' in columnConfig and columnConfig['permutations'] == 'True':
    try:
      handlePermutations(vText.values(), ' ', columnConfig, allValues, maxPermutations)
    except ValueError as e:
      vNorm = getNormalizedString(' '.join(vText.values()))
      addDescriptiveKeyValue(vNorm, columnConfig, allValues)
      print(f'{recordID}: single value "{vNorm}" taken')
  else:
    vNorm = getNormalizedString(' '.join(vText.values()))
    addDescriptiveKeyValue(vNorm, columnConfig, allValues)


# -----------------------------------------------------------------------------
def handleText(vText, columnConfig, config, allValues, recordID, maxPermutations):
  if 'permutations' in columnConfig and columnConfig['permutations'] == 'True':
    try:
      handlePermutations(vText.split(), ' ', columnConfig, allValues, maxPermutations)
    except ValueError as e:
      vNorm = getNormalizedString(vText)
      addDescriptiveKeyValue(vNorm, columnConfig, allValues)
      if 'counters' in config and 'name-more-than-maxPermutations-words' in config['counters']:
        config['counters'][f'name-more-than-maxPermutations-words'] += 1
      print(f'{recordID}: single value "{vText}" taken')
  else:
    vNorm = getNormalizedString(vText)
    addDescriptiveKeyValue(vNorm, columnConfig, allValues)

# -----------------------------------------------------------------------------
def handleDate(vText, columnConfig, allValues, datePatterns):

  vNorm = parseDate(vText, datePatterns)
  if vNorm == '':
    # pattern was not recognized: simply output input value
    addDescriptiveKeyValue(vText, columnConfig, allValues)
  else:
    # add the actually parsed date as output
    addDescriptiveKeyValue(vNorm, columnConfig, allValues)

    # additionally try to add the year of the date as separate key
    if len(vNorm) >= 4:
      possibleYear = vNorm[0:4]
      if possibleYear.isnumeric():
        yearColumnConfig = columnConfig.copy()
        yearColumnConfig['prefix'] = yearColumnConfig['prefix'] + 'Year'
        addDescriptiveKeyValue(possibleYear, yearColumnConfig, allValues)

      
       

# -----------------------------------------------------------------------------
def handlePermutations(values, joinChar, columnConfig, allValues, maxPermutations=5):

  if len(values) > maxPermutations:
    raise ValueError(f'Warning, value length={len(values)} exceeds maxPermutations={maxPermutations}') 
  else:
    for p in itertools.permutations(values): 
      vNorm = getNormalizedString(' '.join(p))
      addDescriptiveKeyValue(vNorm, columnConfig, allValues)





# -----------------------------------------------------------------------------
if __name__ == "__main__":
  import doctest
  doctest.testmod()
