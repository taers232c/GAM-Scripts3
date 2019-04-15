#!/usr/bin/env python3
"""
# Purpose: Get latest modifiedTime for Team Drives
# Note: This script requires Advanced GAM with Team Drive support:
#	https://github.com/taers232c/GAMADV-XTD, https://github.com/taers232c/GAMADV-XTD3
# Customize: SORT_HEADER
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
#    that shows the organizers for each Team Drive.
#    Set the following items in GetTeamDriveOrganizers.py
#    ONE_ORGANIZER = True
#    SHOW_GROUP_ORGANIZERS = False
#    SHOW_USER_ORGANIZERS = True
#  $ python GetTeamDriveOrganizers.py TeamDriveACLs.csv TeamDrives.csv TeamDriveOrganizers.csv
# 6: Using the list of Team Drives and organizers, get a list of file ids and names sorted by modifiedTime descending
#  $ gam redirect csv ./TeamDriveFileList.csv multiprocess csv TeamDriveOrganizers.csv gam user ~organizers print filelist select teamdriveid ~id query "mimeType != 'application/vnd.google-apps.folder'" fields teamDriveId,id,name,modifiedtime orderby modifiedtime descending
# 7: From that list of files, output a CSV file with headers "id,name,driveFileId,driveFileName,modifiedTime'
#    that show the most recently modified file for each Team Drive
#  $ python GetTeamDriveLastModified.py TeamDriveFileList.csv TeamDrives.csv TeamDriveLastModified.csv
"""

import csv
import sys

SORT_HEADER = 'name' # 'name' - Team Drive name, 'id' - Team Drive ID, 'modifiedTime' - file modifiedTime

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

if (len(sys.argv) > 3) and (sys.argv[3] != '-'):
  outputFile = open(sys.argv[3], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['id', 'name', 'driveFileId', 'driveFileName', u'modifiedTime'], lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
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

teamDriveProcessed = set()
csvRows = []
for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  teamDriveId = row['teamDriveId']
  if teamDriveId not in teamDriveProcessed:
    teamDriveProcessed.add(teamDriveId)
    csvRows.append({'id': teamDriveId,
                    'name': teamDriveNames.get(teamDriveId, teamDriveId),
                    'driveFileId': row['id'],
                    'driveFileName': row['name'],
                    'modifiedTime': row['modifiedTime']})
csvRows.sort(key=lambda k: k[SORT_HEADER])
outputCSV.writerows(csvRows)

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
