#!/usr/bin/env python3
"""
# Purpose: For a CSV file, delete the duplcate rows based an a field. You can optionally delete unwanted fields.
# Customize: Set ID_FIELD, DELETE_FIELDS, LINE_TERMINATOR
# Usage:
# 1: Produce a CSV file Input.csv
# 2: Delete the duplicate rows
#  $ python ./DeleteDuplicateRows.py Input.csv Output.csv
"""

import csv
import sys

ID_FIELD = 'id' # Field name to use for duplicate checking
DELETE_FIELDS = [] # Fields to delete; Single field ['Field',]; multiple fields ['Field1', 'Field2', ...]

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin

inputCSV = csv.DictReader(inputFile, quotechar=QUOTE_CHAR)
outputFieldnames = inputCSV.fieldnames[:]
deleteFieldnames = []
for field in DELETE_FIELDS:
  if field in outputFieldnames:
    outputFieldnames.remove(field)
    deleteFieldnames.append(field)
outputCSV = csv.DictWriter(outputFile, outputFieldnames, lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

previousId = None
for row in sorted(inputCSV, key=lambda row: (row[ID_FIELD]), reverse=False):
  currentId = row[ID_FIELD]
  if currentId != previousId:
    for field in deleteFieldnames:
      row.pop(field, None)
    outputCSV.writerow(row)
    previousId = currentId

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
