#!/usr/bin/env python3
"""
# Purpose: Show all drive file ACLs for Team Drive files
# Note: This script requires Advanced GAM:
#	https://github.com/taers232c/GAMADV-XTD3
# Customize: Set NON_INHERITED_ACLS_ONLY
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# For all Team Drives, start at step 1; For specific Team Drives start at step 7
# All Team Drives
# 1: Get all Team Drives.
#  $ gam redirect csv ./TeamDrives.csv print teamdrives fields id,name
# 2: Get ACLs for all Team Drives
#  $ gam redirect csv ./TeamDriveACLs.csv multiprocess csv ./TeamDrives.csv gam print drivefileacls "~id" fields emailaddress,role,type
# 3: Customize GetTeamDriveOrganizers.py for this task:
#    Set DOMAIN_LIST as required
#    Set ONE_ORGANIZER = True
#    Set SHOW_GROUP_ORGANIZERS = False
#    Set SHOW_USER_ORGANIZERS = True
# 4: From that list of ACLs, output a CSV file with headers "id,name,organizers"
#    that shows the organizers for each Team Drive
#  $ python3 GetTeamDriveOrganizers.py TeamDriveACLs.csv TeamDrives.csv TeamDriveOrganizers.csv
# 5: Get ACLs for all team drive files
#  $ gam redirect csv ./filelistperms.csv multiprocess csv ./TeamDriveOrganizers.csv gam user "~organizers" print filelist select teamdriveid "~id" fields teamdriveid,id,name,permissions
# 6: Go to step 9
# Specific Team Drives
# 7: If you want file ACLs for specific Team Drives make a CSV file TeamDrives.csv
#    with three columns (organizer,id,name) that show an organizer, Team Drive ID and Team Drive Name
# 8: Get ACLs for all team drive files
#  $ gam redirect csv ./filelistperms.csv multiprocess csv ./TeamDrives.csv gam user "~organizer" print filelist select teamdriveid "~id" fields teamdriveid,id,title,permissions
# Common code
# 9: From that list of ACLs, output a CSV file with headers "Owner,teamDriveId,teamDriveName,driveFileId,driveFileTitle,permissionId,role,type,emailAddress,domain,deleted"
#    that lists the driveFileIds and permissionIds for all files
#  $ python3 GetTeamDriveFileACLs.py filelistperms.csv TeamDrives.csv TeamDriveFileACLs.csv
# 10: Inspect TeamDriveFileACLs.csv, use as desired
"""

import csv
import re
import sys

FILE_NAME = 'name'
ALT_FILE_NAME = 'title'

# Specify whether only non-inherited ACLs should be output; inherited ACLs can't be deleted
NON_INHERITED_ACLS_ONLY = True

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

PERMISSIONS_N_TYPE = re.compile(r"permissions.(\d+).type")

if (len(sys.argv) > 3) and (sys.argv[3] != '-'):
  outputFile = open(sys.argv[3], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['Owner', 'teamDriveId', 'teamDriveName', 'driveFileId', 'driveFileTitle',
                                        'permissionId', 'role', 'type', 'emailAddress', 'domain', 'deleted'],
                           lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

teamDriveNames = {}
inputFile = open(sys.argv[2], 'r', encoding='utf-8')
for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  teamDriveNames[row['id']] = row['name']
inputFile.close()

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin

for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  for k, v in iter(row.items()):
    mg = PERMISSIONS_N_TYPE.match(k)
    if mg and v:
      permissions_N = mg.group(1)
      if NON_INHERITED_ACLS_ONLY and str(row.get(f'permissions.{permissions_N}.permissionDetails.0.inherited', False)) == 'True':
        continue
      if v == 'domain':
        emailAddress = ''
        domain = row[f'permissions.{permissions_N}.domain']
      elif v in ['user', 'group']:
        emailAddress = row[f'permissions.{permissions_N}.emailAddress']
        domain = emailAddress[emailAddress.find('@')+1:]
      else: #anyone
        emailAddress = ''
        domain = ''
      outputCSV.writerow({'Owner': row['Owner'],
                          'teamDriveId': row['driveId'],
                          'teamDriveName': teamDriveNames.get(row['driveId'], row['driveId']),
                          'driveFileId': row['id'],
                          'driveFileTitle': row.get(FILE_NAME, row.get(ALT_FILE_NAME, 'Unknown')),
                          'permissionId': f'id:{row[f"permissions.{permissions_N}.id"]}',
                          'role': row[f'permissions.{permissions_N}.role'],
                          'type': v,
                          'emailAddress': emailAddress,
                          'domain': domain,
                          'deleted': row.get(f'permissions.{permissions_N}.deleted', 'False')})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
