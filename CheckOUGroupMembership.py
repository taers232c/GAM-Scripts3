#!/usr/bin/env python3
"""
# Purpose: Reconcile OU and Group membership.
# Note: This script requires Advanced GAM:
#	https://github.com/taers232c/GAMADV-XTD3
# Customize: set OU_HEADER if OUMembers.csv has a header row
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Get OU members
#  $ gam redirect csv ./OUMembers.csv ou /Path/To/OU print users
# 2: Get Group members; you can select more that one group if desired
#  $ gam redirect csv ./GroupMembers.csv print group-members select group1@domain.com,group2@domain.com,... recursive noduplicates
# 3: From those two lists, output one CSV file showing the OU members that are not in the groups and
#    and another CSV file showing the group members that are not in the OU
#  $ python3 CheckOUGroupMembership.py ./OUMembers.csv ./GroupMembers.csv ./OUNotGroupMembers.csv ./GroupNotOU.csv
"""

import csv
import sys

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

OU_HEADER = ''

OUMembers = set()
inputFile = open(sys.argv[1], 'r', encoding='utf-8')
if OU_HEADER:
  for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
    OUMembers.add(row[OU_HEADER])
else:
  for row in csv.reader(inputFile, quotechar=QUOTE_CHAR):
    OUMembers.add(row[0])
inputFile.close()

GroupMembers = set()
inputFile = open(sys.argv[2], 'r', encoding='utf-8')
for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  GroupMembers.add(row['email'])
inputFile.close()

outputFile = open(sys.argv[3], 'w', encoding='utf-8', newline='')
outputCSV = csv.DictWriter(outputFile, ['primaryEmail'], lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()
for email in OUMembers-GroupMembers:
  outputCSV.writerow({'primaryEmail': email})
outputFile.close()

outputFile = open(sys.argv[4], 'w', encoding='utf-8', newline='')
outputCSV = csv.DictWriter(outputFile, ['primaryEmail'], lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()
for email in GroupMembers-OUMembers:
  outputCSV.writerow({'primaryEmail': email})
outputFile.close()
