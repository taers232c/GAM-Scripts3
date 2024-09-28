#!/usr/bin/env python3
"""
# Purpose: Make a CSV file showing groups with no members
# Note: This script can use GAM7 or Advanced GAM:
#       https://github.com/GAM-team/GAM                                                                                                                               
#	https://github.com/taers232c/GAMADV-XTD3
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Get group member counts
#  $ gam redirect csv ./GroupCounts.csv print groups memberscount managerscount ownerscount
# 2: From that list of groups, output a CSV file with headers "group" for those groups with no members
#  $ python3 GetEmptyGroups.py ./GroupCounts.csv ./EmptyGroups.csv
"""

import csv
import sys

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['group'], lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin

for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  total = int(row.get('MembersCount', '0'))+int(row.get('ManagersCount', '0'))+int(row.get('OwnersCount', '0'))
  if total == 0:
    outputCSV.writerow({'group': row.get('email', row.get('Email', 'Unknown'))})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
