#!/usr/bin/env python3
"""
# Purpose: Merge data from print groups CSV file into print group-members CSV file
#
# Note: This script can use GAM7 or Advanced GAM:
#   https://github.com/GAM-team/GAM
#   https://github.com/taers232c/GAMADV-XTD3
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or  python3 -V
#  Python 3.x.y
# Usage:
# 1: Generate the two data files, e.g.:
#  $ gam redirect csv ./GroupInfo.csv print groups fields name,description
#  $ gam redirect csv ./GroupMembers.csv print group-members
# 2: Merge the files
#  $ python3 MergeGroupInfoMembers.py ./GroupInfo.csv ./GroupMembers.csv ./GroupMerged.csv
"""

import csv
import sys

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

# Data from print groups
groupInfo = {}
infoFileName = sys.argv[1]
infoFile = open(infoFileName, 'r', encoding='utf-8')
infoCSV = csv.DictReader(infoFile, quotechar=QUOTE_CHAR)
infoFieldNames = infoCSV.fieldnames[:]
INFO_KEY_FIELD = 'email'
if INFO_KEY_FIELD not in infoFieldNames:
  sys.stderr.write(f'Group Info key field "{INFO_KEY_FIELD}" is not in {infoFileName} headers: {",".join(infoFieldNames)}\n')
  sys.exit(1)
infoFieldNames.remove(INFO_KEY_FIELD)
if 'name' in infoFieldNames:
  infoFieldNames[infoFieldNames.index('name')] = 'groupName'
for row in infoCSV:
  if 'name' in row:
    row['groupName'] = row.pop('name')
  groupInfo[row.pop(INFO_KEY_FIELD).lower()] = row
infoFile.close()

# Data from print group-members
memberFileName = sys.argv[2]
memberFile = open(memberFileName, 'r', encoding='utf-8')
memberCSV = csv.DictReader(memberFile, quotechar=QUOTE_CHAR)
memberFieldNames = memberCSV.fieldnames[:]
MEMBER_KEY_FIELD = 'group'
if MEMBER_KEY_FIELD not in memberFieldNames:
  sys.stderr.write(f'Group Member key field "{MEMBER_KEY_FIELD}" is not in {memberFileName} headers: {",".join(memberFieldNames)}\n')
  sys.exit(1)
i = memberFieldNames.index(MEMBER_KEY_FIELD)
mergedFieldNames = memberFieldNames[0:i+1]+infoFieldNames+memberFieldNames[i+1:]
mergedFileName = sys.argv[3]
mergedFile = open(mergedFileName, 'w', encoding='utf-8', newline='')
mergedCSV = csv.DictWriter(mergedFile, mergedFieldNames, lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
mergedCSV.writeheader()

errors = 0
for row in memberCSV:
  group= row[MEMBER_KEY_FIELD].lower()
  if group in groupInfo:
    row.update(groupInfo[group])
  else:
    errors = 1
    sys.stderr.write(f'Group Member key value "{group}" in {memberFileName} does not occur in {infoFileName}\n')
  mergedCSV.writerow(row)

memberFile.close()
mergedFile.close()
sys.exit(errors)
