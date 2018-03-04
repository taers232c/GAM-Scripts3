#!/usr/bin/env python3
"""
# Purpose: For a Google Drive User, delete root as a parent of files that have root as a parent and other parents
# Note: This script requires Advanced GAM:
#	https://github.com/taers232c/GAMADV-X, https://github.com/taers232c/GAMADV-XTD, https://github.com/taers232c/GAMADV-XTD3
# Customize: Set FILE_NAME and ALT_FILE_NAME based on your environment
# Usage:
# 1: Get all of the files for testuser@domain.com
#  $ gam redirect csv ./userfiles.csv user testuser@domain.com print filelist id title parents
# 2: From that list of files, output a CSV file with headers "Owner,driveFileId,driveFileTitle"
#    that lists the driveFileIds for all files that have root as a parent and other parents
#  $ python GetMultipleParentsRoot.py ./userfiles.csv ./rootparents.csv
# 3: Inspect rootparents.csv, verify that it makes sense and then proceed
# 4: Delete root as parent
#  $ gam redirect stdout ./deleterootparent.out multiprocess csv ./rootparents.csv gam user "~Owner" update drivefile "~driveFileId" removeparents root
"""

import csv
import re
import sys

# For GAMADV-X or GAMADVX-TD/GAMADVX-TD3 with drive_v3_native_names = false
FILE_NAME = 'title'
ALT_FILE_NAME = 'name'
# For GAMADVX-TD/GAMADVX-TD3 with drive_v3_native_names = true
#FILE_NAME = 'name'
#ALT_FILE_NAME = 'title'

PARENTS_N_ID = re.compile(r"parents.(\d+).id")

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['Owner', 'driveFileId', 'driveFileTitle'], lineterminator='\n')
outputCSV.writeheader()

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin

for row in csv.DictReader(inputFile):
  if row['parents'] and int(row['parents']) <= 1:
    continue
  for k, v in iter(row.items()):
    mg = PARENTS_N_ID.match(k)
    if mg and v:
      parents_N = mg.group(1)
      if row['parents.{0}.isRoot'.format(parents_N)] == 'True':
        outputCSV.writerow({'Owner': row['Owner'],
                            'driveFileId': row['id'],
                            'driveFileTitle': row.get(FILE_NAME, row.get(ALT_FILE_NAME, 'Unknown'))})
        continue

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
