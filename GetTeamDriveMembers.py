#!/usr/bin/env python3
"""
# Purpose: Get members for Team Drives
# Note: This script requires Advanced GAM:
#	https://github.com/taers232c/GAMADV-XTD3
# Customize: DELIMITER, DOMAIN_LIST, INCLUDE_TYPES
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
#  $ gam redirect csv ./TeamDriveACLs.csv multiprocess csv ./TeamDrives.csv gam print drivefileacls "~id" fields id,domain,emailaddress,role,type,deleted
# 5: From that list of ACLs, output a CSV file with headers "id,name,organizers,members"
#    that shows the organizers for each Team Drive
#  $ python3 GetTeamDriveMembers.py TeamDriveACLs.csv TeamDrives.csv TeamDriveMembers.csv
"""

import csv
import re
import sys

DELIMITER = ' ' # character that separates list members

# If you want to limit members to a specific list of domains, use the list below, e.g., DOMAIN_LIST = ['domain.com',] DOMAIN_LIST = ['domain1.com', 'domain2.com',]
DOMAIN_LIST = []

INCLUDE_TYPES = {
  'user': True, # False - don't show user members, True - show user members
  'group': True, # False - don't show group members, True - show group members
  }

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

PERMISSIONS_N_ROLE = re.compile(r"permissions.(\d+).role")

if (len(sys.argv) > 3) and (sys.argv[3] != '-'):
  outputFile = open(sys.argv[3], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['id', 'name', 'organizers', 'members'], lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
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
  organizers = []
  members = []
  for k, v in iter(row.items()):
    mg = PERMISSIONS_N_ROLE.match(k)
    if mg and v:
      roleList = organizers if v == 'organizer' else members
      permissions_N = mg.group(1)
      if row.get(f'permissions.{permissions_N}.deleted') == 'True':
        continue
      if not INCLUDE_TYPES[row[f'permissions.{permissions_N}.type']]:
        continue
      member = row[f'permissions.{permissions_N}.emailAddress']
      if DOMAIN_LIST and member[member.find('@')+1:] not in DOMAIN_LIST:
        continue
      roleList.append(member)
  outputCSV.writerow({'id': row['id'],
                      'name': teamDriveNames.get(row['id'], row['id']),
                      'organizers': DELIMITER.join(organizers),
                      'members': DELIMITER.join(members)})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
