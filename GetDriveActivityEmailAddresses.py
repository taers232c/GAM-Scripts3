#!/usr/bin/env python3
"""
# Purpose: Get email addresses for users identified by permissionId in gam print driveactivity when the v2 option is not used
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Get permissionId from Drive Settings. Substitute for all users if applicable.
#  $ Example: gam config auto_batch_min 1 redirect csv ./DriveSettings.csv multiprocess all users print drivesettings fields permissionid
# 2: Generate drive activity
#  $ Example: gam config auto_batch_min 1 redirect csv ./DriveActivity.csv multiprocess <UserTypeEntity> print driveactivity  ...
# 3: From DriveSettings.csv and DriveActivity.csv generate DriveActivityEmail.csv with the additional column user.emailAddress
#  $ python3 GetDriveActivityEmailAddresses.py DriveSettings.csv DriveActivity.csv DriveActivityEmail.csv
"""

import csv
import sys

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

USER_PERMISSIONID = 'user.permissionId'
USER_EMAILADDRESS = 'user.emailAddress'

permissionIdEmailMap = {}
inputFile = open(sys.argv[1], 'r', encoding='utf-8')
for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  permissionIdEmailMap[row['permissionId']] = row['email']
inputFile.close()

inputFile = open(sys.argv[2], 'r', encoding='utf-8')
inputCSV = csv.DictReader(inputFile, quotechar=QUOTE_CHAR)
fieldnames = inputCSV.fieldnames[:]
fieldnames.insert(1, USER_EMAILADDRESS)

outputFile = open(sys.argv[3], 'w', encoding='utf-8', newline='')
outputCSV = csv.DictWriter(outputFile, fieldnames, lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

for row in inputCSV:
  permissionId = row[USER_PERMISSIONID]
  if permissionId not in permissionIdEmailMap:
    permissionIdEmailMap[permissionId] = 'Unknown'
  row[USER_EMAILADDRESS] = permissionIdEmailMap[permissionId]
  outputCSV.writerow(row)

inputFile.close()
outputFile.close()
