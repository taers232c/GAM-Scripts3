#!/usr/bin/env python3
"""
# Purpose: For a CSV file with JSON columns, produce a file with no header row and only JSON data.
# Customize: Set QUOTE_CHAR, LINE_TERMINATOR, MERGE_NON_JSON_DATA, NON_JSON_DATA_SKIP_FIELDS, MAKE_LIST
# Usage:
# 1: Produce a CSV file Input.csv
# 2: Produce a JSON file Output.json
#  $ python ./ConvertCSVtoJSON.py Input.csv Output.json
"""

import csv
import json
import sys

QUOTE_CHAR = "'" # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'
MERGE_NON_JSON_DATA = True # False to omit data from non-JSON columns
NON_JSON_DATA_SKIP_FIELDS = [] # List of non-JSON columns that should not be merged, e.g, ['a',] ['a', 'b']
MAKE_LIST = True
# When MAKE_LIST = True, output is
# [
#   {"key": "value"},
#   {"key": "value"},
# ]
# When MAKE_LIST = False, output is
#   {"key": "value"}
#   {"key": "value"}

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w', newline='')
else:
  outputFile = sys.stdout
if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin
inputCSV = csv.DictReader(inputFile, quotechar=QUOTE_CHAR)
plainFields = []
jsonFields = []
for fieldName in inputCSV.fieldnames:
  if fieldName.startswith('JSON'):
    jsonFields.append(fieldName)
  elif MERGE_NON_JSON_DATA and fieldName not in NON_JSON_DATA_SKIP_FIELDS:
    plainFields.append(fieldName)
jsonRows = []
for row in inputCSV:
  jsonRow = {}
  for k in plainFields:
    jsonRow[k] = row[k]
  for k in jsonFields:
    jsonRow.update(json.loads(row[k]))
  jsonRows.append(jsonRow)
if MAKE_LIST:
  outputFile.write('['+LINE_TERMINATOR)
  lineTerminator = ','+LINE_TERMINATOR
  for jsonRow in jsonRows:
    outputFile.write('  '+json.dumps(jsonRow, ensure_ascii=False, sort_keys=True)+lineTerminator)
  outputFile.write(']'+LINE_TERMINATOR)
else:
  for jsonRow in jsonRows:
    outputFile.write(json.dumps(jsonRow, ensure_ascii=False, sort_keys=True)+LINE_TERMINATOR)

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
