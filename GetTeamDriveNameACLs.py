#!/usr/bin/env python3
"""
# Purpose: Get ACLs for Team Drives, add Team Drive name to row
# Note: This script requires Advanced GAM:
#	https://github.com/taers232c/GAMADV-XTD3
# Customize: Set ONE_ACL_PER_ROW as desired
# Usage:
# 1: Get all Team Drives
#  $ gam redirect csv ./TeamDrives.csv print teamdrives fields id,name
# 2: Get ACLs for all Team Drives; adjust the fields list as desired
#  $ gam redirect csv ./TeamDriveACLs.csv multiprocess csv TeamDrives.csv gam print drivefileacls ~id fields emailaddress,role,type
# 3: From that list of ACLs, output a CSV file with the same headers as TeamDriveACLs.csv witn the Team Drive name as the third column
#  $ python GetTeamDriveNameACLs.py TeamDriveACLs.csv TeamDrives.csv TeamDriveNameACLs.csv
"""

import csv
import re
import sys

ONE_ACL_PER_ROW = False # Set True for one ACL per row

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

PERMISSIONS_N_FIELD = re.compile(r"permissions.\d+.(.*)")

if (len(sys.argv) > 3) and (sys.argv[3] != '-'):
  outputFile = open(sys.argv[3], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout

teamDriveNames = {}
inputFile = open(sys.argv[2], 'r', encoding='utf-8')
for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  teamDriveNames[row['id']] = row['name']
inputFile.close()

if sys.argv[1] != '-':
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin
inputCSV = csv.DictReader(inputFile, quotechar=QUOTE_CHAR)
if not ONE_ACL_PER_ROW:
  fieldnames = inputCSV.fieldnames[:]
  fieldnames.insert(2, 'name')
else:
  fieldnames = inputCSV.fieldnames[0:2]
  fieldnames.append('name')
  permFieldNames = set()
  for k in inputCSV.fieldnames[3:]:
    mg = PERMISSIONS_N_FIELD.match(k)
    if mg:
      permFieldNames.add(mg.group(1))
  fieldnames.extend(sorted(permFieldNames))

outputCSV = csv.DictWriter(outputFile, fieldnames, lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

if not ONE_ACL_PER_ROW:
  for row in inputCSV:
    row['name'] = teamDriveNames.get(row['id'], row['id'])
    outputCSV.writerow(row)
else:
  for row in inputCSV:
    for permissions_N in range(0, int(row['permissions'])):
      orow = {'Owner': row['Owner'], 'id': row['id'], 'name': teamDriveNames.get(row['id'], row['id'])}
      for k in permFieldNames:
        if row.get(f'permissions.{permissions_N}.{k}'):
          orow[k] = row[f'permissions.{permissions_N}.{k}']
      outputCSV.writerow(orow)

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
