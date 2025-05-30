#!/usr/bin/env python3
"""
# Purpose: For a Google Drive User(s), get all drive file ACLs for files shared with anyone
# Customize: Set DESIRED_ALLOWFILEDISCOVERY.
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Get ACLs for all files, if you don't want all users, replace all users with your user selection in the command below
#    You can minimize the number of files downloaded by using a query with the visibility keyword.
#    DESIRED_ALLOWFILEDISCOVERY = 'Any' - query "(visibility='anyoneCanFind' or visibility='anyoneWithLink')"
#    DESIRED_ALLOWFILEDISCOVERY = 'True' - query "visibility='anyoneCanFind'"
#    DESIRED_ALLOWFILEDISCOVERY = 'False' - query "visibility='anyoneWithLink'"
#    Change the query as desired.
#  $ gam config auto_batch_min 1 redirect csv ./filelistperms.csv multiprocess all users print filelist fields id,name,basicpermissions,owners.emailaddress,mimetype <PutQueryHere>
# 2: From that list of ACLs, output a CSV file with headers "Owner,driveFileId,driveFileTitle,mimeType,permissionId,role,allowFileDiscovery"
#    that lists the driveFileIds and permissionIds for all ACLs shared with anyone
#    (n.b., driveFileTitle, mimeType, role and allowFileDiscovery are not used in the next step, they are included for documentation purposes)
#  $ python3 GetSharedWithAnyoneDriveACLs.py filelistperms.csv deleteperms.csv
# 3: Inspect deleteperms.csv, verify that it makes sense and then proceed
# 4: If desired, delete the ACLs
#  $ gam csv ./deleteperms.csv gam user "~Owner" delete drivefileacl "~driveFileId" "~permissionId"
"""

import csv
import re
import sys

FILE_NAME = 'name'
ALT_FILE_NAME = 'title'

# Specify desired value of allowFileDiscovery field: 'True', 'False', 'Any' (matches True and False)
# allowFileDiscovery False = withLink True
# allowFileDiscovery True = withLink False
DESIRED_ALLOWFILEDISCOVERY = 'Any'

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

PERMISSIONS_N_TYPE = re.compile(r"permissions.(\d+).type")

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['Owner', 'driveFileId', 'driveFileTitle', 'mimeType',
                                        'permissionId', 'role', 'allowFileDiscovery'],
                           lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin

for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  for k, v in iter(row.items()):
    mg = PERMISSIONS_N_TYPE.match(k)
    if mg and v == 'anyone':
      permissions_N = mg.group(1)
      allowFileDiscovery = row.get(f'permissions.{permissions_N}.allowFileDiscovery',
                                   str(row.get(f'permissions.{permissions_N}.withLink') == 'False'))
      if DESIRED_ALLOWFILEDISCOVERY in ('Any', allowFileDiscovery):
        outputCSV.writerow({'Owner': row['owners.0.emailAddress'],
                            'driveFileId': row['id'],
                            'driveFileTitle': row.get(FILE_NAME, row.get(ALT_FILE_NAME, 'Unknown')),
                            'mimeType': row['mimeType'],
                            'permissionId': f'id:{row[f"permissions.{permissions_N}.id"]}',
                            'role': row[f'permissions.{permissions_N}.role'],
                            'allowFileDiscovery': allowFileDiscovery})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
