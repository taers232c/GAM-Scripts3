#!/usr/bin/env python3
"""
# Purpose: For a CSV file, look up user email addresses and add Org Unit information
# Customize: DATA_EMAIL_HEADER, DATA_ORGUNIT_HEADER, USER_EMAIL_HEADER, USER_ORGUNIT_HEADER, UNKNOWN_ORGUNIT
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Generate a list of users and their Org Units
#  $ gam redirect csv ./Users.csv print users fields primaryemail,ou
# 2: Generate some data
#  $ gam redirect csv ./Data.csv ...
# 3: From those two files, generate an output CSV file with the same headers as Data.csv plus a header for the users's Org Unit
#  $ python3 AddOrgUnit.py ./Data.csv ./Users.csv ./DataWithOrgUnit.csv
"""

import csv
import sys

# You have to indicate the header in Data.csv that contains the user email addresses
# and the desired Org Unit header in DataWithOrgUnit.csv
# Common values are:
# report login - actor.email, actor.orgUnitPath
# report user - email, orgUnitPath
DATA_EMAIL_HEADER = 'email'
DATA_ORGUNIT_HEADER = 'orgUnitPath'

# Email header in Users.csv CSV file
USER_EMAIL_HEADER = 'primaryEmail'

# OrgUnit header in Users.csv CSV file
USER_ORGUNIT_HEADER = 'orgUnitPath'

# Unkown Org Unit value
UNKNOWN_ORGUNIT = 'Unknown'

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

userOrgUnits = {}
inputFile = open(sys.argv[2], 'r', encoding='utf-8')
for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  userOrgUnits[row[USER_EMAIL_HEADER]] = row[USER_ORGUNIT_HEADER]
inputFile.close()

if sys.argv[1] != '-':
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin
inputCSV = csv.DictReader(inputFile, quotechar=QUOTE_CHAR)

outputFieldNames = inputCSV.fieldnames[:]
if outputFieldNames is None:
  sys.stderr.write(f'Error: no headers in Data file {sys.argv[1]}\n')
  sys.exit(2)
if DATA_EMAIL_HEADER not in outputFieldNames:
  sys.stderr.write(f'Error: field {DATA_EMAIL_HEADER} is not in Data file {sys.argv[1]} field names: {",".join(outputFieldNames)}\n')
  sys.exit(3)
index = outputFieldNames.index(DATA_EMAIL_HEADER)
outputFieldNames.insert(index+1, DATA_ORGUNIT_HEADER)
if (len(sys.argv) > 3) and (sys.argv[3] != '-'):
  outputFile = open(sys.argv[3], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, outputFieldNames, lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

for row in inputCSV:
  row[DATA_ORGUNIT_HEADER] = userOrgUnits.get(row[DATA_EMAIL_HEADER], UNKNOWN_ORGUNIT)
  outputCSV.writerow(row)

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
