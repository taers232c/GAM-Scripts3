#!/usr/bin/env python3
"""
# Purpose: For a Google Drive User(s), show all drive file ACls for files shared with the desired users.
# Note: This script can use basic GAM: https://github.com/jay0lee/GAM or advanced GAM: https://github.com/taers232c/GAMADV-X
# Usage:
# 1: Get ACLS for all files, if you don't want all users, replace all users with your user selection in the command below
#  $ Basic: gam all users print filelist id title permissions > filelistperms.csv
#  $ Advanced: gam config auto_batch_min 1 redirect csv ./filelistperms.csv multiprocess all users print filelist id title permissions
# 2: From that list of ACLs, output a CSV file with headers "Owner,driveFileId,driveFileTitle,permissionId,role,emailAddress"
#    that lists the driveFileIds and permissionIds for all ACLs with the desired users
#  $ python GetSharedWithUserDriveACLs.py filelistperms.csv deleteperms.csv
# 3: Inspect deleteperms.csv, verify that it makes sense and then proceed
# 4: Delete the ACLS
#  $ gam csv deleteperms.csv gam user "~Owner" delete drivefileacl "~driveFileId" "~permissionId"
"""

import csv
import re
import sys

# Substitute your user(s) in the list below, e.g., userList = ['user1@domain.com',] userList = ['user1@domain.com', 'user2@domain.com',]
userList = ['user@domain.com',]

id_n_type = re.compile(r"permissions.(\d+).type")

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['Owner', 'driveFileId', 'driveFileTitle', 'permissionId', 'role', 'emailAddress'], lineterminator='\n')
outputCSV.writeheader()

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r')
else:
  inputFile = sys.stdin

for row in csv.DictReader(inputFile):
  for k, v in iter(row.items()):
    mg = id_n_type.match(k)
    if mg:
      perm_user = mg.group(1)
      emailAddress = row['permissions.{0}.emailAddress'.format(perm_user)]
      if (row['permissions.{0}.type'.format(perm_user)] == u'user') and (emailAddress in userList):
        outputCSV.writerow({'Owner': row['Owner'],
                            'driveFileId': row['id'],
                            'driveFileTitle': row['title'],
                            'permissionId': 'id:{0}'.format(row['permissions.{0}.id'.format(perm_user)]),
                            'role': row['permissions.{0}.role'.format(perm_user)],
                            'emailAddress': emailAddress})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
