#!/usr/bin/env python3
"""
# Purpose: For a CSV file with JSON columns, produce a file with no header row (optional) and only JSON data.
# Customize: Set INPUT_QUOTE_CHAR, OUTPUT_QUOTE_CHAR, LINE_TERMINATOR, MERGE_NON_JSON_DATA, NON_JSON_DATA_SKIP_FIELDS, MAKE_LIST, HEADER_ROW
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Produce a CSV file Input.csv
# 2: Produce a JSON file Output.json
#  $ python3 ./ConvertCSVtoJSON.py Input.csv Output.json
"""

import csv
import json
import sys

INPUT_QUOTE_CHAR = "'" # Adjust as needed
OUTPUT_QUOTE_CHAR = "'" # Adjust as desired; can be empty ""
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

MERGE_NON_JSON_DATA = False # True - Merge data from non-JSON columns; False to omit data from non-JSON columns
NON_JSON_DATA_SKIP_FIELDS = [] # List of non-JSON columns that should not be merged, e.g, ['a',] ['a', 'b']
MAKE_LIST = False
HEADER_ROW = True # True - Header row JSON; False - no header row. Only applies when MAKE_LIST = False
# When MAKE_LIST = True: output is
# [
#   {"key": "value", "key": "value"},
#   {"key": "value", "key": "value"},
#   {"key": "value", "key": "value"}
# ]
# When MAKE_LIST = False, HEADER_ROW = False: output is
#   '{"key": "value", "key": "value"}'
#   '{"key": "value", "key": "value"}'
# When MAKE_LIST = False, HEADER_ROW = True: output is
#   JSON
#   '{"key": "value", "key": "value"}'
#   '{"key": "value", "key": "value"}'

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin
inputCSV = csv.DictReader(inputFile, quotechar=INPUT_QUOTE_CHAR)
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
  outputFile.seek(outputFile.tell()-(1+len(LINE_TERMINATOR)), 0)
  outputFile.write(LINE_TERMINATOR+']'+LINE_TERMINATOR)
else:
  if HEADER_ROW:
    outputFile.write('JSON'+LINE_TERMINATOR)
  for jsonRow in jsonRows:
    outputFile.write(OUTPUT_QUOTE_CHAR+json.dumps(jsonRow, ensure_ascii=False, sort_keys=True)+OUTPUT_QUOTE_CHAR+LINE_TERMINATOR)
if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
