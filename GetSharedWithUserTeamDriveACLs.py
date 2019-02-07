#!/usr/bin/env python3
"""
# Purpose: For a Google Drive User(s), show all drive file ACLs for Team Drive files shared with selected users or all users in selected domains.
# Note: This script requires Advanced GAM with Team Drive support:
#	https://github.com/taers232c/GAMADV-XTD, https://github.com/taers232c/GAMADV-XTD3
# Customize: Set FILE_NAME and ALT_FILE_NAME based on your environment. Set USER_LIST and DOMAIN_LIST.
# Usage:
# 1: If you want to include all Team Drives, do this step and then skip to step 4, otherwise start at step 2.
#  $ gam redirect csv ./TeamDrives.csv print teamdrives role organizer fields id,name
# 2: If want Team Drives for a specific set of organizers, replace <UserTypeEntity> with your user selection in the command below
#  $ gam redirect csv ./AllTeamDrives.csv <UserTypeEntity> print teamdrives role organizer fields id,name
# 3: Delete duplicate Team Drives (some may have multiple organizers). Make sure that ID_FIELD = 'id' in DeleteDuplicateRows.py
#  $ python DeleteDuplicateRows.py ./AllTeamDrives.csv ./TeamDrives.csv
# 4: Get ACLs for all team drive files
#  $ gam redirect csv ./filelistperms.csv multiprocess csv TeamDrives.csv gam user ~User print filelist select teamdriveid ~id fields teamdriveid id title permissions
# 5: From that list of ACLs, output a CSV file with headers "Owner,driveFileId,driveFileTitle,permissionId,role,emailAddress"
#    that lists the driveFileIds and permissionIds for all ACLs with the desired users
#    (n.b., driveFileTitle, role, and emailAddress are not used in the next step, they are included for documentation purposes)
#  $ python GetSharedWithUserDriveACLs.py filelistperms.csv deleteperms.csv
# 6: Inspect deleteperms.csv, verify that it makes sense and then proceed
# 7: Delete the ACLs
#  $ gam csv deleteperms.csv gam user "~Owner" delete drivefileacl "~driveFileId" "~permissionId"
"""

import csv
import re
import sys

# For GAM, GAMADV-X or GAMADV-XTD/GAMADV-XTD3 with drive_v3_native_names = false
FILE_NAME = 'title'
ALT_FILE_NAME = 'name'
# For GAMADV-XTD/GAMADV-XTD3 with drive_v3_native_names = true
#FILE_NAME = 'name'
#ALT_FILE_NAME = 'title'

# Substitute your specific user(s) in the list below, e.g., USER_LIST = ['user1@domain.com',] USER_LIST = ['user1@domain.com', 'user2@domain.com',]
# The list should be empty if you're only specifiying domains in DOMAIN_LIST, e,g, USER_LIST = []
USER_LIST = ['user1@domain.com',]
# Substitute your domain(s) in the list below if you want all users in the domain, e.g., DOMAIN_LIST = ['domain.com',] DOMAIN_LIST = ['domain1.com', 'domain2.com',]
# The list should be empty if you're only specifiying users in USER_LIST, e,g, DOMAIN__LIST = []
DOMAIN_LIST = ['domain.com',]

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

PERMISSIONS_N_TYPE = re.compile(r"permissions.(\d+).type")

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['Owner', 'driveFileId', 'driveFileTitle', 'permissionId', 'role', 'emailAddress'], lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin

for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  for k, v in iter(row.items()):
    mg = PERMISSIONS_N_TYPE.match(k)
    if mg and v == u'user':
      permissions_N = mg.group(1)
      if row['permissions.{0}.deleted'.format(permissions_N)] == u'True':
        continue
      emailAddress = row['permissions.{0}.emailAddress'.format(permissions_N)]
      domain = row['permissions.{0}.domain'.format(permissions_N)]
      if row['permissions.{0}.role'.format(permissions_N)] != 'owner' and (emailAddress in USER_LIST or domain in DOMAIN_LIST):
        outputCSV.writerow({'Owner': row['Owner'],
                            'driveFileId': row['id'],
                            'driveFileTitle': row.get(FILE_NAME, row.get(ALT_FILE_NAME, 'Unknown')),
                            'permissionId': 'id:{0}'.format(row['permissions.{0}.id'.format(permissions_N)]),
                            'role': row['permissions.{0}.role'.format(permissions_N)],
                            'emailAddress': emailAddress})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
