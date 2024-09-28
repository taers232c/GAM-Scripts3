#!/usr/bin/env python3
"""
# Purpose: Make a CSV file showing guardians with student emails
# Note: This script can use GAM7 or Advanced GAM:
#       https://github.com/GAM-team/GAM                                                                                                                               
#	https://github.com/taers232c/GAMADV-XTD3
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Get guardians
#  $ gam print guardians > ./Guardians.csv
# 2: Get student emails,
#  Use one of the following to select a collection of users
# <UserTypeEntity> ::=
#        (all users)|
#        (users <UserList>)|
#        (group|group_ns <GroupItem>)|
#        (groups|groups_ns <GroupList>)|
#        (ou|ou_ns <OrgUnitItem>)|
#        (ou_and_children|ou_and_children_ns <OrgUnitItem>)|
#        (ous|ous_ns <OrgUnitList>)|
#        (ous_and_children|ous_and_children_ns <OrgUnitList>)|
#        (courseparticipants <CourseIDList>)|
#        (students <CourseIDList>)|
#        (teachers <CourseIDList>)|
#        (file <FileName> [charset <Charset>] [delimiter <Character>])|
#        (csvfile <FileName>(:<FieldName>)+ [charset <Charset>] [columndelimiter <Character>] [quotechar <Character>]
#                [fields <FieldNameList>] (matchfield <FieldName> <RegularExpression>)* [delimiter <Character>])
#  $ gam <UserTypeEntity> print users fields primaryemail,id > ./Students.csv
# 3: Output an updated version of Guardians.csv with student emails obtained from Students.csv
#  $ python3 GetGuardianStudentEmails.py ./Students.csv ./Guardians.csv ./UpdatedGuardians.csv
"""

import csv
import sys

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

studentEmails = {}

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin
for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  studentEmails[row['id']] = row['primaryEmail']
if inputFile != sys.stdin:
  inputFile.close()

if len(sys.argv) > 2:
  inputFile = open(sys.argv[2], 'r', encoding='utf-8')
else:
  sys.stderr.write('Error: Guardians file missing')
  sys.exit(1)
inputCSV = csv.DictReader(inputFile, quotechar=QUOTE_CHAR)

if (len(sys.argv) > 3) and (sys.argv[3] != '-'):
  outputFile = open(sys.argv[3], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, inputCSV.fieldnames, lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

for row in inputCSV:
  row['studentEmail'] = studentEmails.get(row['studentId'], row['studentEmail'])
  outputCSV.writerow(row)

inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
