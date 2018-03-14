#!/usr/bin/env python3
"""
# Purpose: Convert a CSV file showing group members to one showing groups for each user
# Note: This script can use Basic or Advanced GAM:
#	https://github.com/jay0lee/GAM
#	https://github.com/taers232c/GAMADV-X, https://github.com/taers232c/GAMADV-XTD, https://github.com/taers232c/GAMADV-XTD3
# Customize: Set DELIMITER to the single character that will separate groups
# Usage:
# 1: Get group members
#  $ Basic: gam print group-members fields email,type > GroupUsers.csv
#  $ Advanced: gam redirect csv ./GroupUsers.csv print group-members fields email,type
# 2: From that list of group members, output a CSV file with headers primaryEmail,Groups that shows the groups for each user
#  $ python ConvertGroupUsersToUserGroups.py ./GroupUsers.csv ./UserGroups.csv
"""

import csv
import sys

DELIMITER = ' '

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['primaryEmail', 'Groups'], lineterminator='\n')
outputCSV.writeheader()

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin

UserGroups = {}
for row in csv.DictReader(inputFile):
  if row['type'] == 'USER':
    UserGroups.setdefault(row['email'], [])
    UserGroups[row['email']].append(row['group'])

for user, groups in sorted(iter(UserGroups.items())):
  outputCSV.writerow({'primaryEmail': user,
                      'Groups': DELIMITER.join(groups)})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
