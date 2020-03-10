#!/usr/bin/env python3
"""
# Purpose: Create a CSV file showing users that don't belong to any groups
# Note: This script can use Basic or Advanced GAM:
#	https://github.com/jay0lee/GAM
#	https://github.com/taers232c/GAMADV-XTD3
# Usage:
# 1: Get list of users, group members
#  $ gam print users > Users.csv
#  $ gam print group-members > GroupMembers.csv
# 2: From that list of users, output a CSV file with header primaryEmail
#    that shows users that don't belong to any groups
#  $ python GetUsersNoGroups.py ./Users.csv ./GroupMembers.sav ./UsersNoGroups.csv
"""

import csv
import sys

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

Users = {}

inputFile = open(sys.argv[1], 'r', encoding='utf-8')
for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  Users[row['primaryEmail']] = 0
inputFile.close()

inputFile = open(sys.argv[2], 'r', encoding='utf-8')
for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  if row['email'] in Users:
    Users[row['email']] += 1
inputFile.close()

if (len(sys.argv) > 3) and (sys.argv[3] != '-'):
  outputFile = open(sys.argv[3], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['primaryEmail'], lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

for k, v in sorted(Users.items()):
  if not v:
    outputCSV.writerow({'primaryEmail': k})

if outputFile != sys.stdout:
  outputFile.close()
