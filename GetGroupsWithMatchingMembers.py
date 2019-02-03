#!/usr/bin/env python3
"""
# Purpose: Produce a CSV file showing groups with members that match regular expressions
# Note: This script can use Basic or Advanced GAM:
#	https://github.com/jay0lee/GAM
#	https://github.com/taers232c/GAMADV-X, https://github.com/taers232c/GAMADV-XTD, https://github.com/taers232c/GAMADV-XTD3
# Customize: USER_MATCH_PATTERN, GROUP_MATCH_PATTERN, SHOW_GROUPS_WITH_NO_MATCHES
# Usage:
# 1: Get group members
#  $ Basic: gam print group-members fields email,type > GroupMembers.csv
#  $ Advanced: gam redirect csv ./GroupMembers.csv print group-members fields email,type
# 2: From that list of group members, output a CSV file with headers group,groupMatches,groupTotal,userMatches,userTotal
#  $ python GetGroupsWithMatchingMembers.py ./GroupMembers.csv ./GroupsWithExternalMembers.csv
"""

import csv
import re
import sys

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n' 

# Python regular expressions
USER_MATCH_PATTERN = r'^.*$'
GROUP_MATCH_PATTERN = r'^.*$'

# Should groups with no matches be shown
SHOW_GROUPS_WITH_NO_MATCHES = False

# Indexes into group counts
GROUP_MATCHES = 0
GROUP_TOTAL = 1
USER_MATCHES = 2
USER_TOTAL = 3

if USER_MATCH_PATTERN:
  try:
    userMatchPattern = re.compile(USER_MATCH_PATTERN)
  except re.error as e:
    print('Error: invalid USER_MATCH_PATTERN: "{0}", {1}'.format(USER_MATCH_PATTERN, e))
    sys.exit(1)
else:
  userMatchPattern = None

if GROUP_MATCH_PATTERN:
  try:
    groupMatchPattern = re.compile(GROUP_MATCH_PATTERN)
  except re.error as e:
    print('Error: invalid GROUP_MATCH_PATTERN: "{0}", {1}'.format(GROUP_MATCH_PATTERN, e))
    sys.exit(1)
else:
  groupMatchPattern = None

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['group', 'groupMatches', 'groupTotal', 'userMatches', 'userTotal'], lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin

Groups = {}
for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  if row['type'] in ['USER', 'GROUP']:
    group = row['group']
    Groups.setdefault(group, [0, 0, 0, 0])
    emailAddress = row['email']
    if row['type'] == u'USER':
      Groups[group][USER_TOTAL] += 1
      if userMatchPattern and userMatchPattern.match(emailAddress):
        Groups[group][USER_MATCHES] += 1
    elif row['type'] == u'GROUP':
      Groups[group][GROUP_TOTAL] += 1
      if groupMatchPattern and groupMatchPattern.match(emailAddress):
        Groups[group][GROUP_MATCHES] += 1

for group, counts in sorted(iter(Groups.items())):
  if SHOW_GROUPS_WITH_NO_MATCHES or counts[GROUP_MATCHES] or counts[USER_MATCHES]:
    outputCSV.writerow({'group': group,
                        'groupMatches': counts[GROUP_MATCHES],
                        'groupTotal': counts[GROUP_TOTAL],
                        'userMatches': counts[USER_MATCHES],
                        'userTotal': counts[USER_TOTAL],
                       })

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
