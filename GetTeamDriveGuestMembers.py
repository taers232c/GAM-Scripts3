#!/usr/bin/env python3
"""
# Purpose: Show guest members for files on Team Drives.
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# For all Team Drives, start at step 1; For Team Drives selected by user/group/OU, start at step 7
# All Team Drives
# 1: Get all Team Drives.
#  $ gam redirect csv ./TeamDrives.csv print teamdrives fields id,name
# 2: Get ACLs for all Team Drives
#  $ gam redirect csv ./TeamDriveACLs.csv multiprocess csv ./TeamDrives.csv gam print drivefileacls "~id" fields domain,emailaddress,role,type
# 3: Customize GetTeamDriveOrganizers.py for this task:
#    Set DOMAIN_LIST as required
#    Set ONE_ORGANIZER = True
#    Set SHOW_GROUP_ORGANIZERS = False
#    Set SHOW_USER_ORGANIZERS = True
# 4: From that list of ACLs, output a CSV file with headers "id,name,organizers"
#    that shows the organizers for each Team Drive
#  $ python3 GetTeamDriveOrganizers.py TeamDriveACLs.csv TeamDrives.csv TeamDriveOrganizers.csv
# 5: Get ACLs for all team drive files
#  $ gam config csv_input_row_filter "organizers:regex:^.+$" redirect csv ./TeamDriveFileACLs.csv multiprocess csv ./TeamDriveOrganizers.csv gam user "~organizers" print filelist select teamdriveid "~id" fields teamdriveid,id,name,permissions
#    You can add: config csv_output_row_filter "permissions.*.permissionDetails.0.permissionType:regex:file" between gam and redirect to have gam do some pre-filtering.
# 6: Go to step 11
# Selected Team Drives
# 7: If you want Team Drives for a specific set of organizers, replace <UserTypeEntity> with your user selection in the command below
#  $ gam redirect csv ./AllTeamDrives.csv <UserTypeEntity> print teamdrives role organizer fields id,name
# 8: Customize DeleteDuplicateRows.py for this task:
#    Set ID_FIELD = 'id'
# 9: Delete duplicate Team Drives (some may have multiple organizers).
#  $ python3 DeleteDuplicateRows.py ./AllTeamDrives.csv ./TeamDrives.csv
# 10: Get ACLs for all team drive files
#  $ gam redirect csv ./TeamDriveFileACLs.csv multiprocess csv ./TeamDrives.csv gam user "~User" print filelist select teamdriveid "~id" fields teamdriveid,id,name,permissions
#    You can add: config csv_output_row_filter "permissions.*.permissionDetails.0.permissionType:regex:file" between gam and redirect to have gam do some pre-filtering.
# Common code
# 11: From that list of ACLs, output a CSV file with headers "Owner,teamDriveId,teamDriveName,driveFileId,driveFileName,permissionId,role,type,emailAddress,domain"
#    that lists the driveFileIds and permissionIds for all ACLs referencing domains/groups/users that are not members of the Team Drive
#  $ python3 GetTeamDriveGuestMembers.py TeamDriveACLs.csv TeamDrives.csv TeamDriveFileACLs.csv TeamDriveGuestMembers.csv
"""

import csv
import re
import sys

FILE_NAME = 'name'
ALT_FILE_NAME = 'title'

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

PERMISSIONS_N_TYPE = re.compile(r"permissions.(\d+).type")

# TeamDriveGuestMembers.csv
outputFile = open(sys.argv[4], 'w', encoding='utf-8', newline='')
outputCSV = csv.DictWriter(outputFile, ['teamDriveId', 'teamDriveName', 'driveFileId', 'driveFileName',
                                        'permissionId', 'role', 'type', 'emailAddress', 'domain'],
                           lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

# TeamDrives.csv
teamDrives = {}
inputFile = open(sys.argv[2], 'r', encoding='utf-8')
for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  teamDrives[row['id']] = {'name': row['name'], 'user': set(), 'group': set(), 'domain': set()}
inputFile.close()

# TeamDriveACLs.csv
inputFile = open(sys.argv[1], 'r', encoding='utf-8')
for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  driveId = row['id']
  if driveId not in teamDrives:
    teamDrives[driveId] = {'name': driveId, 'user': set(), 'group': set(), 'domain': set()}
  teamDrive = teamDrives[driveId]
  for k, v in iter(row.items()):
    mg = PERMISSIONS_N_TYPE.match(k)
    if mg and v:
      permissions_N = mg.group(1)
      if v == 'domain':
        teamDrive[v].add(row[f'permissions.{permissions_N}.domain'].lower())
      elif v in ['user', 'group']:
        teamDrive[v].add(row[f'permissions.{permissions_N}.emailAddress'].lower())
inputFile.close()

# TeamDriveFileACLs.csv
inputFile = open(sys.argv[3], 'r', encoding='utf-8')
for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  driveId = row['driveId']
  if driveId not in teamDrives:
    teamDrives[driveId] = {'name': driveId, 'user': set(), 'group': set(), 'domain': set()}
  teamDrive = teamDrives[driveId]
  for k, v in iter(row.items()):
    mg = PERMISSIONS_N_TYPE.match(k)
    if mg and v:
      permissions_N = mg.group(1)
      if v == 'domain':
        domain = row[f'permissions.{permissions_N}.domain'].lower()
        if domain in teamDrive[v]:
          continue
        emailAddress = ''
      elif v in ['user', 'group']:
        if row.get(f'permissions.{permissions_N}.deleted') == 'True':
          continue
        emailAddress = row[f'permissions.{permissions_N}.emailAddress'].lower()
        if emailAddress in teamDrive[v]:
          continue
        domain = emailAddress[emailAddress.find('@')+1:]
      else: #anyone
        continue
      outputCSV.writerow({'teamDriveId': driveId,
                          'teamDriveName': teamDrive['name'],
                          'driveFileId': row['id'],
                          'driveFileName': row.get(FILE_NAME, row.get(ALT_FILE_NAME, 'Unknown')),
                          'permissionId': f'id:{row[f"permissions.{permissions_N}.id"]}',
                          'role': row[f'permissions.{permissions_N}.role'],
                          'type': v,
                          'emailAddress': emailAddress,
                          'domain': domain})

inputFile.close()
outputFile.close()
