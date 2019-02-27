#!/usr/bin/env python3
"""
# Purpose: Make a CSV file showing delegators for delegates
# Note: This script can use Basic or Advanced GAM:
#	https://github.com/jay0lee/GAM
#	https://github.com/taers232c/GAMADV-X, https://github.com/taers232c/GAMADV-XTD, https://github.com/taers232c/GAMADV-XTD3
# Usage:
# 1: Get delegates
#  $ Basic: gam all users print delegates > ./AllDelegates.csv
#  $ Advanced: gam all users print delegates shownames > ./AllDelegates.csv
# 2: From that list of delegates, output a CSV file with headers "Delegate,Delegate Email,Delegators
#  $ python ShowDelegators.py ./AllDelegates.csv ./AllDelegators.csv
"""

import csv
import sys

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

delegates = {}

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['Delegate', 'Delegate Email', 'Delegators'], lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin

for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  delegate = row['delegateAddress']
  delegates.setdefault(delegate, {'Delegate': row.get('delegateName', delegate), 'Delegators': []})
  delegates[delegate]['Delegators'].append(row['User'])

for delegate in sorted(delegates):
  outputCSV.writerow({'Delegate': delegates[delegate]['Delegate'],
                      'Delegate Email': delegate,
                      'Delegators': ' '.join(delegates[delegate]['Delegators'])})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
