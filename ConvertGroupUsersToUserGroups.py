#!/usr/bin/env python3
"""
# Purpose: Convert a CSV file showing group members to one showing groups for each user
# Note: This script can use Basic or Advanced GAM:
#	https://github.com/jay0lee/GAM
#	https://github.com/taers232c/GAMADV-XTD3
# Customize: Set DELIMITER to the single character that will separate groups
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Get group members
#  $ Basic: gam print group-members fields email,type > GroupUsers.csv
#  $ Advanced: gam redirect csv ./GroupUsers.csv print group-members fields email,type
# 2: From that list of group members, output a CSV file with headers primaryEmail,GroupsCount,Groups that shows the groups for each user
#  $ python3 ConvertGroupUsersToUserGroups.py ./GroupUsers.csv ./UserGroups.csv
"""

import csv
import sys

DELIMITER = ' '
QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['primaryEmail', 'GroupsCount', 'Groups'], lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin

UserGroups = {}
for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  if row['type'] == 'USER':
    UserGroups.setdefault(row['email'], [])
    UserGroups[row['email']].append(row['group'])

for user, groups in sorted(iter(UserGroups.items())):
  outputCSV.writerow({'primaryEmail': user,
                      'GroupsCount': len(groups),
                      'Groups': DELIMITER.join(groups)})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
