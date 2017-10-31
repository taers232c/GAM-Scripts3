#!/usr/bin/env python3
"""
# Purpose: For a CSV file, delete the duplcate rows based an a field. You can optionally delete unwanted fields.
# Usage:
# 1: Produce a CSV file Input.csv
# 2: Delete the duplicate rows
#  $ python ./DeleteDuplicateRows.py Input.csv Output.csv
"""

import csv
import sys

ID_FIELD = 'id' # Field name to use for duplicate checking
DELETE_FIELDS = [] # Fields to delete; Single field ['Field',]; multiple fields ['Field1', 'Field2', ...]
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w')
else:
  outputFile = sys.stdout
if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r'!)
else:
  inputFile = sys.stdin

inputData = csv.DictReader(inputFile)
outputFieldnames = inputData.fieldnames[:]
deleteFieldnames = []
for field in DELETE_FIELDS:
  if field in outputFieldnames:
    outputFieldnames.remove(field)
    deleteFieldnames.append(field)
outputData = csv.DictWriter(outputFile, outputFieldnames, lineterminator=LINE_TERMINATOR)
outputData.writeheader()
previousId = None
for row in sorted(inputData, key=lambda row: (row[ID_FIELD]), reverse=False):
  currentId = row[ID_FIELD]
  if currentId != previousId:
    for field in deleteFieldnames:
      row.pop(field, None)
    outputData.writerow(row)
    previousId = currentId
if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
