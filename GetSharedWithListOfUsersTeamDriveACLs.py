#!/usr/bin/env python3
"""
# Purpose: Show all drive file ACLs for Team Drive files shared with a list of users from a CSV file
# Note: This script requires Advanced GAM:
#	https://github.com/taers232c/GAMADV-XTD3
# Customize:f Set USER_HEADERS, NON_INHERITED_ACLS_ONLY
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Prepare a CSV file with a list of user email addresses; set USER_HEADERS to identify the column(s) containing the email addresses
#  $ more Users.csv
#  email
#  testuser1@domain1.com
#  testuser2@domain1.com
#  testuser1@domain2.com
#  testuser2@domain2.com
#  ...
#  $ more QuadUsers.csv
#  email1,email2,email3,email4
#  testuser1@domain1.com,testuser2@domain1.com,testuser1@domain2.com,testuser2@domain2.com
#  ...
# For all Team Drives, start at step 2; For Team Drives selected by user/group/OU, start at step 8
# All Team Drives
# 2: Get all Team Drives.
#  $ gam redirect csv ./TeamDrives.csv print teamdrives fields id,name
# 3: Get ACLs for all Team Drives
#  $ gam redirect csv ./TeamDriveACLs.csv multiprocess csv ./TeamDrives.csv gam print drivefileacls "~id" fields emailaddress,role,type
# 4: Customize GetTeamDriveOrganizers.py for this task:
#    Set DOMAIN_LIST as required
#    Set ONE_ORGANIZER = True
#    Set SHOW_GROUP_ORGANIZERS = False
#    Set SHOW_USER_ORGANIZERS = True
# 5: From that list of ACLs, output a CSV file with headers "id,name,organizers"
#    that shows the organizers for each Team Drive
#  $ python3 GetTeamDriveOrganizers.py TeamDriveACLs.csv TeamDrives.csv TeamDriveOrganizers.csv
# 6: Get ACLs for all team drive files
#  $ gam config csv_input_row_filter "organizers:regex:^.+$" redirect csv ./filelistperms.csv multiprocess csv ./TeamDriveOrganizers.csv gam user "~organizers" print filelist select teamdriveid "~id" fields teamdriveid,id,name,permissions,mimetype pm type user em pmfilter
# 7: Go to step 12
# Selected Team Drives
# 8: If you want Team Drives for a specific set of organizers, replace <UserTypeEntity> with your user selection in the command below
#  $ gam redirect csv ./AllTeamDrives.csv <UserTypeEntity> print teamdrives role organizer fields id,name
# 9: Customize DeleteDuplicateRows.py for this task:
#    Set ID_FIELD = 'id'
# 10: Delete duplicate Team Drives (some may have multiple organizers).
#  $ python3 DeleteDuplicateRows.py ./AllTeamDrives.csv ./TeamDrives.csv
# 11: Get ACLs for all team drive files
#  $ gam redirect csv ./filelistperms.csv multiprocess csv ./TeamDrives.csv gam user "~User" print filelist select teamdriveid "~id" fields teamdriveid,id,name,permissions,mimetype pm type user em pmfilter
# Common code
# 12: From that list of ACLs, output a CSV file with headers "Owner,driveFileId,driveFileTitle,mimeType,permissionId,role,emailAddress"
#    that lists the driveFileIds and permissionIds for all ACLs with the desired users
#    (n.b., driveFileTitle, mimeType, role, and emailAddress are not used in the next step, they are included for documentation purposes)
#  $ python3 GetSharedWithListOfUsersTeamDriveACLs.py filelistperms.csv deleteperms.csv Users.csv
# 13: Inspect deleteperms.csv, verify that it makes sense and then proceed
# 14: If desired, delete the ACLs
#  $ gam csv ./deleteperms.csv gam user "~Owner" delete drivefileacl "~driveFileId" "~permissionId"
"""

import csv
import re
import sys

FILE_NAME = 'name'
ALT_FILE_NAME = 'title'

# The headers in the CSV file that contain the user email addresses
USER_HEADERS = ['email'] # USER_HEADERS = ['email1', 'email2', 'email3', 'email4']

# Specify whether only non-inherited ACLs should be output; inherited ACLs can't be deleted
NON_INHERITED_ACLS_ONLY = True

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

PERMISSIONS_N_TYPE = re.compile(r"permissions.(\d+).type")

userSet = set()
inputFile = open(sys.argv[3], 'r', encoding='utf-8')
for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  for header in USER_HEADERS:
    user = row[header].lower()
    if user:
      userSet.add(user)
inputFile.close()

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['Owner', 'driveFileId', 'driveFileTitle', 'mimeType',
                                        'permissionId', 'role', 'emailAddress'],
                           lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin

for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  for k, v in iter(row.items()):
    mg = PERMISSIONS_N_TYPE.match(k)
    if mg and v == 'user':
      permissions_N = mg.group(1)
      if row.get(f'permissions.{permissions_N}.deleted') == 'True':
        continue
      if NON_INHERITED_ACLS_ONLY and str(row.get(f'permissions.{permissions_N}.permissionDetails.0.inherited', False)) == 'True':
        continue
      emailAddress = row[f'permissions.{permissions_N}.emailAddress'].lower()
      if emailAddress in userSet:
        outputCSV.writerow({'Owner': row['Owner'],
                            'driveFileId': row['id'],
                            'driveFileTitle': row.get(FILE_NAME, row.get(ALT_FILE_NAME, 'Unknown')),
                            'mimeType': row['mimeType'],
                            'permissionId': f'id:{row[f"permissions.{permissions_N}.id"]}',
                            'role': row[f'permissions.{permissions_N}.role'],
                            'emailAddress': emailAddress})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
