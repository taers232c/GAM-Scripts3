#!/usr/bin/env python3
"""
# Purpose: Get file counts/total size for Team Drives
# Note: This script requires Advanced GAM:
#	https://github.com/taers232c/GAMADV-XTD3
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: If you want to include all Team Drives, do this step and then skip to step 4, otherwise start at step 2.
#  $ gam redirect csv ./TeamDrives.csv print teamdrives fields id,name
# 2: If want Team Drives for a specific set of organizers, replace <UserTypeEntity> with your user selection in the command below
#  $ gam redirect csv ./AllTeamDrives.csv <UserTypeEntity> print teamdrives role organizer fields id,name
# 3: Delete duplicate Team Drives (some may have multiple organizers). Make sure that ID_FIELD = 'id' in DeleteDuplicateRows.py
#  $ python3 DeleteDuplicateRows.py ./AllTeamDrives.csv ./TeamDrives.csv
# 4: Get ACLs for all Team Drives
#  $ gam redirect csv ./TeamDriveACLs.csv multiprocess csv TeamDrives.csv gam print drivefileacls ~id fields emailaddress,role,type
# 5: From that list of ACLs, output a CSV file with headers "id,name,organizers"
#    that shows the organizers for each Team Drive
# 6: Customize GetTeamDriveOrganizers.py
#    Set DOMAIN_LIST as desired
#    Set ONE_ORGANIZER = True
#    Set SHOW_GROUP_ORGANIZERS = False
#    Set SHOW_USER_ORGANIZERS = True
#  $ python3 GetTeamDriveOrganizers.py TeamDriveACLs.csv TeamDrives.csv TeamDriveOrganizers.csv
# 7: Get Team Drive files
#  $ gam redirect csv ./TeamDriveFiles.csv multiprocess csv TeamDriveOrganizers.csv matchfield organizers "^.+$" gam user ~organizers print filelist select teamdriveid ~id fields id,name,driveid,size
# 8: Get Team Drive counts/size info
#  $ python3 GetTeamDriveCountsSize.py TeamDriveFiles.csv TeamDrives.csv TeamDriveCountsSize.csv

"""

import csv
import sys

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

if (len(sys.argv) > 3) and (sys.argv[3] != '-'):
  outputFile = open(sys.argv[3], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['id', 'name', 'count', 'size'], lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
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

teamDriveInfo = {}
for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  driveId = row.get('driveId')
  if not driveId:
    continue
  if driveId not in teamDriveNames:
    teamDriveNames[driveId] = driveId
  if driveId not in teamDriveInfo:
    teamDriveInfo[driveId] = {'name': teamDriveNames[driveId], 'count': 0, 'size': 0}
  teamDriveInfo[driveId]['count'] += 1
  size = row.get('size', '0')
  if size:
    teamDriveInfo[driveId]['size'] += int(size)

for k, v in iter(teamDriveInfo.items()):
  outputCSV.writerow({'id': k, 'name': v['name'], 'count': v['count'], 'size': v['size']})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
