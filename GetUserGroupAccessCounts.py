#!/usr/bin/env python3
"""
# Purpose: For a Google Drive User(s), show user/group file access counts
# Note: This script can use Basic or Advanced GAM:
#	https://github.com/jay0lee/GAM
#	https://github.com/taers232c/GAMADV-XTD3
# Customize: GROUP_ROLES, USER_ROLES
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Get ACLs for all files, if you don't want all users, replace all users with your user selection in the command below
#  $ Basic: gam all users print filelist id title permissions > filelistperms.csv
#  $ Basic: gam user user@domain.com print filelist id title permissions > filelistperms.csv
#  $ Advanced: gam config auto_batch_min 1 redirect csv ./filelistperms.csv multiprocess all users print filelist fields id,title,permissions
#  $ Advanced: gam redirect csv ./filelistperms.csv user user@domain.com print filelist fields id,title,permissions
# 2: From that list of ACLs, output a CSV file that lists the user/group file access counts
#  $ python3 GetUserGroupAccessCounts.py filelistperms.csv UserCounts.csv GroupCounts.csv
"""

import csv
import re
import sys

GROUP_ROLES = ['commenter', 'reader', 'writer'] # Choose from: commenter|reader|writer
USER_ROLES = ['owner', 'commenter', 'reader', 'writer'] # Choose from: owner|commenter|reader|writer

DEFAULT_GROUP = {}
for role in GROUP_ROLES:
  DEFAULT_GROUP[role] = 0

DEFAULT_USER = {}
for role in USER_ROLES:
  DEFAULT_USER[role] = 0

FILE_NAME = 'name'
ALT_FILE_NAME = 'title'

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

PERMISSIONS_N_TYPE = re.compile(r"permissions.(\d+).type")

Users = {}
Groups = {}

groupOutputFile = open(sys.argv[3], 'w', encoding='utf-8', newline='')
groupFieldNames = ['Group']+GROUP_ROLES
groupOutputCSV = csv.DictWriter(groupOutputFile, groupFieldNames,
                                lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
groupOutputCSV.writeheader()

userOutputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
userFieldNames = ['User']+USER_ROLES
userOutputCSV = csv.DictWriter(userOutputFile, userFieldNames,
                               lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
userOutputCSV.writeheader()

inputFile = open(sys.argv[1], 'r', encoding='utf-8')
for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  for k, v in iter(row.items()):
    mg = PERMISSIONS_N_TYPE.match(k)
    if mg and v:
      permissions_N = mg.group(1)
      if row.get(f'permissions.{permissions_N}.deleted') == 'True':
        continue
      role = row[f'permissions.{permissions_N}.role']
      if v == 'user':
        if role in USER_ROLES:
          emailAddress = row[f'permissions.{permissions_N}.emailAddress'].lower()
          Users.setdefault(emailAddress, DEFAULT_USER.copy())
          Users[emailAddress][role] += 1
      elif v == 'group':
        if role in GROUP_ROLES:
          emailAddress = row[f'permissions.{permissions_N}.emailAddress'].lower()
          Groups.setdefault(emailAddress, DEFAULT_GROUP.copy())
          Groups[emailAddress][role] += 1
inputFile.close()

for k, v in sorted(iter(Users.items())):
  row = {'User': k}
  row.update(v)
  userOutputCSV.writerow(row)
userOutputFile.close()

for k, v in sorted(iter(Groups.items())):
  row = {'Group': k}
  row.update(v)
  groupOutputCSV.writerow(row)
groupOutputFile.close()
