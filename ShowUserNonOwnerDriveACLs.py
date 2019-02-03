#!/usr/bin/env python3
"""
# Purpose: For a Google Drive User, get all drive file ACLs for files except those indicating the user as owner
# Note: This script can use Basic or Advanced GAM:
#	https://github.com/jay0lee/GAM
#	https://github.com/taers232c/GAMADV-X, https://github.com/taers232c/GAMADV-XTD, https://github.com/taers232c/GAMADV-XTD3
# Customize: Set FILE_NAME and ALT_FILE_NAME based on your environment.
# 1: Use print filelist to get selected ACLs
#    gam user testuser@domain.com print filelist id title permissions > filelistperms.csv
# 2: From that list of ACLs, output a CSV file with headers "Owner,driveFileId,driveFileTitle,emailAddress"
#    that lists the driveFileIds/Titles for all ACLs except those indicating the user as owner
#  $ python ShowUserNonOwnerDriveACLs.py filelistperms.csv localperms.csv
"""

import csv
import re
import sys

# For GAM, GAMADV-X or GAMADV-XTD/GAMADV-XTD3 with drive_v3_native_names = false
FILE_NAME = 'title'
ALT_FILE_NAME = 'name'
# For GAMADV-XTD/GAMADV-XTD3 with drive_v3_native_names = true
#FILE_NAME = 'name'
#ALT_FILE_NAME = 'title'

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

PERMISSIONS_N_TYPE = re.compile(r"permissions.(\d+).type")

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w', newline='')
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
      emailAddress = row.get('permissions.{0}.emailAddress'.format(permissions_N), u'')
      if v != 'user' or row['permissions.{0}.role'.format(permissions_N)] != 'owner' or emailAddress != row['Owner']:
        outputCSV.writerow({'Owner': row['Owner'],
                            'driveFileId': row['id'],
                            'driveFileTitle': row.get(FILE_NAME, row.get(ALT_FILE_NAME, 'Unknown')),
                            'emailAddress': emailAddress})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
