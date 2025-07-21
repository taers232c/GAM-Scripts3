#!/usr/bin/env python3
"""
# Purpose: Get organizers for Team Drives
# Customize: DELIMITER, DOMAIN_LIST, INCLUDE_TYPES, ONE_ORGANIZER, SHOW_NO_ORGANIZER_DRIVES, INCLUDE_FILE_ORGANIZERS
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: If you want to include all Team Drives, do this step and then skip to step 4, otherwise start at step 2.
#  $ gam redirect csv ./TeamDrives.csv print teamdrives fields id,name
# 2: If you want Team Drives for a specific set of organizers, replace <UserTypeEntity> with your user selection in the command below
#  $ gam redirect csv ./AllTeamDrives.csv <UserTypeEntity> print teamdrives role organizer fields id,name
# 3: Delete duplicate Team Drives (some may have multiple organizers). Make sure that ID_FIELD = 'id' in DeleteDuplicateRows.py
#  $ python3 DeleteDuplicateRows.py ./AllTeamDrives.csv ./TeamDrives.csv
# 4: Get ACLs for all Team Drives
#  $ gam redirect csv ./TeamDriveACLs.csv multiprocess csv ./TeamDrives.csv gam print drivefileacls "~id" fields id,emailaddress,role,type,deleted
# 5: From that list of ACLs, output a CSV file with headers "id,name,organizers"
#    that shows the organizers for each Team Drive
#  $ python3 GetTeamDriveOrganizers.py TeamDriveACLs.csv TeamDrives.csv TeamDriveOrganizers.csv
"""

import csv
import re
import sys

DELIMITER = ' ' # character that separates list members

# If you want to limit organizers to a specific list of domains, use the list below, e.g., DOMAIN_LIST = ['domain.com',] DOMAIN_LIST = ['domain1.com', 'domain2.com',]
DOMAIN_LIST = ['domain.com']

INCLUDE_TYPES = {
  'user': True, # False - don't show user organizers, True - show user organizers
  'group': True, # False - don't show group organizers, True - show group organizers
  }

ONE_ORGANIZER = True # False - show all organizers, True - show one organizer
SHOW_NO_ORGANIZER_DRIVES = True # False - don't show drives with no organizers, True - show drives with no organizers
# If you're using the output to just get file lists and won't be processing ACLs, fileOrganizers will work; otherwise you only want organizers,
INCLUDE_FILE_ORGANIZERS = False # False - do not include file organizers, True - include file organizers

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

PERMISSIONS_N_ROLE = re.compile(r"permissions.(\d+).role")

if (len(sys.argv) > 3) and (sys.argv[3] != '-'):
  outputFile = open(sys.argv[3], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['id', 'name', 'organizers'], lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
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

roles = {'organizer'}
if INCLUDE_FILE_ORGANIZERS:
  roles.add('fileOrganizer')
for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  organizers = []
  for k, v in iter(row.items()):
    mg = PERMISSIONS_N_ROLE.match(k)
    if mg and v in roles:
      permissions_N = mg.group(1)
      if row.get(f'permissions.{permissions_N}.deleted') == 'True':
        continue
      if not INCLUDE_TYPES[row[f'permissions.{permissions_N}.type']]:
        continue
      member = row[f'permissions.{permissions_N}.emailAddress']
      if DOMAIN_LIST and member[member.find('@')+1:] not in DOMAIN_LIST:
        continue
      organizers.append(member)
      if ONE_ORGANIZER:
        break
  if organizers or SHOW_NO_ORGANIZER_DRIVES:
    outputCSV.writerow({'id': row['id'],
                        'name': teamDriveNames.get(row['id'], row['id']),
                        'organizers': DELIMITER.join(organizers)})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
