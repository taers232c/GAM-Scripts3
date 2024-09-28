#!/usr/bin/env python3
"""
# Purpose: For a Google Drive User(s), output a CSV file showing the number of files created by day by mimeType
# Note: This script can use GAM7 or Advanced GAM:
#       https://github.com/GAM-team/GAM                                                                                                                               
#	https://github.com/taers232c/GAMADV-XTD3
# Customize: Set REVERSE
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Get ACLs for all files, if you don't want all users, replace all users with your user selection in the command below
#  $ gam config auto_batch_min 1 redirect csv ./filelist.csv multiprocess all users print filelist fields id,createdtime,mimetype
# 2: From that list of ACLs, output a CSV file with headers:
#      Owner,createdTime,mimeType
#  $ python3 GetDailyMimeTypeCreations.py filelist.csv mimetypecreations.csv
"""

import csv
import sys

# Set REVERSE = True for createdTime newest to oldest
# Set REVERSE = False for createdTime oldest to newest
REVERSE = True
QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin

userDailyMimeTypeCounts = {}
mimeTypesSet = set()
for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  owner = row['Owner']
  createdDate, createdTime = row['createdTime'].split('T')
  mimeType = row['mimeType']
  mimeTypesSet.add(mimeType)
  userDailyMimeTypeCounts.setdefault(owner, {})
  userDailyMimeTypeCounts[owner].setdefault(createdDate, {})
  userDailyMimeTypeCounts[owner][createdDate].setdefault(mimeType, 0)
  userDailyMimeTypeCounts[owner][createdDate][mimeType] += 1

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputFieldNames = ['Owner', 'createdTime']
outputFieldNames.extend(sorted(mimeTypesSet))
outputCSV = csv.DictWriter(outputFile, outputFieldNames, lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

for owner, createdTimes in sorted(userDailyMimeTypeCounts.items()):
  for createdTime, mimeTypes in sorted(createdTimes.items(), reverse=REVERSE):
    row = {'Owner': owner, 'createdTime': createdTime}
    for mimeType, count in sorted(mimeTypes.items()):
      row[mimeType] = count
    for mimeType in mimeTypesSet:
      if mimeType not in row:
        row[mimeType] = 0
    outputCSV.writerow(row)

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
