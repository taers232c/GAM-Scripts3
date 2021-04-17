#!/usr/bin/env python3
"""
# Purpose: Merge two CSV files with user data
# Note: This script can use Basic or Advanced GAM:
#	https://github.com/jay0lee/GAM
#	https://github.com/taers232c/GAMADV-XTD3
# Customize: DATA_KEY_FIELD, MERGE_KEY_FIELD, MERGE_RETAIN_FIELDS
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Generate the two data files, e.g.:
#  $ gam print users fields primaryemail,name,phones,organizations > ./Data.csv
#  $ gam all users print sendas > ./Merge.csv
# 2: Merge files
#  $ python3 MergeUserData.py ./Data.csv ./Merge.csv ./DataMerge.csv
"""

import csv
import sys

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

# Key field in data file
DATA_KEY_FIELD = 'primaryEmail'
# Key field in merge file
MERGE_KEY_FIELD = 'User'
# Merge fields to retain, leave empty fpr all fields
MERGE_RETAIN_FIELDS = []

userData = {}
dataFileName = sys.argv[1]
dataFile = open(dataFileName, 'r', encoding='utf-8')
dataCSV = csv.DictReader(dataFile, quotechar=QUOTE_CHAR)
dataFieldNames = dataCSV.fieldnames[:]
for row in dataCSV:
  userData[row[DATA_KEY_FIELD]] = row
dataFile.close()

mergeFileName = sys.argv[2]
mergeFile = open(mergeFileName, 'r', encoding='utf-8')
mergeCSV = csv.DictReader(mergeFile, quotechar=QUOTE_CHAR)
mergeFieldNames = mergeCSV.fieldnames[:]

errors = 0
if not MERGE_RETAIN_FIELDS:
  mergeRetainFields = mergeFieldNames
else:
  mergeRetainFields = []
  for fieldName in MERGE_RETAIN_FIELDS:
    if fieldName in mergeFieldNames:
      mergeRetainFields.append(fieldName)
    else:
      errors = 1
      sys.stderr.write(f'Merge field {fieldName} is not in {mergeFileName} headers: {",".join(mergeFieldNames)}\n')
  if errors:
    sys.exit(1)
outputFieldNames = dataFieldNames[:]
mergeFieldNameMap = {}
for fieldName in mergeRetainFields:
  if fieldName not in dataFieldNames:
    mappedFieldName= fieldName
  else:
    mappedFieldName = f'{fieldName}-Merge'
  mergeFieldNameMap[fieldName] = mappedFieldName
  outputFieldNames.append(mappedFieldName)

outputFileName = sys.argv[3]
outputFile = open(outputFileName, 'w', encoding='utf-8', newline='')
outputCSV = csv.DictWriter(outputFile, outputFieldNames, lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

errors = False
for row in mergeCSV:
  if row[MERGE_KEY_FIELD] in userData:
    orow = userData[row[MERGE_KEY_FIELD]]
    for fieldName in mergeFieldNameMap:
      orow[mergeFieldNameMap[fieldName]] = row[fieldName]
    outputCSV.writerow(orow)
  else:
    errors = 1
    sys.stderr.write(f'Merge key field {row[MERGE_KEY_FIELD]} in {mergeFileName} does not occur in {dataFileName}\n')
mergeFile.close()
outputFile.close()
sys.exit(errors)
