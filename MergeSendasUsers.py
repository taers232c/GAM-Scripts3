#!/usr/bin/env python3
"""
# Purpose: Make a CSV file that merges sendas addresses with user data
# Note: This script can use Basic or Advanced GAM:
#	https://github.com/jay0lee/GAM
#	https://github.com/taers232c/GAMADV-XTD3
# Customize: Set INCLUDE_PRIMARY = True/False, OPTIONAL_MERGE_FIELDS
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Get Users
#  Basic GAM:
# $  gam print users fields primaryemail,... > ./Users.csv
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
#  $ gam <UserTypeEntity> print users fields primaryemail,... > ./Users.csv
# 2: Get Sendas addresses
#  $ gam <UserTypeEntity> print sendas > ./Sendas.csv
# 3: Output an updated version of Users.csv with one row for each address in Sendas.csv
#  $ python3 MergeSendasUsers.py ./Sendas.csv ./Users.csv ./UpdatedUsers.csv
"""

import csv
import sys

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

# Should primary email address be include?
INCLUDE_PRIMARY = True
# Select optional fields from Sendas.csv to merge with Users.csv
# Choose from: 'replyToAddress','isPrimary','isDefault','treatAsAlias','verificationStatus','signature'
OPTIONAL_MERGE_FIELDS = []

usersSendasAddresses = {}

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin
for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  usersSendasAddresses.setdefault(row['User'], [])
  if row['isPrimary'] == 'False' or INCLUDE_PRIMARY:
    usersSendasAddresses[row['User']].append(row)
if inputFile != sys.stdin:
  inputFile.close()

if len(sys.argv) > 2:
  inputFile = open(sys.argv[2], 'r', encoding='utf-8')
else:
  sys.stderr.write('Error: Users file missing')
  sys.exit(1)
inputCSV = csv.DictReader(inputFile, quotechar=QUOTE_CHAR)

if (len(sys.argv) > 3) and (sys.argv[3] != '-'):
  outputFile = open(sys.argv[3], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputFieldnames = inputCSV.fieldnames[:]
outputFieldnames.append('sendAsEmail')
outputFieldnames.extend(OPTIONAL_MERGE_FIELDS)
outputCSV = csv.DictWriter(outputFile, outputFieldnames, lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

for row in inputCSV:
  for sendAs in usersSendasAddresses.get(row['primaryEmail'], []):
    row['sendAsEmail'] = sendAs['sendAsEmail']
    for field in OPTIONAL_MERGE_FIELDS:
      row[field] = sendAs[field]
    outputCSV.writerow(row)

inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
