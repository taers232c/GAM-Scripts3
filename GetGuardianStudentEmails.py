#!/usr/bin/env python3
"""
# Purpose: Make a CSV file showing guardians with student emails
# Note: This script can use basic GAM: https://github.com/jay0lee/GAM or advanced GAM: https://github.com/taers232c/GAMADV-X
# Usage:
# 1: Get guardians
#  $ gam print guardians > ./Guardians.csv
# 2: Get student emails, 
#  Basic GAM: gam print users fields primaryemail,id > Students.csv
#  Advanced GAM: use one of the following to select a collection of users
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
#  $ python GetGuardianStudentEmails.py ./Students.csv ./Guardians.csv ./UpdatedGuardians.csv
"""

import csv
import sys

studentEmails = {}

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin
for row in csv.DictReader(inputFile):
  studentEmails[row['id']] = row['primaryEmail']
if inputFile != sys.stdin:
  inputFile.close()

if len(sys.argv) > 2:
  inputFile = open(sys.argv[2], 'r', encoding='utf-8')
else:
  sys.stderr.write('Error: Guardians file missing')
  sys.exit(1)
inputCSV = csv.DictReader(inputFile)

if (len(sys.argv) > 3) and (sys.argv[3] != '-'):
  outputFile = open(sys.argv[3], 'w')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, inputCSV.fieldnames, lineterminator='\n')
outputCSV.writeheader()

for row in inputCSV:
  row['studentEmail'] = studentEmails.get(row['studentId'], row['studentEmail'])
  outputCSV.writerow(row)

inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
