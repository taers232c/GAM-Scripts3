#!/usr/bin/env python3
"""
# Purpose: Add <DriveFilePermissionList> to a list of files/folders
# Note: This script requires Advanced GAM:
#	https://github.com/taers232c/GAMADV-X, https://github.com/taers232c/GAMADV-XTD, https://github.com/taers232c/GAMADV-XTD3
# Definitions:
# <DriveFileACLRole> :: =commenter|editor|organizer|owner|reader|writer
# <DriveFilePermissionScope> ::= anyone|anyonewithlink|user:<EmailAddress>|group:<EmailAddress>|domain:<DomainName>|domainwithlink:<DomainName>
# <DriveFilePermission> ::= <DriveFilePermissionScope>;<DriveFileACLRole>
# <DriveFilePermissionList> ::= "<DriveFilePermission>(,<DriveFilePermission)*"
# Usage:
# 1: Use print filelist to get selected ACLs
#    Syntax: gam <UserTypeEntity> print filelist [anyowner|(showownedby any|me|others)]
#			[query <QueryDriveFile>] [fullquery <QueryDriveFile>] [select <DriveFileEntity>|orphans] [depth <Number>] [showparent]
#    For a full description of print filelist, see: https://github.com/taers232c/GAMADV-XTD/wiki/Users-Drive-Files
#  $ gam redirect csv ./filelist.csv user testuser@domain.com print filelist id ...
# 2: From that list of files, output a CSV file with headers "Owner,driveFileId,permissions"
#    that lists the driveFileIds and permissions to be added
#  $ AddPermissions.py filelist.csv addperms.csv '<DriveFilePermissionsList>'
# 3: Add the ACLs
#    Parallel, faster:
#  $ gam csv addperms.csv gam user ~Owner add permissions ~driveFileId ~permissions
#    Serial, cleaner output:
#  $ gam csvkmd users addperms.csv keyfield Owner subkeyfield driveFileId datafield permissions delimiter "," add permissions csvsubkey driveFileId csvdata permissions
"""

import csv
import sys

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

DRIVEFILE_ACL_ROLES = ['commenter', 'editor', 'owner', 'read', 'reader', 'writer',]
DRIVEFILE_ACL_PERMISSION_TYPES = ['anyone', 'anyonewithlink', 'domain', 'domainwithlink', 'group', 'user',]

if len(sys.argv) < 4:
  sys.stderr.write('ERROR: "<DriveFilePermissionsList>" not specified\n')
  sys.exit(1)
permissions = sys.argv[3]
errors = 0
for permission in permissions.replace(',', ' ').split():
  try:
    scope, role = permission.split(';', 1)
    if scope.find(':') != -1:
      permType, value = scope.split(':', 1)
    else:
      permType = scope
    if permType not in DRIVEFILE_ACL_PERMISSION_TYPES:
      sys.stderr.write('ERROR: Type ({0}) must be in list ({1}), permission ({2})\n'.format(permType, ','.join(DRIVEFILE_ACL_PERMISSION_TYPES), permission))
      errors += 1
    if role not in DRIVEFILE_ACL_ROLES:
      sys.stderr.write('ERROR: Role ({0}) must be in list ({1}), permission ({2})\n'.format(role, ','.join(DRIVEFILE_ACL_ROLES), permission))
      errors += 1
  except ValueError:
    sys.stderr.write('ERROR: Permisson must be (scope;role), permission ({0})\n'.format(permission))
    errors += 1
if errors:
  sys.exit(1)

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['Owner', 'driveFileId', 'permissions'], lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin

for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  outputCSV.writerow({'Owner': row['Owner'],
                      'driveFileId': row['id'],
                      'permissions': permissions})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
