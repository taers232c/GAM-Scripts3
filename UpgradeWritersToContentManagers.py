#!/usr/bin/env python3
"""
# Purpose: Upgrade users with writer access on Team Drives to fileOrganizer access (aka content manager)
# Note: This script requires Advanced GAM:
#	https://github.com/taers232c/GAMADV-XTD3
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Get all Team Drives
#  $ gam redirect csv ./TeamDrives.csv print teamdrives fields id
# 2: Get ACLs for all Team Drives
#  $ gam redirect csv ./TeamDriveACLs.csv multiprocess csv ./TeamDrives.csv gam print drivefileacls "~id" fields id,emailaddress,role,type,deleted
# 3: From that list of ACLs, output a CSV file with headers "teamDriveId,permissionId,type,emailAddress"
#    that lists the teamDriveIds and permissionIds for all ACLs with role writer.
#  $ python3 UpgradeWritersToContentManagers.py ./TeamDriveACLs.csv UpgradedACLs.csv
# 4: Inspect UpgradedACLs.csv, verify that it makes sense and then proceed
# 5: Upgrade the ACLs
#  $ gam redirect stdout ./UpgradedACLs.log multiprocess redirect stderr stdout multiprocess csv UpgradetdACLs.csv gam update drivefileacl teamdriveid "~teamDriveId" "~permissionId" role fileOrganizer
"""

import csv
import re
import sys

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

PERMISSIONS_N_TYPE = re.compile(r"permissions.(\d+).type")

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['teamDriveId', 'permissionId', 'type', 'emailAddress'], lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin

for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  for k, v in iter(row.items()):
    mg = PERMISSIONS_N_TYPE.match(k)
    if mg and v:
      permissions_N = mg.group(1)
      role = row[f'permissions.permissions_N{}.role']
      if role != 'writer' or v not in ['user', 'group']:
        continue
      if row.get(f'permissions.{permissions_N}.deleted')) == 'True':
        continue
      outputCSV.writerow({'teamDriveId': row['id'],
                          'permissionId': f'id:{row[f"permissions.{permissions_N}.id"]}',
                          'type': v,
                          'emailAddress': row[f'permissions.{permissions_N}.emailAddress']})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
