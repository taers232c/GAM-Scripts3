#!/usr/bin/env python3
"""
# Purpose: For a list of group members and a list of users, produce a CSV file that lists the users that are not group members
# Note: This script can use Basic or Advanced GAM:
#	https://github.com/jay0lee/GAM
#	https://github.com/taers232c/GAMADV-XTD3
# Usage:
# 1: Get group members
#  $ gam group <GroupName> print > Members.csv
# 2: Get users; replace <UserTypeEntity> as desired, e.g. ou /Teachers
#  $ gam <UserTypeEntity> print > Users.csv
# 3: Make a CSV file NonMembers.csv that lists the users that are not group members
#  $ python3 CheckMembership.py Members.csv Users.csv NonMembers.csv
"""

import csv
import sys

# Default is that Members.csv does not have a header row; the following sets a field name
MembersEmailField = 'primaryEmail'
MembersFieldNames = [MembersEmailField]
# If Members.csv does have a header row, edit the following line and remove the # from both lines
#MembersEmailField = 'primaryEmail'
#MembersFieldNames = None

# Default is that Users.csv does not have a header row; the following sets a field name
UsersEmailField = 'primaryEmail'
UsersFieldNames = [UsersEmailField]
# If Users.csv does have a header row, edit the following line and remove the # from both lines
#UsersEmailField = 'primaryEmail'
#UsersFieldNames = None

# Edit the following row if you want a different header for NonMembers.csv
NonMembersEmailField = 'primaryEmail'
NonMembersFieldNames = [NonMembersEmailField]

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

MembersSet = set()
inputFile = open(sys.argv[1], 'r', encoding='utf-8')
inputCSV = csv.DictReader(inputFile, fieldnames=MembersFieldNames, quotechar=QUOTE_CHAR)
for row in inputCSV:
  MembersSet.add(row[MembersEmailField])
inputFile.close()

inputFile = open(sys.argv[2], 'r', encoding='utf-8')
inputCSV = csv.DictReader(inputFile, fieldnames=UsersFieldNames, quotechar=QUOTE_CHAR)

if (len(sys.argv) > 3) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[3], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, NonMembersFieldNames, lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

for row in inputCSV:
  if row[UsersEmailField] not in MembersSet:
    outputCSV.writerow({NonMembersEmailField: row[UsersEmailField]})

inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
