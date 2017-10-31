#!/usr/bin/env python3
"""
# Purpose: For a Google Drive User, delete root as a parent of files that have root as a parent and other parents
# Note: This uses advanced GAM: https://github.com/taers232c/GAMADV-X
# Usage:
# 1: Get all of the files for testuser@domain.com
#  $ gam redirect csv ./userfiles.csv user testuser@domain.com print filelist id title parents
# 2: From that list of files, output a CSV file with headers "Owner,driveFileId,title"
#    that lists the driveFileIds for all files that have root as a parent and other parents
#  $ python GetMultipleParentsRoot.py ./userfiles.csv ./rootparents.csv
# 3: Inspect rootparents.csv, verify that it makes sense and then proceed
# 4: Delete root as parent
#  $ gam redirect stdout ./deleterootparent.out multiprocess csv ./rootparents.csv gam user "~Owner" update drivefile "~driveFileId" removeparents root
"""

import csv
import re
import sys

id_n_address = re.compile(r"parents.(\d+).id")

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['Owner', 'driveFileId', 'title'], lineterminator='\n')
outputCSV.writeheader()

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r')
else:
  inputFile = sys.stdin

for row in csv.DictReader(inputFile):
  if row['parents'] and int(row['parents']) <= 1:
    continue
  for k, v in iter(row.items()):
    mg = id_n_address.match(k)
    if mg:
      perm_group = mg.group(1)
      if v:
        if row['parents.{0}.isRoot'.format(perm_group)] == 'True':
          outputCSV.writerow({'Owner': row['Owner'],
                              'driveFileId': row['id'],
                              'title': row['title']})
          continue

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
