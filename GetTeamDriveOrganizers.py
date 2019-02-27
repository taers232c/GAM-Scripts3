#!/usr/bin/env python3
"""
# Purpose: Get organizers for Team Drives
# Note: This script requires Advanced GAM with Team Drive support:
#	https://github.com/taers232c/GAMADV-XTD, https://github.com/taers232c/GAMADV-XTD3
# Customize: DOMAIN_LIST, ONE_ORGANIZER, SHOW_GROUP_ORGANIZERS, SHOW_USER_ORGANIZERS
# Usage:
# 1: If you want to include all Team Drives, do this step and then skip to step 4, otherwise start at step 2.
#  $ gam redirect csv ./TeamDrives.csv print teamdrives fields id,name
# 2: If want Team Drives for a specific set of organizers, replace <UserTypeEntity> with your user selection in the command below
#  $ gam redirect csv ./AllTeamDrives.csv <UserTypeEntity> print teamdrives role organizer fields id,name
# 3: Delete duplicate Team Drives (some may have multiple organizers). Make sure that ID_FIELD = 'id' in DeleteDuplicateRows.py
#  $ python DeleteDuplicateRows.py ./AllTeamDrives.csv ./TeamDrives.csv
# 4: Get ACLs for all Team Drives
#  $ gam redirect csv ./TeamDriveACLs.csv multiprocess csv TeamDrives.csv gam print drivefileacls ~id
# 5: From that list of ACLs, output a CSV file with headers "id,name,organizers"
#    that shows the organizers for each Team Drive
#  $ python GetTeamDriveOrganizers.py TeamDriveACLs.csv TeamDrives.csv TeamDriveOrganizers.csv
"""

import csv
import re
import sys

# If you want to limit organizers to a specific list of domains, use the list below, e.g., DOMAIN_LIST = ['domain.com',] DOMAIN_LIST = ['domain1.com', 'domain2.com',]
DOMAIN_LIST = []

ONE_ORGANIZER = False # False - show all organizers, True - show one organizer

SHOW_GROUP_ORGANIZERS = True # False - don't show group organizers, True - show group organizers
SHOW_USER_ORGANIZERS = True # False - don't show user organizers, True - show user organizers

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

PERMISSIONS_N_ROLE = re.compile(r"permissions.(\d+).role")

if (len(sys.argv) > 3) and (sys.argv[3] != '-'):
  outputFile = open(sys.argv[3], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['id', 'name', u'organizers'], lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
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
  for k, v in iter(row.items()):
    mg = PERMISSIONS_N_ROLE.match(k)
    if mg and v == 'organizer':
      permissions_N = mg.group(1)
      orgtype = row['permissions.{0}.type'.format(permissions_N)]
      if (orgtype == u'user' and not SHOW_USER_ORGANIZERS) or (orgtype == u'group' and not SHOW_GROUP_ORGANIZERS):
        continue
      emailAddress = row['permissions.{0}.emailAddress'.format(permissions_N)]
      if DOMAIN_LIST:
        domain = emailAddress[emailAddress.find(u'@')+1:]
        if domain not in DOMAIN_LIST:
          continue
      organizers.append(emailAddress)
      if ONE_ORGANIZER:
        break
  outputCSV.writerow({'id': row['id'],
                      'name': teamDriveNames.get(row['id'], row['id']),
                      'organizers': ' '.join(organizers)})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
