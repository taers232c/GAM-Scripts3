#!/usr/bin/env python3
"""
# Purpose: For a Google Drive User(s), delete all files except those in selected top level folders
# Note: This script requires Advanced GAM:
#	https://github.com/taers232c/GAMADV-XTD3
# Customize: Set PATHS_TO_SAVE
# Usage:
# 1: Get information for all files, if you don't want all users, replace all users with your user selection
#     in the command below, e.g., ou /Students/Classof2019
#    These fields are required: fields id,name,owners.emailaddress
#    You can add additional fields that will be preserved in the output.
#  $ gam config auto_batch_min 1 redirect csv ./UserFiles.csv multiprocess all users print filelist fields id,name,owners.emailaddress fullpath
# 2: From that list of files, output a CSV file with the same headers as the input CSV file
#    that lists the drive file Ids that are not in the selected top level folders
#  $ python SelectiveDelete.py ./UserFiles.csv ./DeleteFiles.csv
# 3: Inspect DeleteFiles.csv, verify that it makes sense and then proceed
# 4: Delete the  files
#  $ gam redirect stdout ./DeleteFiles.log multiprocess redirect stderr stdout csv ./DetelteFiles.csv gam user "~owners.0.emailAddress" delete drivefile "~id"
"""

import csv
import sys

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

# ['My Drive/xxx'] or ['My Drive/xxx', 'My Drive/yyy']
PATHS_TO_SAVE = []

def pathToSave(crow):
  for i in range(0, int(crow['paths'])):
    path = crow['path.{0}'.format(i)]
    for p in PATHS_TO_SAVE:
      if path.startswith(p):
        return True
  return False

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
  if not pathToSave(row):
    outputCSV.writerow(row)
if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
