#!/usr/bin/env python3
"""
# Purpose: Convert a CSV file showing group members to one showing groups and their parents for each user
# Note: This script can use GAM7 or Advanced GAM:
#       https://github.com/GAM-team/GAM                                                                                                                               
#	https://github.com/taers232c/GAMADV-XTD3
# Customize: Set DELIMITER to the single character that will separate parent groups
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Get group members; omit field role if you're not interested the user's role
#  $ gam redirect csv ./GroupUsers.csv print group-members fields email,type,role
# 2: From that list of group members, output a CSV file with headers primaryEmail,Group,Role,ParentsCount,Parents that shows the groups and their parents for each user
#  $ python3 ConvertGroupUsersToUserGroupParents.py ./GroupUsers.csv ./UserGroupParents.csv
"""

import csv
import sys

DELIMITER = ' '
QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

def getGroupParents(groupEmail):
  groupParents[groupEmail] = {'parents': []}
  for parentGroup in GroupGroups[groupEmail]:
    groupParents[groupEmail]['parents'].append(parentGroup)
    if parentGroup not in groupParents:
      getGroupParents(parentGroup)

def printGroupParents(groupEmail, urow):
  if groupParents[groupEmail]['parents']:
    for parentEmail in groupParents[groupEmail]['parents']:
      urow['parents'].append(parentEmail)
      printGroupParents(parentEmail, urow)
      del urow['parents'][-1]
  else:
    csvRow = {'primaryEmail': urow['primaryEmail'], 'Group': urow['Group'],
              'ParentsCount': len(urow['parents']), 'Parents': DELIMITER.join(urow['parents'])}
    if includeRole:
      csvRow['Role'] = urow['Role']
    outputCSV.writerow(csvRow)

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin
inputCSV = csv.DictReader(inputFile, quotechar=QUOTE_CHAR)

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputFieldNames = ['primaryEmail', 'Group', 'ParentsCount', 'Parents']
if 'role' in inputCSV.fieldnames:
  outputFieldNames.insert(2, 'Role')
  includeRole = True
else:
  includeRole = False
outputCSV = csv.DictWriter(outputFile, outputFieldNames, lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

groupParents = {}
GroupGroups = {}
UserGroups = {}
for row in inputCSV:
  if row['type'] == 'USER':
    GroupGroups.setdefault(row['group'], [])
    email = row['email'].lower()
    UserGroups.setdefault(email, {'role': None, 'groups': []})
    UserGroups[email]['groups'].append(row['group'].lower())
    if includeRole:
      UserGroups[email]['role'] = row['role']
  elif row['type'] == 'GROUP':
    GroupGroups.setdefault(row['group'], [])
    email = row['email'].lower()
    GroupGroups.setdefault(email, [])
    GroupGroups[email].append(row['group'].lower())

for group in groupParents:
  groupParents[group].sort()
for user, info in sorted(iter(UserGroups.items())):
  for group in sorted(info['groups']):
    if group not in groupParents:
      getGroupParents(group)
    printGroupParents(group, {'primaryEmail': user, 'Group': group, 'Role': info['role'], 'parents': []})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
