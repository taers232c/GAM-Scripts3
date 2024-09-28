#!/usr/bin/env python3
"""
# Purpose: Produce a CSV file showing groups with with a count of their member types
# Note: This script can use GAM7 or Advanced GAM:
#       https://github.com/GAM-team/GAM                                                                                                                               
#	https://github.com/taers232c/GAMADV-XTD3
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Get group members
#  $ gam redirect csv ./GroupMembers.csv print group-members fields type
# 2: From that list of group members, output a CSV file with headers group,customercount,groupcount,usercount
#  $ python3 GetGroupTypeCounts.py ./GroupMembers.csv ./GroupTypeCounts.csv
"""

import csv
import sys

DELIMITER = ' ' # Character to separate domains in output CSV
QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['group', 'CUSTOMER', 'GROUP', 'USER', 'UNKNOWN'], lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin
inputCSV = csv.DictReader(inputFile, quotechar=QUOTE_CHAR)

Groups = {}
for row in inputCSV:
  mtype = row.get('type', 'UNKNOWN')
  group = row['group']
  Groups.setdefault(group, {'CUSTOMER': 0, 'GROUP': 0, 'USER': 0, 'UNKNOWN': 0})
  if mtype in {'CUSTOMER', 'GROUP', 'USER'}:
    Groups[group][mtype] += 1
  else:
    Groups[group]['UNKNOWN'] += 1

for group, counts in sorted(iter(Groups.items())):
  outputCSV.writerow({'group': group,
                      'CUSTOMER': counts['CUSTOMER'],
                      'GROUP': counts['GROUP'],
                      'USER': counts['USER'],
                      'UNKNOWN': counts['UNKNOWN']})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
