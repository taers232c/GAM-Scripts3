#!/usr/bin/env python3
"""
# Purpose: Produce a file to show hierarchial group membership
# Note: This script can use GAM7 or Advanced GAM:
#       https://github.com/GAM-team/GAM                                                                                                                               
#	https://github.com/taers232c/GAMADV-XTD3
# Customize: SHOW_ROLE
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Get group members
#  $ gam redirect csv ./GroupMembers.csv print group-members fields email,role recursive noduplicates
# 2: From that list of group members, output a file showing hierarchial group membership
#  $ python3 ShowGroupMemberTree.py ./GroupMembers.csv ./GroupMemberTree.txt
"""

import csv
import sys

QUOTE_CHAR = '"' # Adjust as needed

SHOW_ROLE = False # True - display role, False - don't display role

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin
inputCSV = csv.DictReader(inputFile, quotechar=QUOTE_CHAR)

Groups = {}
for row in inputCSV:
  group = row['group']
  Groups.setdefault(group, {})
  Groups[group][row['email']] = row['role']
for group, members in sorted(iter(Groups.items())):
  outputFile.write(f'Group: {group}\n')
  for member, role in sorted(iter(members.items())):
    if SHOW_ROLE:
      outputFile.write(f"  {member}:{role}\n")
    else:
      outputFile.write(f"  {member}\n")
if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
