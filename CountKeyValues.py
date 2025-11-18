#!/usr/bin/env python3
"""
# Purpose: Make a CSV file showing the number of instances of a key field
# Customize: Set KEY_FIELD, MIN_KEY_COUNT
# Python: Use python or python3 below as appropriate to your system; verify that you have version  3.9 or greater
#  $ python -V   or python3 -V
#  Python 3.x.y
# Usage:
# 1: Generate a CSV file KeyValues.csv
# 2: From that CSV file, output a CSV file with headers "Key,Count" that shows the
#    number of instances if each key value
#  $ python3 CountKeyValues.py ./KeyValues.csv ./KeyValueCounts.csv
"""

import csv
import sys

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

KEY_FIELD = '' # Set to a column header in KeyValues.csv
MIN_KEY_COUNT = 0 # 0 - Show all counts; N - Show counts >= N

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['Key', 'Count'], lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin

keyCounts = {}
for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  keyValue = row[KEY_FIELD]
  keyCounts.setdefault(keyValue, 0)
  keyCounts[keyValue] += 1
for key, count in sorted(keyCounts.items()):
  if count >= MIN_KEY_COUNT:
    outputCSV.writerow({'Key': key, 'Count': count})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
