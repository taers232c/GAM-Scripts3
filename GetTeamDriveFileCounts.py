#!/usr/bin/env python3
"""
# Purpose: Get file counts for Team Drives
# Note: This script requires Advanced GAM with Team Drive support:
#	https://github.com/taers232c/GAMADV-XTD, https://github.com/taers232c/GAMADV-XTD3
# Customize: DOMAIN_LIST
# Usage:
# 1: If you want to include all Team Drives, do this step and then skip to step 4, otherwise start at step 2.
#  $ gam redirect csv ./TeamDrives.csv print teamdrives fields id,name
# 2: If want Team Drives for a specific set of organizers, replace <UserTypeEntity> with your user selection in the command below
#  $ gam redirect csv ./AllTeamDrives.csv <UserTypeEntity> print teamdrives role organizer fields id,name
# 3: Delete duplicate Team Drives (some may have multiple organizers). Make sure that ID_FIELD = 'id' in DeleteDuplicateRows.py
#  $ python DeleteDuplicateRows.py ./AllTeamDrives.csv ./TeamDrives.csv
# 4: Get ACLs for all Team Drives
#  $ gam redirect csv ./TeamDriveACLs.csv multiprocess csv TeamDrives.csv gam print drivefileacls ~id
# 5: From that list of ACLs, output a CSV file with headers "id,name,organizer"
#    that shows an organizer/fileOrganizer for each Team Drive
#  $ python GetTeamDriveFileCounts.py TeamDriveACLs.csv TeamDrives.csv TeamDriveOrganizers.csv
# 6: From that list of organizers, get the file counts for all Team Drives that have an organizer (matchfield organizer "^.+$")
#  $ gam redirect csv ./TeamDriveFileCounts.csv multiprocess csv TeamDriveOrganizers.csv matchfield organizer "^.+$"  gam user ~organizer print filecounts select teamdriveid ~id
# 7: You can identify all Team Drives without an organizer
#  $ gam csv TeamDriveOrganizers.csv skipfield organizer "^.+$" gam info teamdrive teamdriveid ~id
"""

import csv
import re
import sys

# If you want to limit organizers to a specific list of domains, use the list below, e.g., DOMAIN_LIST = ['domain.com',] DOMAIN_LIST = ['domain1.com', 'domain2.com',]
DOMAIN_LIST = []

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

PERMISSIONS_N_ROLE = re.compile(r"permissions.(\d+).role")

if (len(sys.argv) > 3) and (sys.argv[3] != '-'):
  outputFile = open(sys.argv[3], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['id', 'name', u'organizer'], lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
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
  organizer = ''
  for k, v in iter(row.items()):
    mg = PERMISSIONS_N_ROLE.match(k)
    if mg and v in ['organizer', 'fileOrganizer']:
      permissions_N = mg.group(1)
      if row['permissions.{0}.type'.format(permissions_N)] != u'user':
        continue
      emailAddress = row['permissions.{0}.emailAddress'.format(permissions_N)]
      if DOMAIN_LIST:
        domain = emailAddress[emailAddress.find(u'@')+1:]
        if domain not in DOMAIN_LIST:
          continue
      organizer = emailAddress
      break
  outputCSV.writerow({'id': row['id'],
                      'name': teamDriveNames.get(row['id'], row['id']),
                      'organizer': organizer})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
