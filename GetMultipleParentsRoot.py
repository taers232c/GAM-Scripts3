#!/usr/bin/env python3
"""
# Purpose: For a Google Drive User, delete root as a parent of files that have root as a parent and other parents
# Note: This script requires Advanced GAM:
#	https://github.com/taers232c/GAMADV-XTD3
# Usage:
# 1: Get all of the files for testuser@domain.com
#  $ gam redirect csv ./userfiles.csv user testuser@domain.com print filelist fields id,title,parents,owners.emailaddress
# 2: From that list of files, output a CSV file with headers "Owner,driveFileId,driveFileTitle"
#    that lists the driveFileIds for all files that have root as a parent and other parents
#  $ python3 GetMultipleParentsRoot.py ./userfiles.csv ./rootparents.csv
# 3: Inspect rootparents.csv, verify that it makes sense and then proceed
# 4: Delete root as parent
#  $ gam redirect stdout ./deleterootparent.out multiprocess csv ./rootparents.csv gam user "~Owner" update drivefile "~driveFileId" removeparents root
"""

import csv
import re
import sys

FILE_NAME = 'name'
ALT_FILE_NAME = 'title'

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

PARENTS_N_ID = re.compile(r"parents.(\d+).id")

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['Owner', 'driveFileId', 'driveFileTitle'], lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin

for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  if row['parents'] and int(row['parents']) <= 1:
    continue
  for k, v in iter(row.items()):
    mg = PARENTS_N_ID.match(k)
    if mg and v:
      parents_N = mg.group(1)
      if row[f'parents.{parents_N}.isRoot'] == 'True':
        outputCSV.writerow({'Owner': row['owners.0.emailAddress'],
                            'driveFileId': row['id'],
                            'driveFileTitle': row.get(FILE_NAME, row.get(ALT_FILE_NAME, 'Unknown'))})
        continue

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
