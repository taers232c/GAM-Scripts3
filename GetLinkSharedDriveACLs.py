#!/usr/bin/env python3
"""
# Purpose: For a Google Drive User(s), get all drive file ACLs for files shared with anyone/domain withlink
# Note: This script can use Basic or Advanced GAM:
#	https://github.com/jay0lee/GAM - Version 6.07+
#	https://github.com/taers232c/GAMADV-XTD3 - Version 6.04.17+
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Get ACLs for all files, if you don't want all users, replace all users with your user selection in the command below
#  $ Basic: gam all users print filelist id title permissions owners linksharemetadata resourcekey mimetype webviewlink query "visibility='anyoneWithLink' or visibility='domainWithLink'" > filelistperms.csv
#  $ Advanced: gam config auto_batch_min 1 redirect csv ./filelistperms.csv multiprocess all users print filelist fields id,name,permissions,owners.emailaddress,linksharemetadata,resourcekey,mimetype,webviewlink  query "visibility='anyoneWithLink' or visibility='domainWithLink'"
# 2: From that list of ACLs, output a CSV file with headers "Owner,driveFileId,driveFileTitle,mimeType,permissionId,role,allowFileDiscovery,resourceKey,linkShareMetadata.securityUpdateEligible,linkShareMetadata.securityUpdateEnabled,webViewLink"
#    that lists the driveFileIds, permissionIds and link share details for all ACLs shared with anyone/domain withlink
#  $ python3 GetLinkSharedDriveACLs.py filelistperms.csv linksharedperms.csv
"""

import csv
import re
import sys

FILE_NAME = 'name'
ALT_FILE_NAME = 'title'

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

PERMISSIONS_N_TYPE = re.compile(r"permissions.(\d+).type")

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile,
                           ['Owner', 'driveFileId', 'driveFileTitle', 'mimeType', 'permissionId', 'role', 'allowFileDiscovery',
                            'resourceKey', 'linkShareMetadata.securityUpdateEligible', 'linkShareMetadata.securityUpdateEnabled',
                            'webViewLink'],
                           lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin

for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  for k, v in iter(row.items()):
    mg = PERMISSIONS_N_TYPE.match(k)
    if mg and v in {'anyone', 'domain'}:
      permissions_N = mg.group(1)
      allowFileDiscovery = row.get(f'permissions.{permissions_N}.allowFileDiscovery', str(row.get(f'permissions.{permissions_N}.withLink') == 'False'))
      if allowFileDiscovery == 'False':
        outputCSV.writerow({'Owner': row['owners.0.emailAddress'],
                            'driveFileId': row['id'],
                            'driveFileTitle': row.get(FILE_NAME, row.get(ALT_FILE_NAME, 'Unknown')),
                            'mimeType': row['mimeType'],
                            'permissionId': f'id:{row[f"permissions.{permissions_N}.id"]}',
                            'role': row[f'permissions.{permissions_N}.role'],
                            'allowFileDiscovery': allowFileDiscovery,
                            'linkShareMetadata.securityUpdateEligible': row.get('linkShareMetadata.securityUpdateEligible', ''),
                            'linkShareMetadata.securityUpdateEnabled': row.get('linkShareMetadata.securityUpdateEnabled', ''),
                            'resourceKey': row.get('resourceKey', ''),
                            'webViewLink': row.get('webViewLink', '')})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
