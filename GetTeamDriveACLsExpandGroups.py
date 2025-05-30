#!/usr/bin/env python3
"""
# Purpose: Get ACLs for Team Drives, expand type group ACls into the constituent type user ACLs. permission.id is deleted for the users as it is not known
# Customize: Set RETAIN_GROUP_ACL_ROW as desired
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Get ACLs for all Shared Drives
#  $ gam redirect csv ./TeamDriveACLs.csv print teamdriveacls fields id,domain,emailaddress,role,type,deleted oneitemperrow
# 2: Get group members
#  $ gam redirect csv ./GroupMembers.csv print groups roles members,managers,owners delimiter " "
# 3: Generate a CSV file with the same headers as TeamDriveACls.csv with type group ACLs replaced with type user ACLs for each member
#    There is an additional header, permission.group, that shows the group email address from which the user ACLs are derived.
#  $ python3 GetTeamDriveACLsExpandGroups.py TeamDriveACLs.csv GroupMembers.csv TeamDriveACLsExpandedGroups.csv
"""

import csv
import sys

MEMBER_DELIMITER = ' '

RETAIN_GROUP_ACL_ROW = False # False: delete type group ACL rows, True: retain type grpup ACL rows

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

inputFile = open(sys.argv[1], 'r', encoding='utf-8')
inputCSV = csv.DictReader(inputFile, quotechar=QUOTE_CHAR)
fieldnames = inputCSV.fieldnames[:]
fieldnames.append('permission.group')

GroupMembers = {}
groupFile = open(sys.argv[2], 'r', encoding='utf-8')
for row in csv.DictReader(groupFile, quotechar=QUOTE_CHAR):
  group = row['email']
  GroupMembers[group] = []
  for field in ['Members', 'Managers', 'Owners']:
    if row[field]:
      GroupMembers[group].extend(row[field].split(MEMBER_DELIMITER))
groupFile.close()

if (len(sys.argv) > 3) and (sys.argv[3] != '-'):
  outputFile = open(sys.argv[3], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, fieldnames,
                           lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

for row in inputCSV:
  if row['permission.type'] != 'group':
    outputCSV.writerow(row)
    continue
  if RETAIN_GROUP_ACL_ROW:
    outputCSV.writerow(row)
  row['permission.type'] = 'user'
  row['permission.id'] = ''
  group = row['permission.emailAddress']
  row['permission.group'] = group
  for member in GroupMembers.get(group, []):
    row['permission.emailAddress'] = member
    _, domain = member.split('@')
    row['permission.domain'] = domain
    outputCSV.writerow(row)

inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
