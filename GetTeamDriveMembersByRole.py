#!/usr/bin/env python3
"""
# Purpose: Get members by role for Team Drives
# Customize: DELIMITER, DOMAIN_LIST, INCLUDE_TYPES, USE_GUI_ROLES
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: If you want to include all Team Drives, do this step and then skip to step 4, otherwise start at step 2.
#  $ gam redirect csv ./TeamDrives.csv print teamdrives fields id,name
# 2: If you want Team Drives for a specific set of organizers, replace <UserTypeEntity> with your user selection in the command below
#  $ gam redirect csv ./AllTeamDrives.csv <UserTypeEntity> print teamdrives fields id,name
# 3: Delete duplicate Team Drives (some may have multiple organizers). Make sure that ID_FIELD = 'id' in DeleteDuplicateRows.py
#  $ python3 DeleteDuplicateRows.py ./AllTeamDrives.csv ./TeamDrives.csv
# 4: Get ACLs for all Team Drives
#  $ gam redirect csv ./SharedDriveACLs.csv print shareddriveacls oneitemperrow
# 5: From that list of ACLs, output a CSV file with headers that show the members by role for each Team Drive
#    USE_GUI_ROLES = False "id,name,createdTime,organizer,fileOrganizer,writer,commanter,reader"
#    USE_GUI_ROLES = True  "id,name,createdTime,Manager,Content manager,Contributor,Commanter,Viewer"
#  $ python3 GetTeamDriveMembersByRole.py TeamDriveACLs.csv TeamDriveMembers.csv
"""

import csv
import sys

DELIMITER = ' ' # character that separates list members

# If you want to limit organizers/members to a specific list of domains, use the list below, e.g., DOMAIN_LIST = ['domain.com',] DOMAIN_LIST = ['domain1.com', 'domain2.com',]
DOMAIN_LIST = []

INCLUDE_TYPES = {
  'user': True, # False - don't show user members, True - show user members
  'group': True, # False - don't show group members, True - show group members
  }

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

SHAREDDRIVE_API_GUI_ROLES_MAP = {
  'organizer': 'Manager',
  'fileOrganizer': 'Content manager',
  'writer': 'Contributor',
  'commenter': 'Commenter',
  'reader': 'Viewer',
  }

USE_GUI_ROLES = False # False - use API roles, True - use GUI roles

outputHeaders = ['id', 'name', 'createdTime']
if not USE_GUI_ROLES:
  for apirole in SHAREDDRIVE_API_GUI_ROLES_MAP.keys():
    outputHeaders.append(apirole)
else:
  for guirole in SHAREDDRIVE_API_GUI_ROLES_MAP.values():
    outputHeaders.append(guirole)
outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
outputCSV = csv.DictWriter(outputFile, outputHeaders, lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

teamDrives = {}
inputFile = open(sys.argv[1], 'r', encoding='utf-8')
for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  driveId = row['id']
  if id not in teamDrives:
    teamDrives[driveId] = {'id': driveId, 'name': row['name'], 'createdTime': row['createdTime'],
                           'organizer': [], 'fileOrganizer': [], 'writer': [], 'commenter': [], 'reader': []}
  if row.get('permission.deleted') == 'True':
    continue
  if not INCLUDE_TYPES[row['permission.type']]:
    continue
  member = row['permission.emailAddress']
  if DOMAIN_LIST and member[member.find('@')+1:] not in DOMAIN_LIST:
    continue
  teamDrives[id][row['permission.role']].append(member)
for teamDrive in teamDrives.values():
  row = {'id': teamDrive['id'], 'name': teamDrive['name'], 'createdTime': teamDrive['createdTime']}
  if not USE_GUI_ROLES:
    for apirole in SHAREDDRIVE_API_GUI_ROLES_MAP.keys():
      row[apirole] = DELIMITER.join(teamDrive[apirole])
  else:
    for apirole, guirole in SHAREDDRIVE_API_GUI_ROLES_MAP.items():
      row[guirole] = DELIMITER.join(teamDrive[apirole])
  outputCSV.writerow(row)

inputFile.close()
outputFile.close()
