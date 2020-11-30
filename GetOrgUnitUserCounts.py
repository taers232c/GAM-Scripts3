#!/usr/bin/env python3
"""
# Purpose: Show the number of Users in each Org Unit
# Note: This script can use Basic or Advanced GAM:
#	https://github.com/jay0lee/GAM
#	https://github.com/taers232c/GAMADV-XTD3
# Customize: Set SHOW_SUSPENDED, SHOW_SUSPENSION_REASON and SHOW_TOTALS
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Get OrgUnits
#  $ gam print ous > OrgUnits.csv
# 2: Get Users; omit suspended if you don't want suspension info
#  $ gam print users ou suspended > Users.csv
# 3: From those lists of Users and Org Units, output a CSV file with user counts for each Org Unit
#  $ python3 GetOrgUnitUserCounts.py ./OrgUnits.csv ./Users.csv ./OrgUnitUserCounts.csv
"""

import csv
import sys

SHOW_SUSPENDED = True # False if you don't want suspension info
SHOW_SUSPENSION_REASON = True # False if you don't want suspensionReason info
SHOW_TOTALS = True # False if you don't want totals

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

orgUnits = {}
inputFile = open(sys.argv[1], 'r', encoding='utf-8')
inputCSV = csv.DictReader(inputFile, quotechar=QUOTE_CHAR)
inputFieldNames = inputCSV.fieldnames
if 'orgUnitPath' not in inputFieldNames:
  sys.stderr.write(f'Error: no header orgUnitPath in Org Units file {sys.argv[1]} field names: {",".join(inputFieldNames)}\n')
  sys.exit(1)
for row in inputCSV:
  orgUnits[row['orgUnitPath']] = {'users' : 0, 'active': 0, 'suspended': 0, 'suspensionReason': {}}
inputFile.close()

if sys.argv[2] != '-':
  inputFile = open(sys.argv[2], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin
inputCSV = csv.DictReader(inputFile, quotechar=QUOTE_CHAR)
inputFieldNames = inputCSV.fieldnames
if 'orgUnitPath' not in inputFieldNames:
  sys.stderr.write(f'Error: no header orgUnitPath in Users file {sys.argv[2]} field names: {",".join(inputFieldNames)}\n')
  sys.exit(1)
fieldnames = ['orgUnitPath', 'users']
checkSuspended = SHOW_SUSPENDED and 'suspended' in inputFieldNames
if checkSuspended:
  fieldnames.extend(['active', 'suspended'])
checkSuspensionReason = SHOW_SUSPENSION_REASON and 'suspensionReason' in inputFieldNames
suspensionReasons = set()

if (len(sys.argv) > 3) and (sys.argv[3] != '-'):
  outputFile = open(sys.argv[3], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout

totals = {'users' : 0, 'active': 0, 'suspended': 0, 'suspensionReason': {}}

for row in inputCSV:
  orgUnitPath = row['orgUnitPath']
  if orgUnitPath not in orgUnits:
    orgUnits[orgUnitPath] = {'users' : 0, 'active': 0, 'suspended': 0, 'suspensionReason': {}}
  orgUnits[orgUnitPath]['users'] += 1
  if checkSuspended:
    if row['suspended'] != 'True':
      orgUnits[orgUnitPath]['active'] += 1
    else:
      orgUnits[orgUnitPath]['suspended'] += 1
      if checkSuspensionReason:
        suspensionReason = row['suspensionReason']
        if suspensionReason not in suspensionReasons:
          suspensionReasons.add(suspensionReason)
        orgUnits[orgUnitPath]['suspensionReason'].setdefault(suspensionReason, 0)
        orgUnits[orgUnitPath]['suspensionReason'][suspensionReason] += 1
if checkSuspensionReason:
  for suspensionReason in sorted(suspensionReasons):
    fieldnames.append(f'suspensionReason.{suspensionReason}')
    totals['suspensionReason'][suspensionReason] = 0

outputCSV = csv.DictWriter(outputFile, fieldnames, lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()
for orgUnit, counts in sorted(iter(orgUnits.items())):
  row = {'orgUnitPath': orgUnit, 'users': counts['users']}
  totals['users'] += counts['users']
  if checkSuspended:
    row['active'] = counts['active']
    totals['active'] += counts['active']
    row['suspended'] = counts['suspended']
    totals['suspended'] += counts['suspended']
    if checkSuspensionReason:
      for suspensionReason in suspensionReasons:
        count = counts['suspensionReason'].get(suspensionReason, 0)
        row[f'suspensionReason.{suspensionReason}'] = count
        totals['suspensionReason'][suspensionReason] += count
  outputCSV.writerow(row)
if SHOW_TOTALS:
  row = {'orgUnitPath': 'Totals', 'users': totals['users']}
  if checkSuspended:
    row['active'] = totals['active']
    row['suspended'] = totals['suspended']
    if checkSuspensionReason:
      for suspensionReason, count in iter(totals['suspensionReason'].items()):
        row[f'suspensionReason.{suspensionReason}'] = count
  outputCSV.writerow(row)

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
