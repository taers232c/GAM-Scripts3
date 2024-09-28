#!/usr/bin/env python3
"""
# Purpose: Append user data to a CSV file
# Methodology:
# A user CSV file is read and each row is stored in a user data dictionary under the key row[USER_KEY_FIELD]
# A data CSV file is read and row[DATA_KEY_FIELD] is looked up in the user data dictionary
# If the user data row is found, the data row and user data row are combined and written to the output CSV file
# If the user data row is not found, an error message is generated and the data row is written to the output CSV file
# If a user CSV file column header matches a data CSV file column header, ".user" is appended to the
# user column header in the output CSV file
#
# Note: This script can use GAM7 or Advanced GAM:
#	https://github.com/GAM-team/GAM
#	https://github.com/taers232c/GAMADV-XTD3
# Customize: DATA_KEY_FIELD, USER_KEY_FIELD, RETAIN_USER_KEY_FIELD, USER_APPEND_FIELDS, WRITE_UNMATCHED_DATA_ROWS
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Generate the two data files, e.g., to add a user name to a password change edit log
#  $ gam redirect csv ./Data.csv report login user all start "2022-08-01" end "2022-09-01" event password_edit
#  $ gam redirect csv ./User.csv multiprocess csv Data.csv gam user "~actor.email" print fullname
# 2: Merge files
#  $ python3 AppendUserData.py ./Data.csv ./User.csv ./Output.csv
"""

import csv
import sys

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

# Key field in data file
DATA_KEY_FIELD = ''
# Key field in user file; common values are primaryEmail, Owner, User
USER_KEY_FIELD = 'primaryEmail'
# Should key field in user file be retained
RETAIN_USER_KEY_FIELD = False
# User append fields, leave empty for all fields
USER_APPEND_FIELDS = []
# Should unmatched data key rows be written to output
WRITE_UNMATCHED_DATA_ROWS = True

dataFileName = sys.argv[1]
dataFile = open(dataFileName, 'r', encoding='utf-8')
dataCSV = csv.DictReader(dataFile, quotechar=QUOTE_CHAR)
dataFieldNames = dataCSV.fieldnames[:]
if DATA_KEY_FIELD not in dataFieldNames:
  sys.stderr.write(f'Data key field {DATA_KEY_FIELD} is not in {dataFileName} headers: {",".join(dataFieldNames)}\n')
  sys.exit(1)

userData = {}
userFileName = sys.argv[2]
userFile = open(userFileName, 'r', encoding='utf-8')
userCSV = csv.DictReader(userFile, quotechar=QUOTE_CHAR)
userFieldNames = userCSV.fieldnames[:]
if USER_KEY_FIELD not in userFieldNames:
  sys.stderr.write(f'User key field {USER_KEY_FIELD} is not in {userFileName} headers: {",".join(userFieldNames)}\n')
  sys.exit(1)
for row in userCSV:
  userData[row[USER_KEY_FIELD]] = row
userFile.close()

errors = 0
if not USER_APPEND_FIELDS:
  userAppendFields = userFieldNames
else:
  userAppendFields = []
  for fieldName in USER_APPEND_FIELDS:
    if fieldName in userFieldNames:
      userAppendFields.append(fieldName)
    else:
      errors = 1
      sys.stderr.write(f'User append field {fieldName} is not in {userFileName} headers: {",".join(userFieldNames)}\n')
  if errors:
    sys.exit(1)

if not RETAIN_USER_KEY_FIELD and USER_KEY_FIELD in userAppendFields:
  userAppendFields.remove(USER_KEY_FIELD)

outputFieldNames = dataFieldNames[:]
userFieldNameMap = {}
for fieldName in userAppendFields:
  if fieldName not in dataFieldNames:
    mappedFieldName = fieldName
  else:
    mappedFieldName = f'{fieldName}.user'
  userFieldNameMap[fieldName] = mappedFieldName
  outputFieldNames.append(mappedFieldName)

outputFileName = sys.argv[3]
outputFile = open(outputFileName, 'w', encoding='utf-8', newline='')
outputCSV = csv.DictWriter(outputFile, outputFieldNames, lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

errors = 0
for row in dataCSV:
  k = row[DATA_KEY_FIELD]
  if k in userData:
    for fieldName in userFieldNameMap:
      row[userFieldNameMap[fieldName]] = userData[k][fieldName]
    outputCSV.writerow(row)
  else:
    errors = 1
    sys.stderr.write(f'Data key field {row[DATA_KEY_FIELD]} in {dataFileName} does not occur in {userFileName}\n')
    if WRITE_UNMATCHED_DATA_ROWS:
      outputCSV.writerow(row)

dataFile.close()
outputFile.close()
sys.exit(errors)
