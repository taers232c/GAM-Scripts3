#!/usr/bin/env python3
"""
# Purpose: For a Google Drive User(s), show all drive file ACLs for files shared with the desired type and withLink values
# Note: This script can use Basic or Advanced GAM:
#	https://github.com/GAM-team/GAM
#	https://github.com/taers232c/GAMADV-XTD3
# Customize: Set LINK_FIELD, DESIRED_TYPE and LINK_VALUE.
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Get ACLs for all files, if you don't want all users, replace all users with your user selection in the command below
#  $ Basic: gam all users print filelist id title permissions owners mimetype > filelistperms.csv
#  $ Advanced: gam config auto_batch_min 1 redirect csv ./filelistperms.csv multiprocess all users print filelist fields id,title,permissions,owners.emailaddress,mimetype
# 2: From that list of ACLs, output a CSV file with headers "Owner,driveFileId,driveFileTitle,permissionId,role"
#    that lists the driveFileIds and permissionIds for all ACLs with the desired type and withLink values
#  $ python3 GetTypeWithLinkDriveACLs.py filelistperms.csv deleteperms.csv
# 3: Inspect deleteperms.csv, verify that it makes sense and then proceed
# 4: If desired, delete the ACLs
#  $ gam csv ./deleteperms.csv gam user "~Owner" delete drivefileacl "~driveFileId" "~permissionId"
"""

import csv
import re
import sys

FILE_NAME = 'name'
ALT_FILE_NAME = 'title'
# For GAMADV-XTD3 with drive_v3_native_names = false
#LINK_FIELD = 'withLink'
# For GAMADV-XTD3 with drive_v3_native_names = true
LINK_FIELD = 'allowFileDiscovery'

DESIRED_TYPE = 'anyone' # anyone or domain
# Remember: withLink True = allowFileDiscovery False
LINK_VALUE = 'True' # 'True' or 'False'

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

PERMISSIONS_N_TYPE = re.compile(r"permissions.(\d+).type")

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['Owner', 'driveFileId', 'driveFileTitle', 'mimeType', 'permissionId', 'role'],
                           lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
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
      if v == DESIRED_TYPE and row[f'permissions.{permissions_N}.{LINK_FIELD}'] == LINK_VALUE:
        outputCSV.writerow({'Owner': row['owners.0.emailAddress'],
                            'driveFileId': row['id'],
                            'driveFileTitle': row.get(FILE_NAME, row.get(ALT_FILE_NAME, 'Unknown')),
                            'mimeType': row['mimeType'],
                            'permissionId': f'id:{row[f"permissions.{permissions_N}.id"]}',
                            'role': row[f'permissions.{permissions_N}.role']})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
