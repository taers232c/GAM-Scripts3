#!/usr/bin/env python3
"""
# Purpose: For a Google Drive User(s), show all drive file ACLs for files shared with a list of users from a CSV file
# Customize: Set USER_HEADERS
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
# 2: Get ACLs for all files, if you don't want all users, replace all users with your user selection in the command below
#    If you don't want all files, use query/fullquery
#  $ gam config auto_batch_min 1 redirect csv ./filelistperms.csv multiprocess all users print filelist fields id,title,permissions,owners.emailaddress,mimetype pm type user notrole owner em pmfilter
# 3: From that list of ACLs, output a CSV file with headers "Owner,driveFileId,driveFileTitle,mimeType,permissionId,role,emailAddress"
#    that lists the driveFileIds and permissionIds for all ACLs with the desired users
#    (n.b., driveFileTitle, mimeType, role, and emailAddress are not used in the next step, they are included for documentation purposes)
#  $ python3 GetSharedWithListOfUsersDriveACLs.py filelistperms.csv deleteperms.csv Users.csv
# 4: Inspect deleteperms.csv, verify that it makes sense and then proceed
# 5: If desired, delete the ACLs
#  $ gam csv ./deleteperms.csv gam user "~Owner" delete drivefileacl "~driveFileId" "~permissionId"
"""

import csv
import re
import sys

FILE_NAME = 'name'
ALT_FILE_NAME = 'title'

# The headers in the CSV file that contain the user email addresses
USER_HEADERS = ['email'] # USER_HEADERS = ['email1', 'email2', 'email3', 'email4']

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

if sys.argv[2] != '-':
  outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['Owner', 'driveFileId', 'driveFileTitle', 'mimeType',
                                        'permissionId', 'role', 'emailAddress'],
                           lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

if sys.argv[1] != '-':
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin

for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  for k, v in iter(row.items()):
    mg = PERMISSIONS_N_TYPE.match(k)
    if mg and v == 'user':
      permissions_N = mg.group(1)
      if row.get(f'permissions.{permissions_N}.deleted', '') == 'True':
        continue
      emailAddress = row[f'permissions.{permissions_N}.emailAddress'].lower()
      if row[f'permissions.{permissions_N}.role'] != 'owner' and emailAddress in userSet:
        outputCSV.writerow({'Owner': row['owners.0.emailAddress'],
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
