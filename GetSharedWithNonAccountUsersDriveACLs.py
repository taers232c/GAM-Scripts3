#!/usr/bin/env python3
"""
# Purpose: For a Google Drive User(s), show all drive file ACLs for files shared with users outside of your account.
# Note: This script can use Basic or Advanced GAM:
#	https://github.com/GAM-team/GAM
#	https://github.com/taers232c/GAMADV-XTD3
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Get users in account
#  $ Basic: gam print users > accountusers.csv
#  $ Advanced: gam redirect csv ./accountusers.csv print users
# 2: Get ACLs for all files, if you don't want all users, replace all users with your user selection in the command below
#  $ Basic: gam all users print filelist id title permissions owners > filelistperms.csv
#  $ Advanced: gam config auto_batch_min 1 redirect csv ./filelistperms.csv multiprocess all users print filelist fields id,title,permissions,owners.emailaddress
# 3: From that list of ACLs, output a CSV file with headers "Owner,driveFileId,driveFileTitle,permissionId,role,emailAddress"
#    that lists the driveFileIds and permissionIds for all ACLs with the non-account users
#    (n.b., driveFileTitle, role, and emailAddress are not used in the next step, they are included for documentation purposes)
#  $ python3 GetSharedWithNonAccountUsersDriveACLs.py accountusers.csv filelistperms.csv deleteperms.csv
# 4: Inspect deleteperms.csv, verify that it makes sense and then proceed
# 5: If desired, delete the ACLs
#  $ gam csv ./deleteperms.csv gam user "~Owner" delete drivefileacl "~driveFileId" "~permissionId"
"""

import csv
import re
import sys

FILE_NAME = 'name'
ALT_FILE_NAME = 'title'

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

PERMISSIONS_N_TYPE = re.compile(r"permissions.(\d+).type")

if (len(sys.argv) > 3) and (sys.argv[3] != '-'):
  outputFile = open(sys.argv[3], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['Owner', 'driveFileId', 'driveFileTitle', 'permissionId', 'role', 'emailAddress'], lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  inputFile = open(sys.argv[2], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin

accountUsers = set()
usersFile = open(sys.argv[1], 'r', encoding='utf-8')
for row in csv.DictReader(usersFile, quotechar=QUOTE_CHAR):
  accountUsers.add(row['primaryEmail'])
usersFile.close()

for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  for k, v in iter(row.items()):
    mg = PERMISSIONS_N_TYPE.match(k)
    if mg and v == 'user':
      permissions_N = mg.group(1)
      if row.get(f'permissions.{permissions_N}.deleted') == 'True':
        continue
      emailAddress = row[f'permissions.{permissions_N}.emailAddress']
      if row[f'permissions.{permissions_N}.role'] != 'owner' and emailAddress not in accountUsers:
        outputCSV.writerow({'Owner': row['owners.0.emailAddress'],
                            'driveFileId': row['id'],
                            'driveFileTitle': row.get(FILE_NAME, row.get(ALT_FILE_NAME, 'Unknown')),
                            'permissionId': f'id:{row[f"permissions.{permissions_N}.id"]}',
                            'role': row[f'permissions.{permissions_N}.role'],
                            'emailAddress': emailAddress})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
