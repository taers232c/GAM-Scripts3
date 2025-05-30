#!/usr/bin/env python3
"""
# Purpose: Show the number of Users/CrOS devices in each Org Unit
# Customize: Set SHOW_SUSPENDED, SHOW_SUSPENSION_REASON, SHOW_STATUS and SHOW_TOTALS
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Get OrgUnits
#  $ gam redirect csv ./OrgUnits.csv print ous
# 2: Get Users; omit suspended if you don't want suspension info
#  $ gam redirect csv ./Users.csv print users ou suspended
# 3: Get CrOS devices; omit status if you don't want status info
#  $ gam redirect csv ./CrOS.csv print cros ou status
# 4: From those lists of Users and Org Units, output a CSV file with user counts for each Org Unit
#  $ python3 GetOrgUnitUserCrOSCounts.py ./OrgUnits.csv ./Users.csv ./CrOS.csv ./OrgUnitUserCounts.csv
"""

import csv
import sys

SHOW_SUSPENDED = True # False if you don't want user suspension info
SHOW_SUSPENSION_REASON = True # False if you don't want suspensionReason info
SHOW_STATUS = True # False if you don't want device status information
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
  orgUnits[row['orgUnitPath']] = {'total' : 0, 'users' : 0, 'active': 0, 'suspended': 0, 'suspensionReason': {}, 'devices': 0, 'statusValues': {}}
inputFile.close()

fieldnames = ['orgUnitPath', 'total']

userInputFile = open(sys.argv[2], 'r', encoding='utf-8')
userInputCSV = csv.DictReader(userInputFile, quotechar=QUOTE_CHAR)
inputFieldNames = userInputCSV.fieldnames
if 'orgUnitPath' not in inputFieldNames:
  sys.stderr.write(f'Error: no header orgUnitPath in Users file {sys.argv[2]} field names: {",".join(inputFieldNames)}\n')
  sys.exit(1)
userFieldnames = ['users']
checkSuspended = SHOW_SUSPENDED and 'suspended' in inputFieldNames
if checkSuspended:
  userFieldnames.extend(['active', 'suspended'])
checkSuspensionReason = SHOW_SUSPENSION_REASON and 'suspensionReason' in inputFieldNames
suspensionReasons = set()

crosInputFile = open(sys.argv[3], 'r', encoding='utf-8')
crosInputCSV = csv.DictReader(crosInputFile, quotechar=QUOTE_CHAR)
inputFieldNames = crosInputCSV.fieldnames
if 'orgUnitPath' not in inputFieldNames:
  sys.stderr.write(f'Error: no header orgUnitPath in CrOS file {sys.argv[3]} field names: {",".join(inputFieldNames)}\nf')
  sys.exit(1)
crosFieldnames = ['devices']
checkStatus = SHOW_STATUS and 'status' in inputFieldNames
statusValues = set()

if (len(sys.argv) > 4) and (sys.argv[4] != '-'):
  outputFile = open(sys.argv[4], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout

totals = {'total' : 0, 'users' : 0, 'active': 0, 'suspended': 0, 'suspensionReason': {}, 'devices': 0, 'statusValues': {}}

for row in userInputCSV:
  orgUnitPath = row['orgUnitPath']
  if orgUnitPath not in orgUnits:
    orgUnits[orgUnitPath] = {'total' : 0, 'users' : 0, 'active': 0, 'suspended': 0, 'suspensionReason': {}, 'devices': 0, 'statusValues': {}}
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
    userFieldnames.append(f'suspensionReason.{suspensionReason}')
    totals['suspensionReason'][suspensionReason] = 0
fieldnames.extend(userFieldnames)

for row in crosInputCSV:
  orgUnitPath = row['orgUnitPath']
  if orgUnitPath not in orgUnits:
    orgUnits[orgUnitPath] = {'total' : 0, 'users' : 0, 'active': 0, 'suspended': 0, 'suspensionReason': {}, 'devices': 0, 'statusValues': {}}
  orgUnits[orgUnitPath]['devices'] += 1
  if checkStatus:
    statusValue = row['status']
    if statusValue not in statusValues:
      statusValues.add(statusValue)
    orgUnits[orgUnitPath]['statusValues'].setdefault(statusValue, 0)
    orgUnits[orgUnitPath]['statusValues'][statusValue] += 1
if checkStatus:
  for statusValue in sorted(statusValues):
    crosFieldnames.append(f'status.{statusValue}')
    totals['statusValues'][statusValue] = 0
fieldnames.extend(crosFieldnames)

outputCSV = csv.DictWriter(outputFile, fieldnames, lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()
for orgUnit, counts in sorted(iter(orgUnits.items())):
  countsUsers = counts['users']
  totals['users'] += countsUsers
  countsDevices = counts['devices']
  totals['devices'] += countsDevices
  countsTotal = countsUsers+countsDevices
  totals['total'] += countsTotal
  row = {'orgUnitPath': orgUnit, 'total': countsTotal, 'users': countsUsers, 'devices': countsDevices}
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
  if checkStatus:
    for statusValue in statusValues:
      count = counts['statusValues'].get(statusValue, 0)
      row[f'status.{statusValue}'] = count
      totals['statusValues'][statusValue] += count
  outputCSV.writerow(row)
if SHOW_TOTALS:
  row = {'orgUnitPath': 'Totals', 'total': totals['total'], 'users': totals['users'], 'devices': totals['devices']}
  if checkSuspended:
    row['active'] = totals['active']
    row['suspended'] = totals['suspended']
    if checkSuspensionReason:
      for suspensionReason, count in iter(totals['suspensionReason'].items()):
        row[f'suspensionReason.{suspensionReason}'] = count
  if checkStatus:
    for statusValue, count in iter(totals['statusValues'].items()):
      row[f'status.{statusValue}'] = count
  outputCSV.writerow(row)

userInputFile.close()
crosInputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
