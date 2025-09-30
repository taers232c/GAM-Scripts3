#!/usr/bin/env python3
"""
# Purpose: Create a CSV file showing users that don't belong to a specific group
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Get list of users, group members
#  $ gam redirect csv ./Users.csv print users
#  Replace group@domain.com with actual group address
#  $ gam redirect csv ./GroupMembers.csv print group-members group group@domain.com
# 2: From that list of users, output a CSV file with the same headers as Users.csv
#    that shows users that don't belong to the specific  group
#  $ python3 GetUsersNotInGroup.py ./Users.csv ./GroupMembers.csv ./UsersNotInGroup.csv
"""

import csv
import sys

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

UsersNotInGroup = {}

inputFile = open(sys.argv[1], 'r', encoding='utf-8')
inputCSV = csv.DictReader(inputFile, quotechar=QUOTE_CHAR)
fieldnames = inputCSV.fieldnames[:]
for row in inputCSV:
  UsersNotInGroup[row['primaryEmail']] = row
inputFile.close()

inputFile = open(sys.argv[2], 'r', encoding='utf-8')
for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  if row['email'] in UsersNotInGroup:
    del UsersNotInGroup[row['email']]
inputFile.close()

outputFile = open(sys.argv[3], 'w', encoding='utf-8', newline='')
outputCSV = csv.DictWriter(outputFile, fieldnames, lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

for _, v in sorted(UsersNotInGroup.items()):
  outputCSV.writerow(v)

outputFile.close()
