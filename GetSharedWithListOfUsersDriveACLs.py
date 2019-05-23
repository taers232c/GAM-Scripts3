#!/usr/bin/env python3
"""
# Purpose: For a Google Drive User(s), show all drive file ACLs for files shared with a list of users from a CSV file
# Note: This script can use Basic or Advanced GAM:
#	https://github.com/jay0lee/GAM
#	https://github.com/taers232c/GAMADV-X, https://github.com/taers232c/GAMADV-XTD, https://github.com/taers232c/GAMADV-XTD3
# Customize: Set FILE_NAME and ALT_FILE_NAME based on your environment. Set USER_HEADER
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
# 3: From that list of ACLs, output a CSV file with headers "Owner,driveFileId,driveFileTitle,permissionId,role,emailAddress"
#    that lists the driveFileIds and permissionIds for all ACLs with the desired users
#    (n.b., driveFileTitle, role, and emailAddress are not used in the next step, they are included for documentation purposes)
#  $ python GetSharedWithListOfUsersDriveACLs.py filelistperms.csv deleteperms.csv Users.csv
# 4: Inspect deleteperms.csv, verify that it makes sense and then proceed
# 5: Delete the ACLs
#  $ gam csv deleteperms.csv gam user "~Owner" delete drivefileacl "~driveFileId" "~permissionId"
"""

import csv
import re
import sys

# For GAM, GAMADV-X or GAMADV-XTD/GAMADV-XTD3 with drive_v3_native_names = false
#FILE_NAME = 'title'
#ALT_FILE_NAME = 'name'
# For GAMADV-XTD/GAMADV-XTD3 with drive_v3_native_names = true
FILE_NAME = 'name'
ALT_FILE_NAME = 'title'

# The header in the CSV file that contains the user email addresses
USER_HEADER = u'email'

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

PERMISSIONS_N_TYPE = re.compile(r"permissions.(\d+).type")

userSet = set()
inputFile = open(sys.argv[3], 'r', encoding='utf-8')
for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  userSet.add(row[USER_HEADER].lower())
inputFile.close()

if sys.argv[2] != '-':
  outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['Owner', 'driveFileId', 'driveFileTitle', 'permissionId', 'role', 'emailAddress'], lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

if sys.argv[1] != '-':
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
      emailAddress = row['permissions.{0}.emailAddress'.format(permissions_N)].lower()
      if row['permissions.{0}.role'.format(permissions_N)] != 'owner' and emailAddress in userSet:
        outputCSV.writerow({'Owner': row['owners.0.emailAddress'],
                            'driveFileId': row['id'],
                            'driveFileTitle': row.get(FILE_NAME, row.get(ALT_FILE_NAME, 'Unknown')),
                            'permissionId': 'id:{0}'.format(row['permissions.{0}.id'.format(permissions_N)]),
                            'role': row['permissions.{0}.role'.format(permissions_N)],
                            'emailAddress': emailAddress})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
