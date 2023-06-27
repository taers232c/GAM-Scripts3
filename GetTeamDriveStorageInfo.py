#!/usr/bin/env python3
"""
# Purpose: Get storage info for Team Drives
# Note: This script requires Advanced GAM:
#	https://github.com/taers232c/GAMADV-XTD3
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
#  $ gam redirect csv ./TeamDriveACLs.csv multiprocess csv ./TeamDrives.csv gam print drivefileacls "~id" fields emailaddress,role,type
# 5: From that list of ACLs, output a CSV file with headers "id,name,organizers"
#    that shows the organizers for each Team Drive
# 6: Customize GetTeamDriveOrganizers.py
#    Set DOMAIN_LIST as desired
#    Set ONE_ORGANIZER = True
#    Set SHOW_GROUP_ORGANIZERS = False
#    Set SHOW_USER_ORGANIZERS = True
#  $ python3 GetTeamDriveOrganizers.py TeamDriveACLs.csv TeamDrives.csv TeamDriveOrganizers.csv
# 7: Get Team Drive files
#  $ gam config csv_input_row_filter "organizers:regex:^.+$" redirect csv ./TeamDriveFileCountsSize.csv multiprocess csv ./TeamDriveOrganizers.csv user "~organizers" print filecounts select teamdriveid "~id" showsize
# 8: Get Team Drive storage info
#  $ python3 GetTeamDriveStorageInfo.py TeamDriveFileCountsSize.csv TeamDriveStorageInfo.csv

"""

import csv
import sys

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

ONE_KILO_BYTES = 1024
ONE_MEGA_BYTES = ONE_KILO_BYTES*ONE_KILO_BYTES
ONE_GIGA_BYTES = ONE_KILO_BYTES*ONE_MEGA_BYTES
ONE_TERA_BYTES = ONE_KILO_BYTES*ONE_GIGA_BYTES

MAX_FILES_FOLDERS = 400000

def formatSize(size):
  if size == 0:
    return '0 KB'
  if size < ONE_KILO_BYTES:
    return '1 KB'
  if size < ONE_MEGA_BYTES:
    return f'{size/ONE_KILO_BYTES:.2f} KB'
  if size < ONE_GIGA_BYTES:
    return f'{size/ONE_MEGA_BYTES:.2f} MB'
  if size < ONE_TERA_BYTES:
    return f'{size/ONE_GIGA_BYTES:.2f} GB'
  return f'{size/ONE_TERA_BYTES:.2f} TB'

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['id', 'name', 'size', 'Storage used', 'count', 'Item cap'], lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin

teamDriveInfo = {}
for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  outputCSV.writerow({'id': row['id'], 'name': row['name'], 'size': row['Size'], 'Storage used': formatSize(int(row['Size'])),
                      'count': row['Total'], 'Item cap': f"{int(row['Total'])/MAX_FILES_FOLDERS:.2%}"})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
