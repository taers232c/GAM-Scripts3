#!/usr/bin/env python3
"""
# Purpose: Merge two CSV files with user data
# Methodology:
# A data CSV file is read and each row is stored in a dictionary under the key row[DATA_KEY_FIELD]
# A merge CSV file is read and row[MERGE_KEY_FIELD] is looked up in the data dictionary
# If the data row is found, the data row and merge row are combined and written to the output CSV file
# If the data row is not found, an error message is generated.
# If a merge CSV file column header matches a data CSV file column header, ".merge" is appended to the
# merge column header in the output CSV file
#
# Note: This script can use Basic or Advanced GAM:
#	https://github.com/GAM-team/GAM
#	https://github.com/taers232c/GAMADV-XTD3
# Customize: DATA_KEY_FIELD, MERGE_KEY_FIELD, RETAIN_MERGE_KEY_FIELD, MERGE_RETAIN_FIELDS, OUTPUT_UNMERGED_DATA
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Generate the two data files, e.g.:
#  $ gam print users fields primaryemail,name,phones,organizations > ./Data.csv
#  $ gam all users print sendas > ./Merge.csv
# 2: Merge files
#  $ python3 MergeUserData.py ./Data.csv ./Merge.csv ./Output.csv
"""

import csv
import sys

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

# Key field in data file; common values are primaryEmail, Owner, User
DATA_KEY_FIELD = 'primaryEmail'
# Key field in merge file; common values are primaryEmail, Owner, User
MERGE_KEY_FIELD = 'User'
# Show keys fields be shifted to lower case
LOWERCASE_KEY_FIELDS = True
# Should key field in merge file be retained
RETAIN_MERGE_KEY_FIELD = False
# Merge fields to retain, leave empty for all fields
MERGE_RETAIN_FIELDS = []
# Should data rows that have not been merged be output
OUTPUT_UNMERGED_DATA = False

userData = {}
dataFileName = sys.argv[1]
dataFile = open(dataFileName, 'r', encoding='utf-8')
dataCSV = csv.DictReader(dataFile, quotechar=QUOTE_CHAR)
dataFieldNames = dataCSV.fieldnames[:]
if DATA_KEY_FIELD not in dataFieldNames:
  sys.stderr.write(f'Data key field {DATA_KEY_FIELD} is not in {dataFileName} headers: {",".join(dataFieldNames)}\n')
  sys.exit(1)
for row in dataCSV:
  if LOWERCASE_KEY_FIELDS:
    row[DATA_KEY_FIELD] = row[DATA_KEY_FIELD].lower()
  userData[row[DATA_KEY_FIELD]] = row
dataFile.close()

mergeFileName = sys.argv[2]
mergeFile = open(mergeFileName, 'r', encoding='utf-8')
mergeCSV = csv.DictReader(mergeFile, quotechar=QUOTE_CHAR)
mergeFieldNames = mergeCSV.fieldnames[:]
if MERGE_KEY_FIELD not in mergeFieldNames:
  sys.stderr.write(f'Merge key field {MERGE_KEY_FIELD} is not in {mergeFileName} headers: {",".join(mergeFieldNames)}\n')
  sys.exit(1)

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
      sys.stderr.write(f'Merge retain field {fieldName} is not in {mergeFileName} headers: {",".join(mergeFieldNames)}\n')
  if errors:
    sys.exit(1)

if not RETAIN_MERGE_KEY_FIELD and MERGE_KEY_FIELD in mergeRetainFields:
  mergeRetainFields.remove(MERGE_KEY_FIELD)

outputFieldNames = dataFieldNames[:]
mergeFieldNameMap = {}
for fieldName in mergeRetainFields:
  if fieldName not in dataFieldNames:
    mappedFieldName = fieldName
  else:
    mappedFieldName = f'{fieldName}.merge'
  mergeFieldNameMap[fieldName] = mappedFieldName
  outputFieldNames.append(mappedFieldName)

outputFileName = sys.argv[3]
outputFile = open(outputFileName, 'w', encoding='utf-8', newline='')
outputCSV = csv.DictWriter(outputFile, outputFieldNames, lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

outputData = {}
errors = False
for row in mergeCSV:
  if LOWERCASE_KEY_FIELDS:
    row[MERGE_KEY_FIELD] = row[MERGE_KEY_FIELD].lower()
  k = row[MERGE_KEY_FIELD]
  if k in userData:
    orow = userData.pop(k)
    for fieldName in mergeFieldNameMap:
      orow[mergeFieldNameMap[fieldName]] = row[fieldName]
    outputData[k] = orow
  else:
    errors = 1
    sys.stderr.write(f'Merge key field {row[MERGE_KEY_FIELD]} in {mergeFileName} does not occur in {dataFileName}\n')
if OUTPUT_UNMERGED_DATA:
  outputData.update(userData)
for _, v in sorted(iter(outputData.items())):
  outputCSV.writerow(v)

mergeFile.close()
outputFile.close()
sys.exit(errors)
