#!/usr/bin/env python3
"""
# Purpose: For a Google Drive User(s), delete all duplicate drive files
# Note: This script requires Advanced GAM:
#	https://github.com/taers232c/GAMADV-X, https://github.com/taers232c/GAMADV-XTD, https://github.com/taers232c/GAMADV-XTD3
# Customize: Set FILE_NAME and CREATED_DATE based on your environment.
# Usage:
# 1: Get information for all files, if you don't want all users, replace all users with your user selection in the command below
#    These fields are required: fields id,title,createddate,mimetype filepath
#    You can add additional fields that will be preserved in the output.
#    You can add a select option if you want to only process files in a specific folder
#    If you don't want to delete folders, add showmimetype not gfolder
#  $ gam redirect csv ./UserFiles.csv multiprocess all users print filelist fields id,title,createddate,mimetype filepath
#  $ gam redirect csv ./UserFiles.csv user user@domain.com print filelist fields id,title,createddate,mimetype filepath
#                               select drivefilename "Folder Name" showmimetype not gfolder
# 2: From that list of files, output a CSV file with the same headers as the input CSV file
#    that lists the drive file Ids that have the same owner, title, mimeType and paths with a createdDate older than the most recent createdDate
#  $ python DeleteDuplicateFiles.py ./UserFiles.csv ./DuplicateFiles.csv
# 3: Inspect DuplicateFiles.csv, verify that it makes sense and then proceed
# 4: Delete the duplicate files
#  $ gam redirect stdout ./DeleteDuplicateFiles.log multiprocess redirect stderr stdout csv ./DuplicateFiles.csv gam user "~Owner" delete drivefile "~id"
"""

import csv
import sys

# For GAMADV-X or GAMADVX-TD/GAMADVX-TD3 with drive_v3_native_names = false
FILE_NAME = 'title'
CREATED_DATE = 'createdDate'
# For GAMADVX-TD/GAMADVX-TD3 with drive_v3_native_names = true
#FILE_NAME = 'name'
#CREATED_DATE = 'createdTime'

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

def rowPaths(crow):
  paths = set()
  for i in range(0, int(crow['paths'])):
    paths.add(crow['path.{0}'.format(i)])
  return paths

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w')
else:
  outputFile = sys.stdout
if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin

prevOwner = None
prevTitle = None
prevMimeType = None
prevCreatedDate = None
prevPaths = None

inputCSV = csv.DictReader(inputFile, quotechar=QUOTE_CHAR)
outputCSV = csv.DictWriter(outputFile, inputCSV.fieldnames, lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

rows = sorted(inputCSV, key=lambda k: k[CREATED_DATE], reverse=True)
for row in sorted(rows, key=lambda k: (k['Owner'], k[FILE_NAME], k['mimeType'], k['paths'])):
  if ((row['Owner'] == prevOwner)
      and (row[FILE_NAME] == prevTitle)
      and (row['mimeType'] == prevMimeType)
      and (row[CREATED_DATE] < prevCreatedDate)
      and (rowPaths(row) == prevPaths)):
    outputCSV.writerow(row)
  else:
    prevOwner = row['Owner']
    prevTitle = row[FILE_NAME]
    prevMimeType = row['mimeType']
    prevCreatedDate = row[CREATED_DATE]
    prevPaths = rowPaths(row)
if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
