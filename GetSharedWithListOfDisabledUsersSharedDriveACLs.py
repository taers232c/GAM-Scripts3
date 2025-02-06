#!/usr/bin/env python3
"""
# Purpose: For a Google Drive User(s), show all drive file ACLs for files shared exclusively with a list of users from a CSV file
# Note: This script use Advanced GAM:
#	https://github.com/taers232c/GAMADV-XTD3
# Customize: Set USER_HEADERS
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: If you want to include all Team Drives, do this step and then skip to step 4, otherwise start at step 2.
#  $ gam redirect csv ./TeamDrives.csv print teamdrives fields id,name
# 2: Get ACLs for all Team Drives
#  $ gam redirect csv ./TeamDriveACLs.csv multiprocess csv ./TeamDrives.csv gam print drivefileacls "~id" fields id,emailaddress,role,type
# 3: Get suspended accounts
#  $ gam redirect csv ./Users.csv print users issuspended true
# 4: From that list of ACLs, output a CSV file with headers "id,name,organizers"
#    that shows the organizers for each Team Drive
#  $ python3 GetTeamDriveOrganizers.py TeamDriveACLs.csv TeamDrives.csv TeamDriveOrganizers.csv
# 5: Get Shared Drive files ACL with non-inherited permissions
#  $ gam config csv_input_row_filter "organizers:regex:^.+$" redirect csv ./TeamDriveFileFilesPermission.csv multiprocess csv ./TeamDriveOrganizers.csv gam user "~organizers" print filelist select teamdriveid "~id" fields id,name,permissions pmfilter pm deleted false inherited false em
# 6: Get Ids to remove ACLs
#  $ python3 GetSharedWithListOfDisabledUsersSharedDriveACLs.py TeamDriveFileFilesPermission.csv Users.csv
# 7: Cleanup
#  $ gam csv ./cleanup.csv gam user ~owner delete drivefileacl "~id" "~emailAddress"
"""

import csv
import re
import sys

# The headers in the CSV file that contain the user email addresses
USER_HEADERS = ['primaryEmail']

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

PERMISSIONS_N_TYPE = re.compile(r"permissions.(\d+).type")

userSet = set()
inputFile = open(sys.argv[2], 'r', encoding='utf-8')
for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  for header in USER_HEADERS:
    user = row[header].lower()
    if user:
      userSet.add(user)
inputFile.close()

inputFile = open(sys.argv[1], 'r', encoding='utf-8')
inputCSV = csv.DictReader(inputFile, quotechar=QUOTE_CHAR)
outputFile = open('cleanup.csv', 'w', encoding='utf-8', newline='')
outputCSV = csv.DictWriter(outputFile, ['owner', 'id', 'emailAddress'], lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
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
      emailAddress = row.get(f'permissions.{permissions_N}.emailAddress', '').lower()
      if not emailAddress:
        continue
      if emailAddress not in userSet:
        break
      shared = True
      outputCSV.writerow({'owner': row['Owner'],
                        'id': row['id'],
                        'emailAddress': emailAddress})

inputFile.close()
outputFile.close()
