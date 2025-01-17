#
# (c) 2024 Sven Lieber
# KBR Brussels
#
import ast
import os
import json
import enchant
import hashlib
import csv
from argparse import ArgumentParser
from tqdm import tqdm
from . import descriptive_key_utils as utils
import stdnum


# -----------------------------------------------------------------------------
def main(inputFilenames, configFilename, outputFilename):

  # read the config file
  #
  with open(configFilename, 'r') as configFile:
    config = json.load(configFile)  
  
  with open(outputFilename, 'w') as outFile:

    outputFields = ['authorityID', 'descriptiveKey']
    outputWriter = csv.DictWriter(outFile, fieldnames=outputFields, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    outputWriter.writeheader()

    fileCounter = 0
    recordCounter = 0
    updateFrequency = 100
    pbar = tqdm(inputFilenames)
    pbar.total = None

    for inputFilename in pbar:
      fileCounter += 1

      with open(inputFilename, 'r') as inFile:
        inputReader = csv.DictReader(inFile)

        for row in inputReader:
          for authorityID, descriptiveKey in getDescriptiveKeys(row, config):
            outputWriter.writerow({"authorityID": authorityID, "descriptiveKey": descriptiveKey })

          recordCounter += 1
          if recordCounter % updateFrequency == 1:
            pbar.set_description(f'files {fileCounter}/{len(pbar)}; records: {recordCounter}')
            pbar.update()
    pbar.close()

# -----------------------------------------------------------------------------
def getDescriptiveKeys(row, config):
  """This function extracts descriptive keys from the provided row based on the provided config."""

  authorityID = row[config["recordIDColumn"]]

  # get part1's
  firstKeyParts = getValueList(row, config, "part1")
  
  # get part2's
  secondKeyParts = getValueList(row, config, "part2")

  #print(f'firstKeyParts: {firstKeyParts}')
  #print(f'secondKeyParts: {secondKeyParts}')
  #print()
  # for each part1 create a combination with a part2
  descriptiveKeys = []
  for key1 in firstKeyParts:
    for key2 in secondKeyParts:
      yield [authorityID, f'{key1}/{key2}']

  # some key values are already unique identifiers
  uniqueKeys = getValueList(row, config, "singlePart")
  for uk in uniqueKeys:
    yield [authorityID, f'{uk}']


# -----------------------------------------------------------------------------
def getValueList(row, config, configKey):

  valueDelimiter = ';'
  keyParts = []

  # first check if we can extract the data we should extract
  #
  if configKey not in config:
    print(f'No key "{configKey}" in config!')
    return None

  recordID = row[config['recordIDColumn']]

  # for names with many components computing the permutations takes too long
  # thus we handle a maximum of 5 permutatons
  defaultMaxPermutations = 5

  # check each config entry and try to add values to allValues
  #
  allValues = set()
  for columnConfig in config[configKey]:
    columnName = columnConfig['columnName']
    dataType = columnConfig['dataType'] if 'dataType' in columnConfig else 'text'

    if columnName in row:
      maxPermutations = columnConfig["maxPermutations"] if 'maxPermutations' in columnConfig else defaultMaxPermutations
      if row[columnName] != '':

        # we handle CSV files where each value is a Python list, e.g. "['value1', 'value2']" or "[{'val1': 'value1'}, {'val1': 'value1'}]"
        # get the values of the array (strings or dictionaries)
        values = ast.literal_eval(row[columnName])

        # process each element of the list of values stored in the column
        for vText in values:

          if isinstance(vText, dict):
            utils.handleDictionary(vText, columnConfig, allValues, maxPermutations)             
            
          elif isinstance(vText, str):
            if dataType == 'text':
              utils.handleText(vText, columnConfig, config, allValues, recordID, maxPermutations)

            elif dataType == 'date':
              utils.handleDate(vText, columnConfig, allValues, config['datePatterns'])

          else:
            # so far we only handle strings or dictionaries
            print(f'Script handles strings or dictionaries, but other type found for "{vText}"')

  return allValues


# -----------------------------------------------------------------------------
def parseArguments():

  parser = ArgumentParser(description='This script reads one or more CSV files and based on a config creates descriptive keys of available column values')
  parser.add_argument('inputFiles', nargs='+', help='The input file containing CSV records')
  parser.add_argument('-c', '--config-file', action='store', required=True, help='The config file with instructions how to build the descriptive keys')
  parser.add_argument('-o', '--output-file', action='store', required=True, help='The output CSV file containing descriptive keys based on the key composition config')
  args = parser.parse_args()

  return args


if __name__ == '__main__':
  args = parseArguments()
  main(args.inputFiles, args.config_file, args.output_file)
