#!/usr/bin/env python3
"""
# Purpose: For a Google Drive User, get all drive file ACLs for files except those indicating the user as owner
# Note: This script can use Basic or Advanced GAM:
#	https://github.com/jay0lee/GAM
#	https://github.com/taers232c/GAMADV-XTD3
# 1: Use print filelist to get selected ACLs
#    Basic: gam user testuser@domain.com print filelist id title permissions owners > filelistperms.csv
#    Advanced: gam user testuser@domain.com print filelist fields id,title,permissions,owners.emailaddress > filelistperms.csv
# 2: From that list of ACLs, output a CSV file with headers "Owner,driveFileId,driveFileTitle,emailAddress"
#    that lists the driveFileIds/Titles for all ACLs except those indicating the user as owner
#  $ python ShowUserNonOwnerDriveACLs.py filelistperms.csv localperms.csv
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
outputCSV = csv.DictWriter(outputFile, ['Owner', 'driveFileId', 'driveFileTitle', 'emailAddress'], lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
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
      emailAddress = row.get(f'permissions.{permissions_N}.emailAddress', '')
      if v != 'user' or row[f'permissions.{permissions_N}.role'] != 'owner' or emailAddress != row['owners.0.emailAddress']:
        outputCSV.writerow({'Owner': row['owners.0.emailAddress'],
                            'driveFileId': row['id'],
                            'driveFileTitle': row.get(FILE_NAME, row.get(ALT_FILE_NAME, 'Unknown')),
                            'emailAddress': emailAddress})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
