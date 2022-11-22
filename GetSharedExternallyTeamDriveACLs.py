#!/usr/bin/env python3
"""
# Purpose: For a Google Drive User(s), show all drive file ACLs for Team Drive files shared outside of a list of specified domains
#          You specify a list of domains, DOMAIN_LIST, and indicate whether this list is exclusive/inclusive
#          EXCLUSIVE_DOMAINS = True: exclude domains in DOMAIN_LIST from the output
#          EXCLUSIVE_DOMAINS = False: include domains in DOMAIN_LIST in the output
#          You can include/exclude shares to anyone in the ouput
#          INCLUDE_ANYONE = True: include shares to anyone in the output
#          INCLUDE_ANYONE = False: exclude shares to anyone from the output
# Note: This script requires Advanced GAM:
#	https://github.com/taers232c/GAMADV-XTD3
# Customize: Set DOMAIN_LIST, EXCLUSIVE_DOMAINS, INCLUDE_ANYONE, NON_INHERITED_ACLS_ONLY
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# For all Team Drives, start at step 1; For Team Drives selected by user/group/OU, start at step 7
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
#  $ gam redirect csv ./filelistperms.csv multiprocess csv ./TeamDriveOrganizers.csv gam user "~organizers" print filelist select teamdriveid "~id" fields teamdriveid,id,name,permissions,mimetype
# 6: Go to step 11
# Selected Team Drives
# 7: If you want Team Drives for a specific set of organizers, replace <UserTypeEntity> with your user selection in the command below
#  $ gam redirect csv ./AllTeamDrives.csv <UserTypeEntity> print teamdrives role organizer fields id,name
# 8: Customize DeleteDuplicateRows.py for this task:
#    Set ID_FIELD = 'id'
# 9: Delete duplicate Team Drives (some may have multiple organizers).
#  $ python3 DeleteDuplicateRows.py ./AllTeamDrives.csv ./TeamDrives.csv
# 10: Get ACLs for all team drive files
#  $ gam redirect csv ./filelistperms.csv multiprocess csv ./TeamDrives.csv gam user "~User" print filelist select teamdriveid "~id" fields teamdriveid,id,name,permissions,mimetype
# Common code
# 11: From that list of ACLs, output a CSV file with headers "Owner,teamDriveId,teamDriveName,driveFileId,driveFileTitle,permissionId,role,type,emailAddress,domain"
#    that lists the driveFileIds and permissionIds for all ACLs except those from the specified domains.
#    (n.b., teamDriveId, teamDriveName, driveFileTitle, role, type, emailAddress and domain are not used in the next step, they are included for documentation purposes)
#  $ python3 GetSharedExternallyTeamDriveACLs.py filelistperms.csv TeamDrives.csv  deleteperms.csv
# 12: Inspect deleteperms.csv, verify that it makes sense and then proceed
# 13: If desired, delete the ACLs
#  $ gam csv ./deleteperms.csv gam user "~Owner" delete drivefileacl "~driveFileId" "~permissionId"
"""

import csv
import re
import sys

FILE_NAME = 'name'
ALT_FILE_NAME = 'title'

# Substitute your domain(s) in the list below, e.g., DOMAIN_LIST = ['domain.com',] DOMAIN_LIST = ['domain1.com', 'domain2.com',]
DOMAIN_LIST = ['domain.com',]
# Indicate whether the list is exclusive or inclusive
# EXCLUSIVE_DOMAINS = True: You're interested only in domains not in DOMAIN_LIST which would typically be your internal domains
# EXCLUSIVE_DOMAINS = False: You're interested only in domains in DOMAIN_LIST which would typically be external domains
EXCLUSIVE_DOMAINS = True
# Indicate whether shares to anyone should be included
INCLUDE_ANYONE = True

# Specify whether only non-inherited ACLs should be output; inherited ACLs can't be deleted
NON_INHERITED_ACLS_ONLY = True

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

PERMISSIONS_N_TYPE = re.compile(r"permissions.(\d+).type")

if (len(sys.argv) > 3) and (sys.argv[3] != '-'):
  outputFile = open(sys.argv[3], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['Owner', 'teamDriveId', 'teamDriveName', 'driveFileId', 'driveFileTitle', 'mimeType',
                                        'permissionId', 'role', 'type', 'emailAddress', 'domain'],
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
        if row.get(f'permissions.{permissions_N}.deleted') == 'True':
          continue
        emailAddress = row[f'permissions.{permissions_N}.emailAddress']
        domain = emailAddress[emailAddress.find('@')+1:]
      else: #anyone
        if not INCLUDE_ANYONE:
          continue
        emailAddress = ''
        domain = ''
      if ((row[f'permissions.{permissions_N}.role'] != 'organizer') and
          ((v == 'anyone') or # Can only be true is INCLUDE_ANYONE = True
           (EXCLUSIVE_DOMAINS and domain not in DOMAIN_LIST) or
           (not EXCLUSIVE_DOMAINS and domain in DOMAIN_LIST))):
        outputCSV.writerow({'Owner': row['Owner'],
                            'teamDriveId': row['driveId'],
                            'teamDriveName': teamDriveNames.get(row['driveId'], row['driveId']),
                            'driveFileId': row['id'],
                            'driveFileTitle': row.get(FILE_NAME, row.get(ALT_FILE_NAME, 'Unknown')),
                            'mimeType': row['mimeType'],
                            'permissionId': f'id:{row[f"permissions.{permissions_N}.id"]}',
                            'role': row[f'permissions.{permissions_N}.role'],
                            'type': v,
                            'emailAddress': emailAddress,
                            'domain': domain})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
