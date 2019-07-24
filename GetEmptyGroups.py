#!/usr/bin/env python3
"""
# Purpose: Make a CSV file showing groups with no members
# Note: This script can use Basic or Advanced GAM:
#	https://github.com/jay0lee/GAM
#	https://github.com/taers232c/GAMADV-X, https://github.com/taers232c/GAMADV-XTD, https://github.com/taers232c/GAMADV-XTD3
# Usage:
# 1: Get group member counts
#  $ gam print groups memberscount managerscount ownerscount > ./GroupCounts.csv
# 2: From that list of groups, output a CSV file with headers "group" for those groups with no members
#  $ python GetEmptyGroups.py ./GroupCounts.csv ./EmptyGroups.csv
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
