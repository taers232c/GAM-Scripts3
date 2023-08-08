#!/usr/bin/env python3
"""
# Purpose: Get folder sizes
# Note: This script requires Advanced GAM:
#	https://github.com/taers232c/GAMADV-XTD3
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Get users files
#  $ gam redirect csv ./filelist.csv user user@domain.com print filelist select <Parentid> fields id,name,size,mimetype,parents filepath showownedby any showparent
# 3: From that list of files, output a CSV file with the same headers with size
#  $ python3 GetFolderSize.py filelist.csv folderlist.csv
"""

import csv
import re
import sys

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

PARENTS_N_FIELD = re.compile(r"parents.(\d+).(.*)")

inputFile = open(sys.argv[1], 'r', encoding='utf-8')
inputCSV = csv.DictReader(inputFile, quotechar=QUOTE_CHAR)
parentFieldNames = ['parents']
outputFieldNames = []
for k in inputCSV.fieldnames:
  if PARENTS_N_FIELD.match(k):
    parentFieldNames.append(k)
  else:
    outputFieldNames.append(k)

outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
outputCSV = csv.DictWriter(outputFile, outputFieldNames, lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

folders = {}
for row in inputCSV:
  if row['mimeType'] == 'application/vnd.google-apps.folder':
    folderId = row['id']
    for field in parentFieldNames:
      row.pop(field)
    if folderId not in folders:
      folders[folderId] = {'row': row, 'size': 0}
    else:
      folders[folderId]['row'] = row
  else:
    parentId = row['parents.0.id']
    size = int(row['size']) if row['size'].isdigit() else 0
    if parentId not in folders:
      folders[parentId] = {'row': {'id': parentId, 'path.0': 'Unknown'}, 'size': size}
    else:
      folders[parentId]['size'] += size

for data in sorted(iter(folders.values()), key=lambda k: k['row']['path.0']):
  data['row']['size'] = data['size']
  outputCSV.writerow(data['row'])

inputFile.close()
outputFile.close()
