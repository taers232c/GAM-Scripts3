#!/usr/bin/env python3
"""
# Purpose: Make a CSV file showing groups owned by users
# Usage:
# 1: Get group owners
#  $ gam print groups owners delimiter " " > ./GroupOwners.csv
# 2: From that list of groups, output a CSV file with headers "User,GroupsOwnedByUser
#  $ python GetGroupsOwnedByUser.py ./GroupOwners.csv ./GroupsOwnedByUser.csv
# 3: If you only want groups owned by a select list of users, specify the CSV file name and field name that lists the users
#  $ python GetGroupsOwnedByUser.py ./GroupOwners.csv ./GroupsOwnedByUser.csv ./<Filename>:<FieldName>
"""

import csv
import sys

SelectedUsers = set()
GroupsOwnedByUser = {}

if len(sys.argv) > 3:
  filename, fieldname = sys.argv[3].split(':')
  inputFile = open(filename, 'rb')
  for row in csv.DictReader(inputFile):
    SelectedUsers.add(row[fieldname].lower())
  inputFile.close()
if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w')
else:
  outputFile = sys.stdout
outputFile.write('User,GroupsOwnedByUser\n')
if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r')
else:
  inputFile = sys.stdin

for row in csv.DictReader(inputFile):
  for k, v in iter(row.items()):
    if row['OwnersCount'] != '0':
      for owner in row['Owners'].lower().split(' '):
        if (not SelectedUsers) or (owner in SelectedUsers):
          GroupsOwnedByUser.setdefault(owner, [])
          GroupsOwnedByUser[owner].append(row['Email'])
for user in sorted(GroupsOwnedByUser):
  outputFile.write('{0},{1}\n'.format(user,
                                      ' '.join(GroupsOwnedByUser[user])))

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
