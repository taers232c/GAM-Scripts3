#!/usr/bin/env python3
"""
# Purpose: For a Google Drive User(s), show all non-shared drive files
# Note: This script can use Basic or Advanced GAM:
#	https://github.com/jay0lee/GAM
#	https://github.com/taers232c/GAMADV-X, https://github.com/taers232c/GAMADV-XTD, https://github.com/taers232c/GAMADV-XTD3
# Customize: Set FILE_NAME and ALT_FILE_NAME based on your environment.
# Usage:
# 1: Get ACLs for all files, if you don't want all users, replace all users with your user selection in the command below
#  $ Basic: gam all users print filelist id title permissions > filelistperms.csv
#  $ Basic: gam user user@domain.com print filelist id title permissions > filelistperms.csv
#  $ Advanced: gam config auto_batch_min 1 redirect csv ./filelistperms.csv multiprocess all users print filelist id title permissions
#  $ Advanced: gam redirect csv ./filelistperms.csv multiprocess user user@domain.com print filelist id title permissions
# 2: From that list of ACLs, output a CSV file that lists only the non-shared files.
#  $ python GetNonSharedFiles.py filelistperms.csv nonsharedfiles.csv
"""

import csv
import re
import sys

# For GAM, GAMADV-X or GAMADVX-TD/GAMADVX-TD3 with drive_v3_native_names = false
FILE_NAME = 'title'
ALT_FILE_NAME = 'name'
# For GAMADVX-TD/GAMADVX-TD3 with drive_v3_native_names = true
#FILE_NAME = 'name'
#ALT_FILE_NAME = 'title'

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

PERMISSIONS_N_TYPE = re.compile(r"permissions.(\d+).type")

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w')
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
      if v == u'user':
        permissions_N = mg.group(1)
        role = row['permissions.{0}.role'.format(permissions_N)]
        emailAddress = row['permissions.{0}.emailAddress'.format(permissions_N)]
        if (role and role != 'owner') or (emailAddress and emailAddress != row[u'Owner']):
          shared = True
      elif v:
        shared = True
  if not shared:
    outputCSV.writerow(row)

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
