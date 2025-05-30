#!/usr/bin/env python3
"""
# Purpose: Make a CSV file that merges all values for a given key.
# Customize: Set KEY_FIELD and VALUE_FIELD
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Generate CSV file KeySingleValue.csv with columns KEY_FIELD and VALUE_FIELD, one key and value per row
# 2: Output an updated CSV file with columns KEY_FIELD and VALUE_FIELD containing a row per key
#    with its merged (space separated) values
#  $ python3 CombineKeyValues.py ./KeyValue.csv ./KeyMergedValues.csv
"""

import csv
import sys

# Name of key field
KEY_FIELD = 'key'
# Name of value field
VALUE_FIELD = 'value'

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

keyValues = {}

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin
for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  key = row[KEY_FIELD]
  keyValues.setdefault(key, set())
  keyValues[key].add(row[VALUE_FIELD])

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout

outputCSV = csv.DictWriter(outputFile, [KEY_FIELD, VALUE_FIELD], lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

for key, values in sorted(iter(keyValues.items())):
  outputCSV.writerow({KEY_FIELD: key, VALUE_FIELD: ' '.join(values)})

inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
