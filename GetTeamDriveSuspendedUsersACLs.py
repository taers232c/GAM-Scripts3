#!/usr/bin/env python3
"""
# Purpose: Get ACLs for Team Drives that reference suspended users
# Note: This script requires Advanced GAM:
#	https://github.com/taers232c/GAMADV-XTD3
# Usage:
# 1: Get all Team Drives
#  $ gam redirect csv ./TeamDrives.csv print teamdrives fields id,name
# 2: Get ACLs for all Team Drives
#  $ gam redirect csv ./TeamDriveACLs.csv multiprocess csv TeamDrives.csv gam print drivefileacls ~id fields id,emailaddress,role,type,deleted pm type user em
# 3: Get suspended users
#  $ gam redirect csv SuspendedUsers.csv print users query "isSuspended=True"
# 4: From the list of ACLs, output a CSV file with headers "id,name,permissionId,role,emailAddress"
#  $ python3 GetTeamDriveSuspendedUsersACLs.py TeamDriveACLs.csv TeamDrives.csv SuspendedUsers.csv TeamDriveSuspendedUsersACLs.csv
# 5: Inspect TeamDriveSuspendedUsersACLs.csv, verify that it makes sense and then proceed if desired
# 4: Delete the ACLs
#  $ gam redirect stdout DeleteTeamDriveSuspendedUsersACLs.log multiprocess redirect stderr stdout csv TeamDriveSuspendedUsersACLs.csv gam delete drivefileacl "~id" "~permissionId"
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

userSet = set()
inputFile = open(sys.argv[3], 'r', encoding='utf-8')
for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  userSet.add(row['primaryEmail'].lower())
inputFile.close()

if sys.argv[1] != '-':
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin
inputCSV = csv.DictReader(inputFile, quotechar=QUOTE_CHAR)

if (len(sys.argv) > 4) and (sys.argv[4] != '-'):
  outputFile = open(sys.argv[4], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['id', 'name', 'permissionId', 'role', 'emailAddress'], lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  for k, v in iter(row.items()):
    mg = PERMISSIONS_N_TYPE.match(k)
    if mg and v == 'user':
      permissions_N = mg.group(1)
      if row.get(f'permissions.{permissions_N}.deleted') == 'True':
        continue
      emailAddress = row[f'permissions.{permissions_N}.emailAddress'].lower()
      if emailAddress in userSet:
        outputCSV.writerow({'id': row['id'],
                            'name': teamDriveNames.get(row['id'], row['id']),
                            'permissionId': f'id:{row[f"permissions.{permissions_N}.id"]}',
                            'role': row[f'permissions.{permissions_N}.role'],
                            'emailAddress': emailAddress})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
