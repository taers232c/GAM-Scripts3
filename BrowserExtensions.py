#!/usr/bin/env python3
"""
# Purpose: Show browser extension information
# See: https://cloud.google.com/blog/products/chrome-enterprise/enhanced-extension-reporting-with-chrome-browsers-takeout-api
#
# Note: This script can use GAM7 or Advanced GAM:
#       https://github.com/GAM-team/GAM                                                                                                                               
#	https://github.com/taers232c/GAMADV-XTD3
# Customize: MAX_BROWSERS_TO_PROCESS, MAX_ITEMS_PER_LIST, DESIRED_COLUMN_ORDER, SORT_COLUMN, SEPARATOR
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Get browser information
#  $ gam redirect csv ./BrowserInfo.csv print browsers fields browsers,machinename formatjson quotechar "'"
# 2: Format browser extension information
#  $ python3 ./BrowserExtensions.py BrowserInfo.csv ExtensionsInfo.csv
"""

import csv
import json
import sys

INPUT_QUOTE_CHAR = "'"
OUTPUT_QUOTE_CHAR = '"'
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'
FIX_DOUBLE_SLASH_QUOTE = False # Set to true if you get json.decoder.JSONDecodeError: Expecting ',' delimiter:

MAX_BROWSERS_TO_PROCESS = 0 # 0 = process all browsers, N = limit processing to N browsers
MAX_ITEMS_PER_LIST = 0 # 0 = Use cell length splitting, N = Use maximum items in a list splitting
MAX_ITEMS_LISTS = ['installed', 'disabled', 'forced'] # Properties to apply MAX_ITEMS_PER_LIST
DESIRED_COLUMN_ORDER = [
  'id', 'name', 'num_permissions', 'num_installed', 'num_disabled',
  'num_forced', 'permissions', 'installed', 'disabled', 'forced'
  ]
SORT_COLUMN = 'name' # Sort the data on this column
SEPARATOR = ', ' # Separates machine names

extensionsList = {} # The extension list dictionary to fill.
allColumns = set() # Set of all columns that are found in the data

def ComputeExtensionsList(data):
  """Computes list of machines that have an extension.

  This sample function processes the |data| retrieved from the Takeout API and
  calculates the list of machines that have installed each extension listed in
  the data.

  Args:
    data: the data fetched from the Takeout API.
  """
  for browser in data.get('browsers', []):
    for profile in browser.get('profiles', []):
      for extension in profile.get('extensions', []):
        key = extension['extensionId']
        if 'version' in extension:
          key = key + ' @ ' + extension['version']
        if key not in extensionsList:
          current_extension = {
              'name': extension.get('name', ''),
              'permissions': extension.get('permissions', ''),
              'installed': set(),
              'disabled': set(),
              'forced': set()
          }
        else:
          current_extension = extensionsList[key]

        machine_name = data['machineName']
        current_extension['installed'].add(machine_name)
        if extension.get('installType', '') == 'ADMIN':
          current_extension['forced'].add(machine_name)
        if extension.get('disabled', False):
          current_extension['disabled'].add(machine_name)

        extensionsList[key] = current_extension

def DictToList(data, key_name='id'):
  """Converts a dict into a list.

  The value of each member of |data| must also be a dict. The original key for
  the value will be inlined into the value, under the |key_name| key.

  Args:
    data: a dict where every value is a dict
    key_name: the name given to the key that is inlined into the dict's values

  Yields:
    The values from |data|, with each value's key inlined into the value.
  """
  assert isinstance(data, dict), '|data| must be a dict'
  for key, value in data.items():
    assert isinstance(value, dict), '|value| must contain dict items'
    value[key_name] = key
    yield value

def Flatten(data):
  """Flattens lists inside |data|, one level deep.

  This function will flatten each dictionary key in |data| into a single row
  so that it can be written to a CSV file.

  Args:
    data: the data to be flattened.

  Yields:
    A list of dict objects whose lists or sets have been flattened.
  """

  # Max length of a cell in Excel is technically 32767 characters but if we get
  # too close to this limit Excel seems to create weird results when we open
  # the CSV file. To protect against this, give a little more buffer to the max
  # characters.
  MAX_CELL_LENGTH = 32700

  for item in data:
    added_item = {}
    for prop, value in item.items():
      # Non-container properties can be added directly.
      if not isinstance(value, (list, set)):
        added_item[prop] = value
        continue

      # Otherwise join the container together into a single cell.
      num_prop = 'num_' + prop
      added_item[num_prop] = len(value)

      if MAX_ITEMS_PER_LIST > 0 and prop in MAX_ITEMS_LISTS:
        # For specified long lists, split the list into chunks of length MAX_ITEMS_PER_LIST
        flat_list = sorted(value)
        bcount = 0
        jcount = added_item[num_prop]
        overflow_prop_index = 0
        current_column = prop
        added_item[current_column] = ''
        while bcount < jcount:
          kcount = min(jcount-bcount, MAX_ITEMS_PER_LIST)
          added_item[current_column] = SEPARATOR.join(flat_list[bcount:bcount+kcount])
          bcount += kcount
          overflow_prop_index += 1
          current_column = f'{prop}_{overflow_prop_index}'
      else:
        # For long lists, the cell contents may go over MAX_CELL_LENGTH, so
        # split the list into chunks that will fit into MAX_CELL_LENGTH.
        flat_list = SEPARATOR.join(sorted(value))
        overflow_prop_index = 0
        while True:
          current_column = prop
          if overflow_prop_index:
            current_column = prop + '_' + str(overflow_prop_index)

          flat_list_len = len(flat_list)
          if flat_list_len > MAX_CELL_LENGTH:
            last_separator = flat_list.rfind(SEPARATOR, 0,
                                             MAX_CELL_LENGTH - flat_list_len)
            if last_separator != -1:
              added_item[current_column] = flat_list[0:last_separator]
              flat_list = flat_list[last_separator + 2:]
              overflow_prop_index = overflow_prop_index + 1
              continue

          # Fall-through case where no more splitting is possible, this is the
          # last cell to add for this list.
          added_item[current_column] = flat_list
          break

      assert isinstance(added_item[prop],
                        (int, bool, str)), (f'unexpected type for item: {type(added_item[prop]).__name__}')

    allColumns.update(added_item.keys())
    yield added_item


# Process browser extension data
with open(sys.argv[1], 'r', encoding='utf-8') as inputFile:
  inputCSV = csv.DictReader(inputFile, quotechar=INPUT_QUOTE_CHAR)
  browsersProcessed = 0
  for r in inputCSV:
    if not FIX_DOUBLE_SLASH_QUOTE:
      rawData = r['JSON']
    else:
      rawData = r['JSON'].replace(r'\\"', r'\"')
    ComputeExtensionsList(json.loads(rawData))
    browsersProcessed += 1
    if MAX_BROWSERS_TO_PROCESS > 0 and browsersProcessed == MAX_BROWSERS_TO_PROCESS:
      break

# Write extensions CSV file
flattenedList = list(Flatten(DictToList(extensionsList)))

# Order the columns as desired. Columns other than those in
# |DESIRED_COLUMN_ORDER| will be in an unspecified order after these columns.
orderedFieldnames = []
for c in DESIRED_COLUMN_ORDER:
  matchingColumns = []
  for f in allColumns:
    if f == c or f.startswith(c):
      matchingColumns.append(f)
  orderedFieldnames.extend(sorted(matchingColumns))

orderedFieldnames.extend([x for x in DESIRED_COLUMN_ORDER if x not in orderedFieldnames])
with open(sys.argv[2], mode='w', newline='', encoding='utf-8') as outputCSV:
  outputCSV = csv.DictWriter(outputCSV, fieldnames=orderedFieldnames, lineterminator=LINE_TERMINATOR, quotechar=OUTPUT_QUOTE_CHAR)
  outputCSV.writeheader()
  for row in sorted(flattenedList, key=lambda ext: ext[SORT_COLUMN]):
    outputCSV.writerow(row)
