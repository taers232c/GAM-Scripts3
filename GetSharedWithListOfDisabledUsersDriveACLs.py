#!/usr/bin/env python3
"""
# Purpose: For a Google Drive User(s), show all drive file ACLs for files shared exclusively with a list of users from a CSV file
# Note: This script can use Basic or Advanced GAM:
#	https://github.com/GAM-team/GAM
#	https://github.com/taers232c/GAMADV-XTD3
# Customize: Set USER_HEADER
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Prepare a CSV file with a list of user email addresses; set USER_HEADER to identify the column containing the email addresses
#  $ more Users.csv
#  email
#  testuser1@domain1.com
#  testuser2@domain1.com
#  testuser1@domain2.com
#  testuser2@domain2.com
#  ...
# 2: Get ACLs for all files, if you don't want all users, replace all users with your user selection in the command below
#    If you don't want all files, use query/fullquery
#  $ Basic: gam all users print filelist id title permissions owners > filelistperms.csv
#  $ Advanced: gam config auto_batch_min 1 redirect csv ./filelistperms.csv multiprocess all users print filelist fields id,title,permissions,owners.emailaddress
# 3: From that list of ACLs, output a CSV file with the same headers as the input CSV file
#    only including files that are shared exclusively with the users in Users.csv
#  $ python3 GetSharedWithListOfDisabledUsersDriveACLs.py filelistperms.csv disabledusersperms.csv Users.csv
# 4: Inspect disabledusersperms.csv, verify that it makes sense and then proceed
"""

import csv
import re
import sys

FILE_NAME = 'name'
ALT_FILE_NAME = 'title'

# The header in the CSV file that contains the user email addresses
USER_HEADER = 'email'

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

PERMISSIONS_N_TYPE = re.compile(r"permissions.(\d+).type")

userSet = set()
inputFile = open(sys.argv[3], 'r', encoding='utf-8')
for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  userSet.add(row[USER_HEADER].lower())
inputFile.close()

inputFile = open(sys.argv[1], 'r', encoding='utf-8')
inputCSV = csv.DictReader(inputFile, quotechar=QUOTE_CHAR)

outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
outputCSV = csv.DictWriter(outputFile, inputCSV.fieldnames, lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

for row in inputCSV:
  shared = False
  for k, v in iter(row.items()):
    mg = PERMISSIONS_N_TYPE.match(k)
    if mg:
      if v in {'anyone', 'domain', 'group'}:
        break
      permissions_N = mg.group(1)
      if row.get(f'permissions.{permissions_N}.deleted') == 'True':
        continue
      if row[f'permissions.{permissions_N}.role'] == 'owner':
        continue
      emailAddress = row[f'permissions.{permissions_N}.emailAddress'].lower()
      if not emailAddress:
        continue
      if emailAddress not in userSet:
        break
      shared = True
  else:
    if shared:
      outputCSV.writerow(row)

inputFile.close()
outputFile.close()
