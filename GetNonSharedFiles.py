#!/usr/bin/env python3
"""
# Purpose: For a Google Drive User(s), show all non-shared drive files
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Get ACLs for all files, if you don't want all users, replace all users with your user selection in the command below
#  $ gam config auto_batch_min 1 redirect csv ./filelistperms.csv multiprocess all users print filelist id title permissions
#  $ gam redirect csv ./filelistperms.csv user user@domain.com print filelist id title permissions
# 2: From that list of ACLs, output a CSV file that lists only the non-shared files.
#  $ python3 GetNonSharedFiles.py filelistperms.csv nonsharedfiles.csv
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

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin

inputCSV = csv.DictReader(inputFile, quotechar=QUOTE_CHAR)
outputCSV = csv.DictWriter(outputFile, inputCSV.fieldnames, lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

for row in inputCSV:
  shared = False
  for k, v in iter(row.items()):
    mg = PERMISSIONS_N_TYPE.match(k)
    if mg:
      if v == 'user':
        permissions_N = mg.group(1)
        role = row[f'permissions.{permissions_N}.role']
        emailAddress = row.get(f'permissions.{permissions_N}.emailAddress', '').lower()
        if (role and role != 'owner') or (emailAddress and emailAddress != row['Owner'].lower()):
          shared = True
      elif v:
        shared = True
  if not shared:
    outputCSV.writerow(row)

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
