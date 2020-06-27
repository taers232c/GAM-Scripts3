#!/usr/bin/env python3
"""
# Purpose: Show the number of CrOS devices in each Org Unit
# Note: This script can use Basic or Advanced GAM:
#	https://github.com/jay0lee/GAM
#	https://github.com/taers232c/GAMADV-XTD3
# Customize: Set SHOW_STATUS,SHOW_TOTALS
# Usage:
# 1: Get OrgUnits
#  $ gam print ous > OrgUnits.csv
# 2: Get CrOS devices; omit status if you don't want status info
#  $ gam print cros ou status > CrOS.csv
# 3: From those lists of Org Units and CrOS devices, output a CSV file with CrOS device counts for each Org Unit
#  $ python GetOrgUnitCrOSCounts.py ./OrgUnits.csv ./CrOS.csv ./OrgUnitCrOSCounts.csv
"""

import csv
import sys

SHOW_STATUS = True # False if you don't want status information
SHOW_TOTALS = True # False if you don't want totals

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

orgUnits = {}
inputFile = open(sys.argv[1], 'r', encoding='utf-8')
inputCSV = csv.DictReader(inputFile, quotechar=QUOTE_CHAR)
inputFieldNames = inputCSV.fieldnames
if 'orgUnitPath' not in inputFieldNames:
  sys.stderr.write('Error: no header orgUnitPath in Org Units file {0} field names: {1}\n'.format(sys.argv[1], ','.join(inputFieldNames)))
  sys.exit(1)
for row in inputCSV:
  orgUnits[row['orgUnitPath']] = {'total' : 0, 'statusValues': {}}
inputFile.close()

if sys.argv[2] != '-':
  inputFile = open(sys.argv[2], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin
inputCSV = csv.DictReader(inputFile, quotechar=QUOTE_CHAR)
inputFieldNames = inputCSV.fieldnames
if 'orgUnitPath' not in inputFieldNames:
  sys.stderr.write('Error: no header orgUnitPath in CrOS file {0} field names: {1}\n'.format(sys.argv[2], ','.join(inputFieldNames)))
  sys.exit(1)
fieldnames = ['orgUnitPath', 'total']
checkStatus = SHOW_STATUS and 'status' in inputFieldNames
statusValues = set()

if (len(sys.argv) > 3) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout

totals = {'total' : 0, 'statusValues': {}}
for row in inputCSV:
  orgUnitPath = row['orgUnitPath']
  if orgUnitPath not in orgUnits:
    orgUnits[orgUnitPath] = {'total' : 0, 'statusValues': {}}
  orgUnits[orgUnitPath]['total'] += 1
  if checkStatus:
    statusValue = row['status']
    if statusValue not in statusValues:
      statusValues.add(statusValue)
    orgUnits[orgUnitPath]['statusValues'].setdefault(statusValue, 0)
    orgUnits[orgUnitPath]['statusValues'][statusValue] += 1
if checkStatus:
  for statusValue in sorted(statusValues):
    fieldnames.append(f'status.{statusValue}')
    totals['statusValues'][statusValue] = 0
outputCSV = csv.DictWriter(outputFile, fieldnames, lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()
for orgUnit, counts in sorted(iter(orgUnits.items())):
  row = {'orgUnitPath': orgUnit, 'total': counts['total']}
  totals['total'] += counts['total']
  if checkStatus:
    for statusValue, count in iter(counts['statusValues'].items()):
      row[f'status.{statusValue}'] = count
      totals['statusValues'][statusValue] += count
  outputCSV.writerow(row)
if SHOW_TOTALS:
  row = {'orgUnitPath': 'Totals', 'total': totals['total']}
  if checkStatus:
    for statusValue, count in iter(totals['statusValues'].items()):
      row[f'status.{statusValue}'] = count
  outputCSV.writerow(row)

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
