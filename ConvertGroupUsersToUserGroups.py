#!/usr/bin/env python3
"""
# Purpose: Convert a CSV file showing group members to one showing groups for each user
# Note: This script can use Basic or Advanced GAM:
#	https://github.com/GAM-team/GAM
#	https://github.com/taers232c/GAMADV-XTD3
# Customize: Set DELIMITER to the single character that will separate groups
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Get group members; omit field role if you're not interested the user's role
#  $ Basic: gam print group-members fields email,type,role > GroupUsers.csv
#  $ Advanced: gam redirect csv ./GroupUsers.csv print group-members fields email,type,role
# 2: From that list of group members, output a CSV file with headers primaryEmail,GroupsCount,Groups that shows the groups for each user
#  $ python3 ConvertGroupUsersToUserGroups.py ./GroupUsers.csv ./UserGroups.csv
"""

import csv
import sys

DELIMITER = ' '
QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin
inputCSV = csv.DictReader(inputFile, quotechar=QUOTE_CHAR)

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputFieldNames = ['primaryEmail', 'GroupsCount', 'Groups']
if 'role' in inputCSV.fieldnames:
  outputFieldNames.insert(1, 'Role')
  includeRole = True
else:
  includeRole = False
outputCSV = csv.DictWriter(outputFile, outputFieldNames, lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

UserGroups = {}
for row in inputCSV:
  if row['type'] == 'USER':
    email = row['email'].lower()
    UserGroups.setdefault(email, {'role': None, 'groups': []})
    if includeRole:
      UserGroups[email]['role'] = row['role']
    UserGroups[email]['groups'].append(row['group'].lower())

for user, info in sorted(iter(UserGroups.items())):
  csvRow = {'primaryEmail': user, 'GroupsCount': len(info['groups']), 'Groups': DELIMITER.join(sorted(info['groups']))}
  if includeRole:
    csvRow['Role'] = info['role']
  outputCSV.writerow(csvRow)

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
