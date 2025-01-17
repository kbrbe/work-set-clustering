#
# (c) 2022 Sven Lieber
# KBR Brussels
#
#import xml.etree.ElementTree as ET
import lxml.etree as ET
import os
import json
import itertools
import enchant
import hashlib
import csv
from argparse import ArgumentParser
from tqdm import tqdm
from . import descriptive_key_utils as utils
import stdnum

NS_MARCSLIM = 'http://www.loc.gov/MARC21/slim'

ALL_NS = {'marc': NS_MARCSLIM}

# -----------------------------------------------------------------------------
def main(inputFilenames, configFilename, outputFilename):
  """This script reads an XML file in MARC slim format and extracts several fields to create a CSV file."""


  with open(configFilename, 'r') as configFile:
    config = json.load(configFile)
  
  config['counters'] = {
    'recordCounter': 0,
    'name bigger than 5 words': 0,
    'fileCounter': 0,
    'filteredRecordCounter': 0,
    'filteredRecordExceptionCounter': 0
  }

  
  #
  # Instead of loading everything to main memory, stream over the XML using iterparse
  #
  with open(outputFilename, 'w') as outFile:

    outputFields = ['authorityID', 'descriptiveKey']
    outputWriter = csv.DictWriter(outFile, fieldnames=outputFields, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    outputWriter.writeheader()

    fileCounter = 0
    recordCounter = 0
    updateFrequency = 100
    pbar = tqdm(inputFilenames)
    pbar.total = None

    # used for namespace-agnostic extraction of XML-parsed records
    recordTag = getRecordTagName(config)

    for inputFilename in pbar:
      config['counters']['fileCounter'] += 1

      # if the XML file is huge, memory becomes an issue even while streaming because a reference to the parent is kept
      # therefore we first get the root element
      # https://stackoverflow.com/questions/12160418/why-is-lxml-etree-iterparse-eating-up-all-my-memory
      context = ET.iterparse(inputFilename, tag=recordTag)
      utils.fast_iter(
        context, # the XML context
        processRecord, # the function that is called for every found recordTag
        pbar, # the progress bar that should be updated
        config, # configuration object with counters and other data
        outputWriter, # parameter for processRecord: CSV writer for output file
        updateFrequency=updateFrequency, # after how many records the progress bar should be updated
      )
      print(config['counters'])

# -----------------------------------------------------------------------------
def processRecord(elem, config, outputWriter):

  if "recordFilter" in config:
    try:
      if not utils.passFilter(elem, config["recordFilter"]):
        config['counters']['filteredRecordCounter'] += 1
        return None
    except Exception as e:
        recordID = utils.getElementValue(elem.find(config['recordIDExpression'], ALL_NS))
        config['counters']['filteredRecordExceptionCounter'] += 1
        return None

  for authorityID, descriptiveKey in getDescriptiveKeys(elem, config):
    outputWriter.writerow({"authorityID": authorityID, "descriptiveKey": descriptiveKey })




# -----------------------------------------------------------------------------
def getValueList(elem, config, configKey):

  datePatterns = config["datePatterns"]
  valueDelimiter = ';'
  keyParts = []

  # first check if we can extract the data we should extract
  #
  if configKey not in config:
    print(f'No key "{configKey}" in config!')
    return None

  # for names with many components computing the permutations takes too long
  # thus we handle a maximum of 5 permutatons
  defaultMaxPermutations = 5

  authorityID = utils.getElementValue(elem.find(config['recordIDExpression'], ALL_NS))
  #print(f'authorityID: {authorityID}')
  # check each config entry
  #
  for p in config[configKey]:
    expression = p['expression']
    values = None

    maxPermutations = p["maxPermutations"] if 'maxPermutations' in p else defaultMaxPermutations

    # extract the data
    #
    values = elem.xpath(expression, namespaces=ALL_NS)

    # process all extracted data (possibly more than one value)
    #
    if values:
      newValues = set()
      for v in values:
        vText = v.text
        vNorm = None

        if vText:
          # parse different value types, for example dates or regular strings
          #
          if 'valueType' in p:
            valueType = p['valueType']
            if valueType == 'date':
              utils.handleDate(vText, p, newValues, config['datePatterns'])
            elif valueType == 'isniURL':
              isniComponents = vText.split('isni.org/isni/')
              if len(isniComponents) > 1:
                vNorm = isniComponents[1]
                utils.addDescriptiveKeyValue(vNorm, p, newValues)
              else:
                print(f'Warning: malformed ISNI URL for authority {authorityID}: "{vText}"')
            elif valueType == 'bnfURL':
              bnfComponents = vText.split('ark:/12148/')
              if len(bnfComponents) > 1:
                vNorm = bnfComponents[1]
                utils.addDescriptiveKeyValue(vNorm, p, newValues)
              else:
                print(f'Warning: malformed BnF URL for authority {authorityID}: "{vText}"')

            else:
              # if not date or isniURL or bnfURL, parse it as text
              utils.handleText(vText, p, config, newValues, authorityID, maxPermutations)
          else:
            # parse as text by default
            utils.handleText(vText, p, config, newValues, authorityID, maxPermutations)

      keyParts.extend(newValues)
  return keyParts

# -----------------------------------------------------------------------------
def getDescriptiveKeys(elem, config):
  """This function extracts descriptive keys from the provided elements based on the provided config."""

  authorityID = utils.getElementValue(elem.find(config['recordIDExpression'], ALL_NS))
  prefixedAuthorityID = config['recordIDPrefix'] + authorityID

  # get part1's
  firstKeyParts = getValueList(elem, config, "part1")
  
  # get part2's
  secondKeyParts = getValueList(elem, config, "part2")

  # for each part1 create a combination with a part2
  descriptiveKeys = []
  for key1 in firstKeyParts:
    for key2 in secondKeyParts:
      yield [prefixedAuthorityID, f'{key1}/{key2}']

  # some key values are already unique identifiers
  uniqueKeys = getValueList(elem, config, "singlePart")
  for uk in uniqueKeys:
    yield [prefixedAuthorityID, f'{uk}']

# -----------------------------------------------------------------------------
def getRecordTagName(config):

  recordTagString = config['recordTag']
  recordTag = None
  if ':' in recordTagString:
    prefix, tagName = recordTagString.split(':')
    recordTag = ET.QName(ALL_NS[prefix], tagName)
  else:
    recordTag = recordTagString

  return recordTag



# -----------------------------------------------------------------------------
def parseArguments():

  parser = ArgumentParser(description='This script reads one or more XML files and based on a config creates descriptive keys of available field values')
  parser.add_argument('inputFiles', nargs='+', help='The inputs file containing XML records')
  parser.add_argument('-c', '--config-file', action='store', required=True, help='The config file with XPath expressions to extract')
  parser.add_argument('-o', '--output-file', action='store', required=True, help='The output CSV file containing possible descriptive keys based on the key composition config')
  args = parser.parse_args()

  return args

if __name__ == '__main__':
  args = parseArguments()
  main(args.inputFiles, args.config_file, args.output_file)
