#!/usr/bin/env python3
"""
Purpose: Process a CSV file to combine data fields for unique key fields
Customize: Change QUOTE_CHAR, DATA_DELIMITER, LINE_TERMINATOR as required/desired
Define: KEYFIELD, DATAFIELD, SAVEFIELDS, MATCHFIELDS, SKIPFIELDS
Python: Use python or python3 below as appropriate to your system; verify that you have version 3
 $ python -V   or   python3 -V
 Python 3.x.y
Usage:
 $ python3 CSVKMD.py ./Input.csv ./Output.csv
Example:
You have a CSV file CourseStudent.csv with three columns: id,name,student
The columns are: course ID, course Name, student email address
id,name,student
57121690282,science,testuser1@domain.com
57121690282,science,testuser2@domain.com
57121690282,science,testuser3@domain.com
56941282690,english,testuser4@domain.com
56941282690,english,testuser5@domain.com
56941282690,english,testuser6@domain.com
47491913641,math,testuser7@domain.com
47491913641,math,testuser8@domain.com
47491913641,math,testuser9@domain.com

Process all courses
KEYFIELD = 'id'
DATAFIELD = 'student'
SAVEFIELDS = ['name']
MATCHFIELDS = {}
SKIPFIELDS = {}

$ python3 CSVKMD.py CourseStudent.csv CourseStudentCombined.csv
$ more CourseStudentCombined.csv
id,name,student
47491913641,math,testuser9@domain.com testuser7@domain.com testuser8@domain.com
56941282690,english,testuser5@domain.com testuser6@domain.com testuser4@domain.com
57121690282,science,testuser2@domain.com testuser1@domain.com testuser3@domain.com
$ gam csv CourseStudentCombined.csv gam courses "~id" add students users "~student"

Process only english course
KEYFIELD = 'id'
DATAFIELD = 'student'
SAVEFIELDS = ['name']
MATCHFIELDS = {'name': re.compile(r'english')}
SKIPFIELDS = {}

$ python3 CSVKMD.py CourseStudent.csv CourseStudentCombined.csv
$ more CourseStudentCombined.csv
id,name,student
56941282690,english,testuser5@domain.com testuser6@domain.com testuser4@domain.com
$ gam csv CourseStudentCombined.csv gam courses "~id" add students users "~student"

Process all courses except english
KEYFIELD = 'id'
DATAFIELD = 'student'
SAVEFIELDS = ['name']
MATCHFIELDS = {}
SKIPFIELDS = {'name': re.compile(r'english')}

$ python3 CSVKMD.py CourseStudent.csv CourseStudentCombined.csv
$ more CourseStudentCombined.csv
id,name,student
47491913641,math,testuser8@domain.com testuser7@domain.com testuser9@domain.com
57121690282,science,testuser1@domain.com testuser2@domain.com testuser3@domain.com
$ gam csv CourseStudentCombined.csv gam courses "~id" add students users "~student"
"""

import csv
import re
import sys

QUOTE_CHAR = '"' # Adjust as needed to properly read CSV files
DATA_DELIMITER = ' '# Delimiter between data field items
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

ignore = re.compile(r'') # Keep pylint happy

# Key field name
# e.g., KEYFIELD = 'id'
KEYFIELD = ''
# Data field name
# e.g., DATAFIELD = 'student'
DATAFIELD = ''
# List of additional field names to include in output
# e.g., SAVEFIELDS = ['name']
SAVEFIELDS = []
# A dictionary of fields and associated Python Regular Expressions. Rows where all fields match will be processed
# e.g., MATCHFIELDS = {'name': re.compile(r'english')}
MATCHFIELDS = {}
# A dictionary of fields and associated Python Regular Expressions. Rows where with all fields don't match will be processed
# SKIPFIELDS = {'name': re.compile(r'english')}
SKIPFIELDS = {}


def fieldError(category, fieldName):
  sys.stderr.write(f'Error: {category}field "{fieldName}" not in file {sys.argv[1]} field names: {",".join(inputFieldNames)}\n')

def checkMatchSkipFields(row, matchFields, skipFields):
  for matchField, matchPattern in iter(matchFields.items()):
    if (matchField not in row) or not matchPattern.search(row[matchField]):
      return False
  for skipField, matchPattern in iter(skipFields.items()):
    if (skipField in row) and matchPattern.search(row[skipField]):
      return False
  return True

data = {}

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin
inputCSV = csv.DictReader(inputFile, quotechar=QUOTE_CHAR)
inputFieldNames = inputCSV.fieldnames
fieldErrors = 0
if KEYFIELD not in inputFieldNames:
  fieldError('key', KEYFIELD)
  fieldErrors += 1
if DATAFIELD not in inputFieldNames:
  fieldError('data', DATAFIELD)
  fieldErrors += 1
for field in SAVEFIELDS:
  if field not in inputFieldNames:
    fieldError('save', field)
    fieldErrors += 1
for field in MATCHFIELDS:
  if field not in inputFieldNames:
    fieldError('match', field)
    fieldErrors += 1
for field in SKIPFIELDS:
  if field not in inputFieldNames:
    fieldError('skip', field)
    fieldErrors += 1
if fieldErrors:
  sys.exit(1)
outputFieldNames = []
for field in inputFieldNames:
  if field == KEYFIELD or field == DATAFIELD or field in SAVEFIELDS:
    outputFieldNames.append(field)
for irow in inputCSV:
  keyfield = irow[KEYFIELD]
  datafield = irow[DATAFIELD]
  if keyfield and datafield and checkMatchSkipFields(irow, MATCHFIELDS, SKIPFIELDS):
    data.setdefault(keyfield, {DATAFIELD: set()})
    data[keyfield][DATAFIELD].add(datafield)
    for field in SAVEFIELDS:
      data[keyfield][field] = irow[field]
if inputFile != sys.stdin:
  inputFile.close()

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, outputFieldNames, lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

for kp, kv in sorted(data.items()):
  orow = {KEYFIELD: kp, DATAFIELD: DATA_DELIMITER.join(kv[DATAFIELD])}
  for field in SAVEFIELDS:
    orow[field] = kv[field]
  outputCSV.writerow(orow)

if outputFile != sys.stdout:
  outputFile.close()
