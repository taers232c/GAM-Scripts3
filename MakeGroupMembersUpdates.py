#!/usr/bin/env python3
"""
# Purpose: Make a CSV that shows the changes required to update current group memberships to match desired group memberships
# Note: This script can use Basic or Advanced GAM:
#	https://github.com/GAM-team/GAM
#	https://github.com/taers232c/GAMADV-XTD3
# Customize: Set CURRENT, DESIRED and OUTPUT field names
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Get current group members
#  $ Basic: gam print group-members fields email,role > GroupUsers.csv
#  $ Advanced: gam redirect csv ./CurrentGroupMembers.csv print group-members fields email,role
# 2: Produce a CSV file DesiredGroupMembers.csv with headers group,role,email that lists the desired group members
# 3: From those lists of group members, output a CSV file with headers action,group,role,email that indicates
#    the changes necessary to make th current group members match the desired group members
#  $ python3 MakeGroupMembersUpdates.py ./CurrentGroupMembers.csv ./DesiredGroupMembers.csv ./GroupUpdates.csv
# 3: Preview the changes if desired
#  $ gam redirect stdout ./GroupUpdates.log multiprocess redirect stderr stdout csv ./GroupUpdates.csv gam update group "~group" "~action" "~role" preview "~members"
# 3: Sync the groups
#  $ gam redirect stdout ./GroupUpdates.log multiprocess redirect stderr stdout csv ./GroupUpdates.csv gam update group "~group" "~action" "~role" "~members"
"""

import csv
import sys

CURRENT_INPUT_GROUP = 'group'
CURRENT_INPUT_ROLE = 'role'
CURRENT_INPUT_EMAIL = 'email'

DESIRED_INPUT_GROUP = 'group'
DESIRED_INPUT_ROLE = 'role'
DESIRED_INPUT_EMAIL = 'email'

OUTPUT_ACTION = 'action'
OUTPUT_GROUP = 'group'
OUTPUT_ROLE = 'role'
OUTPUT_MEMBERS = 'members'

ACTION_ADD = 'add'
ACTION_DELETE = 'delete'
ACTION_UPDATE = 'update'

ROLE_MEMBER = 'MEMBER'
ROLE_MANAGER = 'MANAGER'
ROLE_OWNER = 'OWNER'
ROLES_LIST = [ROLE_MEMBER, ROLE_MANAGER, ROLE_OWNER]
ROLES_SET = {ROLE_MEMBER, ROLE_MANAGER, ROLE_OWNER}

SEARCH_ROLE_LISTS = {
  ROLE_MEMBER: [ROLE_MANAGER, ROLE_OWNER],
  ROLE_MANAGER: [ROLE_MEMBER, ROLE_OWNER],
  ROLE_OWNER: [ROLE_MEMBER, ROLE_MANAGER]
  }

DELIMITER = ' '
QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

def findDesiredRole(pgroup, pemail, rolesList, items):
  for prole in rolesList:
    if pemail in DesiredGroups[pgroup][prole]:
      items[prole].append(pemail)
      return

sysRC = 0
CurrentGroups = {}
currentFile = open(sys.argv[1], 'r', encoding='utf-8')
for row in csv.DictReader(currentFile, quotechar=QUOTE_CHAR):
  group = row[CURRENT_INPUT_GROUP].lower()
  role = row[CURRENT_INPUT_ROLE].upper()
  email = row[CURRENT_INPUT_EMAIL].lower()
  if role not in ROLES_SET:
    sys.stderr.write(f'ERROR: File: {currentFile}, Group: {group}, Email: {email}, Role: {role} Invalid\n')
    sysRC = 1
    continue
  CurrentGroups.setdefault(group, {ROLE_MEMBER: set(), ROLE_MANAGER: set(), ROLE_OWNER: set(), 'ALL': set()})
  CurrentGroups[group][role].add(email)
  CurrentGroups[group]['ALL'].add(email)
currentFile.close()
if sysRC:
  sys.exit(sysRC)

DesiredGroups = {}
desiredFile = open(sys.argv[2], 'r', encoding='utf-8')
for row in csv.DictReader(desiredFile, quotechar=QUOTE_CHAR):
  group = row[DESIRED_INPUT_GROUP].lower()
  role = row[DESIRED_INPUT_ROLE].upper()
  email = row[DESIRED_INPUT_EMAIL].lower()
  if role not in ROLES_SET:
    sys.stderr.write(f'ERROR: File: {desiredFile}, Group: {group}, Email: {email}, Role: {role} Invalid\n')
    sysRC = 2
    continue
  DesiredGroups.setdefault(group, {ROLE_MEMBER: set(), ROLE_MANAGER: set(), ROLE_OWNER: set(), 'ALL': set()})
  DesiredGroups[group][role].add(email)
  DesiredGroups[group]['ALL'].add(email)
desiredFile.close()
if sysRC:
  sys.exit(sysRC)

outputFile = open(sys.argv[3], 'w', encoding='utf-8', newline='')
outputCSV = csv.DictWriter(outputFile, [OUTPUT_ACTION, OUTPUT_GROUP, OUTPUT_ROLE, OUTPUT_MEMBERS], lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

for group in sorted(CurrentGroups):
  if group not in DesiredGroups:
    continue
  deletes = CurrentGroups[group]['ALL']-DesiredGroups[group]['ALL']
  if deletes:
    outputCSV.writerow({OUTPUT_ACTION: ACTION_DELETE,
                        OUTPUT_GROUP: group,
                        OUTPUT_ROLE: ROLE_MEMBER,
                        OUTPUT_MEMBERS: DELIMITER.join(deletes)})
  adds = DesiredGroups[group]['ALL']-CurrentGroups[group]['ALL']
  if adds:
    addItems = {ROLE_MEMBER: [], ROLE_MANAGER: [], ROLE_OWNER: []}
    for email in adds:
      findDesiredRole(group, email, ROLES_LIST, addItems)
    for role in ROLES_LIST:
      if addItems[role]:
        outputCSV.writerow({OUTPUT_ACTION: ACTION_ADD,
                            OUTPUT_GROUP: group,
                            OUTPUT_ROLE: role,
                            OUTPUT_MEMBERS: DELIMITER.join(addItems[role])})
  updateItems = {ROLE_MEMBER: [], ROLE_MANAGER: [], ROLE_OWNER: []}
  for role in ROLES_LIST:
    updates = CurrentGroups[group][role]-DesiredGroups[group][role]
    for email in updates:
      if email not in deletes:
        findDesiredRole(group, email, SEARCH_ROLE_LISTS[role], updateItems)
  for role in ROLES_LIST:
    if updateItems[role]:
      outputCSV.writerow({OUTPUT_ACTION: ACTION_UPDATE,
                          OUTPUT_GROUP: group,
                          OUTPUT_ROLE: role,
                          OUTPUT_MEMBERS: DELIMITER.join(updateItems[role])})

outputFile.close()
