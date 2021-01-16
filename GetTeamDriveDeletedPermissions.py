#!/usr/bin/env python3
"""
# Purpose: Get ACLs for Team Drives that reference deleted groups/users
# Note: This script requires Advanced GAM:
#	https://github.com/taers232c/GAMADV-XTD3
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Get all Team Drives
#  $ gam redirect csv ./TeamDrives.csv print teamdrives fields id,name
# 2: Get ACLs for all Team Drives
#  $ gam redirect csv ./TeamDriveACLs.csv multiprocess csv TeamDrives.csv gam print drivefileacls ~id fields id,emailaddress,role,type,deleted pm deleted true em
# 3: From the list of ACLs, output a CSV file with headers "id,name,permissionId,role,type"
#  $ python3 GetTeamDriveDeletedUsersACLs.py TeamDriveACLs.csv TeamDrives.csv TeamDriveDeletedUsersACLs.csv
# 4: Inspect TeamDriveSuspendUsersACLs.csv, verify that it makes sense and then proceed if desired
# 5: Delete the ACLs
#  $ gam redirect stdout DeleteTeamDriveDeletedUsersACLs.log multiprocess redirect stderr stdout csv TeamDriveDeletedUsersACLs.csv gam delete drivefileacl "~id" "~permissionId"
"""

import csv
import re
import sys

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

PERMISSIONS_N_TYPE = re.compile(r"permissions.(\d+).type")

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

if (len(sys.argv) > 3) and (sys.argv[3] != '-'):
  outputFile = open(sys.argv[3], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['id', 'name', 'permissionId', 'role', 'type'], lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  for k, v in iter(row.items()):
    mg = PERMISSIONS_N_TYPE.match(k)
    if mg and v:
      permissions_N = mg.group(1)
      if row.get(f'permissions.{permissions_N}.deleted') == 'True':
        outputCSV.writerow({'id': row['id'],
                            'name': teamDriveNames.get(row['id'], row['id']),
                            'permissionId': f'id:{row[f"permissions.{permissions_N}.id"]}',
                            'role': row[f'permissions.{permissions_N}.role'],
                            'type': v})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
