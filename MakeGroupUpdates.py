#!/usr/bin/env python3
"""
# Purpose: Convert a CSV file showing group members to one that can be fed into Gam to sync members
# Note: This script can use Basic or Advanced GAM:
#	https://github.com/jay0lee/GAM
#	https://github.com/taers232c/GAMADV-XTD3
# Customize: Set INPUT and OUTPUT field names
# Usage:
# 1: Get group members
#  $ Basic: gam print group-members fields email,role > GroupUsers.csv
#  $ Advanced: gam redirect csv ./GroupMembers.csv print group-members fields email,role
# 2: From that list of group members, output a CSV file with headers primaryEmail,GroupsCount,Groups that shows the groups for each user
#  $ python MakeGroupUpdates.py ./GroupMemberss.csv ./GroupUpdates.csv
# 3: Preview the changes if desired
#  $ gam csv GroupUpdates.csv gam update group ~group sync ~role preview ~members
# 3: Sync the groups
#  $ gam csv GroupUpdates.csv gam update group ~group sync ~role ~members
"""

import csv
import sys

INPUT_GROUP = 'group'
INPUT_ROLE = 'role'
INPUT_EMAIL = 'email'

OUTPUT_GROUP = 'group'
OUTPUT_ROLE = 'role'
OUTPUT_MEMBERS = 'members'

DELIMITER = ' '
QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, [OUTPUT_GROUP, OUTPUT_ROLE, OUTPUT_MEMBERS], lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin

Groups = {}
for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  group = row[INPUT_GROUP]
  role = row[INPUT_ROLE]
  Groups.setdefault(group, {})
  Groups[group].setdefault(role, [])
  Groups[group][role].append(row[INPUT_EMAIL])

for group in sorted(Groups):
  for role in Groups[group]:
    outputCSV.writerow({OUTPUT_GROUP: group,
                        OUTPUT_ROLE: role,
                        OUTPUT_MEMBERS: DELIMITER.join(Groups[group][role])})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
