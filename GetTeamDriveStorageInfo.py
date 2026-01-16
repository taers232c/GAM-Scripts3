#!/usr/bin/env python3
"""
# Purpose: Get storage info for Team Drives
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Get a list of Team Drives/organizers
#  $ gam redirect csv ./TeamDriveOrganizers.csv print shareddriveorganizers includefileorganizers
# 2: Get Team Drive files
#  $ gam config csv_input_row_filter "organizers:regex:^.+$" redirect csv ./TeamDriveFileCountsSize.csv multiprocess csv ./TeamDriveOrganizers.csv gam user "~organizers" print filecounts select teamdriveid "~id" showsize
# 3: Get Team Drive storage info
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

MAX_FILES_FOLDERS = 500000

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
