#!/usr/bin/env python3
"""
# Purpose: For a Google Drive User, delete all drive file ACls except those indicating the user as owner
# Note: This script requires advanced GAM: https://github.com/taers232c/GAMADV-X
# Usage:
# 1: Use print filelist to get selected ACLS
#    Syntax, advanced GAM: gam <UserTypeEntity> print filelist [anyowner|(showownedby any|me|others)]
#				[query <QueryDriveFile>] [fullquery <QueryDriveFile>] [select <DriveFileEntity>|orphans] [depth <Number>] [showparent]
#    For a full description of print filelist, see: https://github.com/taers232c/GAMADV-XTD/wiki/Users---Drive---Files
#    Example, advanced GAM: gam redirect csv ./filelistperms.csv user testuser@domain.com print filelist id permissions
# 2: From that list of ACLs, output a CSV file with headers "Owner,driveFileId,permissionIds"
#    that lists the driveFileIds and permissionIds for all ACls except those indicating the user as owner
#  $ python GetUserNonOwnerDrivePermissions.py filelistperms.csv deleteperms.csv
# 3: Inspect deleteperms.csv, verify that it makes sense and then proceed
# 4: Delete the ACLS
#  $ gam csvkmd users deleteperms.csv keyfield Owner subkeyfield driveFileId datafield permissionIds delimiter "," delete permissions csvsubkey driveFileId csvdata permissionIds
"""

import csv
import re
import sys

id_n_address = re.compile(r"permissions.(\d+).id")

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['Owner', 'driveFileId', 'permissionIds'], lineterminator='\n')
outputCSV.writeheader()

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r')
else:
  inputFile = sys.stdin

for row in csv.DictReader(inputFile):
  permissionIds = []
  for k, v in iter(row.items()):
    mg = id_n_address.match(k)
    if mg:
      perm_group = mg.group(1)
      if v:
        if (row['permissions.{0}.type'.format(perm_group)] != 'user'
            or row['permissions.{0}.role'.format(perm_group)] != 'owner'
            or row.get('permissions.{0}.emailAddress'.format(perm_group), '') != row['Owner']):
          permissionIds.append(row['permissions.{0}.id'.format(perm_group)])
  if permissionIds:
    outputCSV.writerow({'Owner': row['Owner'],
                        'driveFileId': row['id'],
                        'permissionIds': ','.join(permissionIds)})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
