#!/usr/bin/env python3
"""
# Purpose: Get ACLs for Team Drives, add Team Drive name (and optional additional fields)  to row
# Note: This script requires Advanced GAM:
#	https://github.com/taers232c/GAMADV-XTD3
# Customize: Set ONE_ACL_PER_ROW,ADDITIONAL_TEAM_DRIVE_FIELDS as desired
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Get all Team Drives
#  $ gam redirect csv ./TeamDrives.csv print teamdrives fields id,name
# 2: Get ACLs for all Team Drives; adjust the fields list as desired
#  $ gam redirect csv ./TeamDriveACLs.csv multiprocess csv ./TeamDrives.csv gam print drivefileacls "~id" fields id,domain,emailaddress,role,type,deleted
# 3: From that list of ACLs, output a CSV file with the same headers as TeamDriveACLs.csv with the Team Drive name as the third column
#  $ python3 GetTeamDriveNameACLs.py TeamDriveACLs.csv TeamDrives.csv TeamDriveNameACLs.csv
"""

import csv
import re
import sys

ONE_ACL_PER_ROW = False # Set True for one ACL per row
ADDITIONAL_TEAM_DRIVE_FIELDS = ['createdTime'] # Team Drive fields in addition to name to add to row, e.g., ADDITIONAL_TEAM_DRIVE_FIELDS = ['createdTime']

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

PERMISSIONS_N_FIELD = re.compile(r"permissions.\d+.(.*)")

if (len(sys.argv) > 3) and (sys.argv[3] != '-'):
  outputFile = open(sys.argv[3], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout

teamDriveData = {}
inputFile = open(sys.argv[2], 'r', encoding='utf-8')
for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  teamDriveData[row['id']] = row
inputFile.close()

if sys.argv[1] != '-':
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin
inputCSV = csv.DictReader(inputFile, quotechar=QUOTE_CHAR)
fieldnames = inputCSV.fieldnames[0:2]+['name']+ADDITIONAL_TEAM_DRIVE_FIELDS
if not ONE_ACL_PER_ROW:
  fieldnames += inputCSV.fieldnames[2:]
else:
  permFieldNames = set()
  for k in inputCSV.fieldnames[3:]:
    mg = PERMISSIONS_N_FIELD.match(k)
    if mg:
      permFieldNames.add(mg.group(1))
  fieldnames.extend([f'permissions.{k}' for k in sorted(permFieldNames)])

outputCSV = csv.DictWriter(outputFile, fieldnames, lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

if not ONE_ACL_PER_ROW:
  for row in inputCSV:
    td = teamDriveData.get(row['id'], {})
    row['name'] = td.get('name', row['id'])
    for field in ADDITIONAL_TEAM_DRIVE_FIELDS:
      row[field] = td.get(field, '')
    outputCSV.writerow(row)
else:
  for row in inputCSV:
    td = teamDriveData.get(row['id'], {})
    orow = {'Owner': row['Owner'], 'id': row['id'], 'name': td.get('name', row['id'])}
    for field in ADDITIONAL_TEAM_DRIVE_FIELDS:
      orow[field] = td.get(field, '')
    for permissions_N in range(0, int(row['permissions'])):
      prow = orow.copy()
      for k in permFieldNames:
        if row.get(f'permissions.{permissions_N}.{k}'):
          prow[f'permissions.{k}'] = row[f'permissions.{permissions_N}.{k}']
      outputCSV.writerow(prow)

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
