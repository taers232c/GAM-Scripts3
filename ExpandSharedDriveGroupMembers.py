#!/usr/bin/env python3
"""
# Purpose: Read a CSV file showing group members and a CSV file showing Shared Drive membership
#          and output a CSV file showing the individual group members
# Note: This script can use GAM7 or Advanced GAM:
#       https://github.com/GAM-team/GAM
#	https://github.com/taers232c/GAMADV-XTD3
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Get Group Membership
#  $ gam redirect csv ./GroupMembers.csv print group-members fields email,type recursive
# 2: Get Shared Drive membership
#  $ gam config csv_output_header_drop_filter "User,createdTime,permission.photoLink,permission.permissionDetails" redirect csv ./SharedDriveMembers.csv print shareddriveacls oneitemperrow
# 3: From that list of Shared Drive members, expand ACLs of type group to show individual members
#  $ python3 ExpandSharedDriveGroupMembers.py ./GroupMembers.csv ./SharedDriveMembers.csv ./ExpandedSharedDriveMembers.csv
"""

import csv
import sys

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

# Get Group Membership
inputFile = open(sys.argv[1], 'r', encoding='utf-8')
inputCSV = csv.DictReader(inputFile, quotechar=QUOTE_CHAR)
GroupMembers = {}
for row in inputCSV:
  if row['type'] == 'USER':
    group = row['group'].lower()
    GroupMembers.setdefault(group, [])
    GroupMembers[group].append({'email': row['email'].lower(), 'level': row['level'], 'subgroup': row['subgroup']})
inputFile.close()

# Get Shared Drive Mmbership
inputFile = open(sys.argv[2], 'r', encoding='utf-8')
inputCSV = csv.DictReader(inputFile, quotechar=QUOTE_CHAR)
inputFieldNames = inputCSV.fieldnames
# Expanded Shared Drive Membership
outputFile = open(sys.argv[3], 'w', encoding='utf-8', newline='')
outputFieldNames = inputFieldNames+['email', 'level', 'subgroup']
outputCSV = csv.DictWriter(outputFile, outputFieldNames, lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

for row in inputCSV:
  email = row['permission.emailAddress'].lower()
  if row['permission.type'] != 'group' or email not in GroupMembers:
    outputCSV.writerow(row)
  else:
    for member in GroupMembers[email]:
      row.update(member)
      outputCSV.writerow(row)

inputFile.close()
outputFile.close()
