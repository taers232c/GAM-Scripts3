#!/usr/bin/env python3
"""
# Purpose: Show formatted top-level ACLs for Team Drives
# Note: This script requires Advanced GAM with Team Drive support:
#	https://github.com/taers232c/GAMADV-XTD, https://github.com/taers232c/GAMADV-XTD3
# Usage:
# 1: Get all Team Drives.
#  $ gam redirect csv ./TeamDrives.csv print teamdrives fields id,name
# 2: Get ACLs for all Team Drives
#  $ gam redirect csv ./TeamDriveACLs.csv multiprocess csv TeamDrives.csv gam print drivefileacls ~id
# 3: From that list of ACLs, output a CSV file with formatted headers and the Team Drive name added
#  $ python GetTeamDriveACLs.py TeamDriveACLs.csv TeamDrives.csv TeamDriveACLsFormatted.csv
"""

import csv
import sys

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

# What headers should be dropped?
DROP_HEADERS = ['Owner', 'permission.teamDrivePermissionDetails', 'permission.permissionDetails', 'permission.photoLink']
# For headers that aren't dropped, map the long name to a shorter name
MAP_HEADERS = {
  'id': 'id',
  'permission.allowFileDiscovery': 'allowFileDiscovery',
  'permission.deleted': 'deleted',
  'permission.displayName': 'displayName',
  'permission.domain': 'domain',
  'permission.emailAddress': 'emailAddress',
  'permission.expirationDate': 'expirationDate',
  'permission.expirationTime': 'expirationTime',
  'permission.id': 'permissionId',
  'permission.name': 'name',
  'permission.role': 'role',
  'permission.type': 'type',
  'permission.withLink': 'withLink',
  }
# What is the header for the Team Drive name
TEAMDRIVE_NAME_HEADER = 'teamDrive'

if (len(sys.argv) > 3) and (sys.argv[3] != '-'):
  outputFile = open(sys.argv[3], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout

teamDriveNames = {}
inputFile = open(sys.argv[2], 'r', encoding='utf-8')
for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  teamDriveNames[row['id']] = row['name']
inputFile.close()

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin
inputCSV = csv.DictReader(inputFile, quotechar=QUOTE_CHAR)

outputFieldnames = []
for k in inputCSV.fieldnames:
  for dh in DROP_HEADERS:
    if k.startswith(dh):
      break
  else:
    outputFieldnames.append(MAP_HEADERS.get(k, k))
outputFieldnames.insert(1, TEAMDRIVE_NAME_HEADER)
outputCSV = csv.DictWriter(outputFile, outputFieldnames, lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

for irow in inputCSV:
  row = {}
  for k, v in iter(irow.items()):
    for dh in DROP_HEADERS:
      if k.startswith(dh):
        break
    else:
      row[MAP_HEADERS.get(k, k)] = v
  row[TEAMDRIVE_NAME_HEADER] = teamDriveNames.get(irow['id'], irow['id'])
  outputCSV.writerow(row)

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
