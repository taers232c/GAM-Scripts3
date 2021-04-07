#!/usr/bin/env python3
"""
# Purpose: For a Google Drive User(s), show all drive file permissions and file paths
# Note: This script requires Advanced GAM:
#	https://github.com/taers232c/GAMADV-XTD3
# Customize: Set INCLUDE_OWNER
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Get ACLs for all files, if you don't want all users, replace all users with your user selection in the command below
#  $ You can have GAM do some pre-filtering
#  $ INCLUDE_OWNER_ACLS = False
#    Add the following to the command to eliminate non shared files: pm not role owner em
#  $ gam config auto_batch_min 1 redirect csv ./filelistperms.csv multiprocess all users print filelist fields id,name,permissions,owners.emailaddress filepath
#  $ gam redirect csv ./filelistperms.csv user user@domain.com print filelist fields id,name,permissions,owners.emailaddress filepath
# 2: From that list of ACLs, output a CSV file that lists the shared file permissions; the file paths are included on each line
#  $ python3 GetFilePermissionsWithPaths.py filelistperms.csv deleteperms.csv
# 3: Inspect deleteperms.csv, verify that it makes sense and then proceed if desired
# 4: If desired, delete the ACLs
#  $ gam csv deleteperms.csv gam user "~Owner" delete drivefileacl "~driveFileId" "~permissionId"
"""

import csv
import re
import sys

FILE_NAME = 'name'
ALT_FILE_NAME = 'title'

# Indicate whether to include owner ACLs in the output
INCLUDE_OWNER_ACLS = False

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

PERMISSIONS_N_TYPE = re.compile(r"permissions.(\d+).type")

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin
inputCSV = csv.DictReader(inputFile, quotechar=QUOTE_CHAR)
inputFieldNames = inputCSV.fieldnames

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputFieldNames = ['Owner', 'driveFileId', 'driveFileTitle', 'permissionId',
                    'role', 'type', 'emailAddress', 'domain', 'allowFileDiscovery']
for fieldName in inputFieldNames:
  if fieldName.startswith('path'):
    outputFieldNames.append(fieldName)
outputCSV = csv.DictWriter(outputFile, outputFieldNames,
                           lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

for row in inputCSV:
  prow = {}
  for k, v in iter(row.items()):
    if k.startswith('path'):
      prow[k] = v
  for k, v in iter(row.items()):
    mg = PERMISSIONS_N_TYPE.match(k)
    if mg and v:
      permissions_N = mg.group(1)
      if row[f'permissions.{permissions_N}.role'] == 'owner' and not INCLUDE_OWNER_ACLS:
        continue
      if v in ['user', 'group']:
        allowFileDiscovery = ''
        emailAddress = row[f'permissions.{permissions_N}.emailAddress'].lower()
        domain = emailAddress[emailAddress.find('@')+1:]
      elif v == 'domain':
        allowFileDiscovery = row.get(f'permissions.{permissions_N}.allowFileDiscovery',
                                     str(row.get(f'permissions.{permissions_N}.withLink') == 'False'))
        emailAddress = ''
        domain = row[f'permissions.{permissions_N}.domain']
      else: #anyone
        allowFileDiscovery = row.get(f'permissions.{permissions_N}.allowFileDiscovery',
                                     str(row.get(f'permissions.{permissions_N}.withLink') == 'False'))
        emailAddress = ''
        domain = ''
      orow = {'Owner': row['owners.0.emailAddress'],
              'driveFileId': row['id'],
              'driveFileTitle': row.get(FILE_NAME, row.get(ALT_FILE_NAME, 'Unknown')),
              'permissionId': f'id:{row[f"permissions.{permissions_N}.id"]}',
              'role': row[f'permissions.{permissions_N}.role'],
              'type': v,
              'emailAddress': emailAddress,
              'domain': domain,
              'allowFileDiscovery': allowFileDiscovery}
      orow.update(prow)
      outputCSV.writerow(orow)

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
