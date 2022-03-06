#!/usr/bin/env python3
"""
# Purpose: Create a CSV file showing users that belong to a number of groups beyond a threshold
# threshold not specified - output all users
# threshold 0 - output all users belonging to at least 1 group
# threshold N - output all users belonging to more than N groups
# Note: This script can use Basic or Advanced GAM:
#	https://github.com/GAM-team/GAM
#	https://github.com/taers232c/GAMADV-XTD3
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Get list of users, group members
#  $ gam print users > Users.csv
#  $ gam print group-members > GroupMembers.csv
# 2: From that list of users, output a CSV file with headers with the same headers as Users.csv plus GroupsCount
#    that shows the number of groups
#  $ python3 GetUsersGroupCounts.py ./Users.csv ./GroupMembers.csv ./UsersGroupsCounts.csv <threshold>
"""

import csv
import sys

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

Users = {}

inputFile = open(sys.argv[1], 'r', encoding='utf-8')
inputCSV = csv.DictReader(inputFile, quotechar=QUOTE_CHAR)
fieldnames = inputCSV.fieldnames[:]
fieldnames.insert(1, 'GroupsCount')
for row in inputCSV:
  row['GroupsCount'] = 0
  Users[row['primaryEmail']] = row
inputFile.close()

inputFile = open(sys.argv[2], 'r', encoding='utf-8')
for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  if row['email'] in Users:
    Users[row['email']]['GroupsCount'] += 1
inputFile.close()

if (len(sys.argv) > 3) and (sys.argv[3] != '-'):
  outputFile = open(sys.argv[3], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, fieldnames, lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

if len(sys.argv) > 4:
  threshold = int(sys.argv[4])
else:
  threshold = -1

for _, v in sorted(Users.items()):
  if v['GroupsCount'] > threshold:
    outputCSV.writerow(v)

if outputFile != sys.stdout:
  outputFile.close()
