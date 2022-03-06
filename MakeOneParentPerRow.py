#!/usr/bin/env python3
"""
# Purpose: For a print filelist file, write multiple parents into separate rows.
# Note: This script can use Basic or Advanced GAM:
#	https://github.com/GAM-team/GAM
#	https://github.com/taers232c/GAMADV-XTD3
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Get all files, if you don't want all users, replace all users with your user selection in the command below
#  $ Basic: gam all users print filelist id title permissions parents ... > filelist.csv
#  $ Basic: gam user user@domain.com print filelist id title permissions parents ... > filelist.csv
#  $ Advanced: gam config auto_batch_min 1 redirect csv ./filelist.csv multiprocess all users print filelist fields id,name,permissions,parents
#  $ Advanced: gam redirect csv ./filelist.csv user user@domain.com print filelist fields id,name,permissions,parents ...
# 3: From that list of files, output a CSV file with the same headers but just 'parents,parents.id,parents.isRoot'
#  $ python3 MakeOneParentPerRow.py filelist.csv filelistoppr.csv
"""

import csv
import re
import sys

ONE_ACL_PER_ROW = False # Set True for one ACL per row

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

PARENTS_N_FIELD = re.compile(r"parents.(\d+).(.*)")

if sys.argv[1] != '-':
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin
inputCSV = csv.DictReader(inputFile, quotechar=QUOTE_CHAR)
fieldnames = []
nonParentNFieldNames = []
parentFields = []
lastParent = -1
for k in inputCSV.fieldnames:
  mg = PARENTS_N_FIELD.match(k)
  if mg:
    lastParent = int(mg.group(1))
    sk = mg.group(2)
    if sk not in parentFields:
      parentFields.append(sk)
      fieldnames.append(f'parents.{sk}')
  else:
    fieldnames.append(k)
    nonParentNFieldNames.append(k)

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, fieldnames, lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

for row in inputCSV:
  if lastParent >= 0:
    orow = {}
    for k in nonParentNFieldNames:
      orow[k] = row[k]
    numParents = int(row['parents'])
    if numParents > 0:
      orow['parents'] = 1
      for n in range(0, numParents):
        for sk in parentFields:
          orow[f'parents.{sk}'] = row.get(f'parents.{n}.{sk}', '')
        outputCSV.writerow(orow)
    else:
      orow['parents'] = 0
      for sk in parentFields:
        orow[f'parents.{sk}'] = ''
      outputCSV.writerow(orow)
  else:
    outputCSV.writerow(row)

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
