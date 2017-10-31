#!/usr/bin/env python3
"""
# Purpose: Make a CSV file showing delegators for delegates
# Note: This script can use basic GAM: https://github.com/jay0lee/GAM or advanced GAM: https://github.com/taers232c/GAMADV-X
# Usage:
# 1: Get delegates
#  $ gam all users print delegates > ./AllDelegates.csv
# 2: From that list of delegates, output a CSV file with headers "Delegate,Delegate Email,Delegators
#  $ python ShowDelegators.py ./AllDelegates.csv ./AllDelegators.csv
"""

import csv
import sys

delegates = {}

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['Delegate', 'Delegate Email', 'Delegators'], lineterminator='\n')
outputCSV.writeheader()
if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r')
else:
  inputFile = sys.stdin

for row in csv.DictReader(inputFile):
  delegate = row['Delegate']
  delegates.setdefault(delegate, {'Delegate Email': row['Delegate Email'], 'Delegators': []})
  delegates[delegate]['Delegators'].append(row['Delegator'])

for delegate in sorted(delegates):
  outputCSV.writerow({'Delegate': delegate,
                      'Delegate Email': delegates[delegate]['Delegate Email'],
                      'Delegators': ' '.join(delegates[delegate]['Delegators'])})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
