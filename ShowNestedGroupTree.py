#!/usr/bin/env python3
"""
# Purpose: Produce a file to show hierarchial group membership
# Note: This script can use GAM7 or Advanced GAM:
#       https://github.com/GAM-team/GAM                                                                                                                               
#	https://github.com/taers232c/GAMADV-XTD3
# Customize: INDENTED_INDENTATION, JSON_INDENTATION, LIST_DELIMITER
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Get group members email address and type
#  $ gam redirect csv ./GroupMembers.csv print group-members fields email,type
# 2: If you want empty groups in the output proceed to step 4
# 3: From the list of group members, output a file showing hierarchial group membership
#  $ python3 ShowNestedGroupTree.py ./GroupMembers.csv indented|list|json ./NestedGroupTree.txt
#    You're done
# 4: Get a list of empty groups
#  $ gam config csv_output_row_filter "'membersCount:count=0','managersCount:count=0','ownersCount:count=0'" redirect csv ./EmptyGroups.csv print groups memberscount managerscount ownerscount
# 5: From the list of group members and empty groups, output a file showing hierarchial group membership
#  $ python3 ShowNestedGroupTree.py ./GroupMembers.csv indented|list|json empty ./EmptyGroups.csv  ./NestedGroupTree.txt
"""

import csv
import json
import sys

QUOTE_CHAR = '"' # Adjust as needed

INDENTED = 'indented'
JSON = 'json'
LIST = 'list'

MODE_CHOICES = [INDENTED, JSON, LIST]
mode = INDENTED

INDENTED_INDENTATION = 2
JSON_INDENTATION = 1
LIST_DELIMITER = ','

def printIndentedGroupTree(email, depth):
  outputFile.write(' '*depth+email+'\n')
  for member in sorted(Groups.get(email, [])):
    if member[1] == 'GROUP':
      printIndentedGroupTree(member[0], depth+INDENTED_INDENTATION)

def printListGroupTree(email, nestedList):
  nestedList.append(email)
  memberList = [member[0] for member in sorted(Groups.get(email, [])) if member[1] == 'GROUP']
  if memberList:
    for member in memberList:
      printListGroupTree(member, nestedList)
      nestedList.pop()
  else:
    outputFile.write(LIST_DELIMITER.join(nestedList)+'\n')

def printJSONGroupTree(email, nestedList):
  nestedList.append(email)
  memberList = [member[0] for member in sorted(Groups.get(email, [])) if member[1] == 'GROUP']
  if memberList:
    for member in memberList:
      printJSONGroupTree(member, nestedList)
      nestedList.pop()
  else:
    groupJSONList.append({nestedList[0]: nestedList[1:]})

Groups = {}

i = 3
if (len(sys.argv) > i) and (sys.argv[i].lower()  == 'empty'):
  i += 1
  if len(sys.argv) > i:
    inputFile = open(sys.argv[i], 'r', encoding='utf-8')
    for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
      Groups[row.get('email', row.get('Email', 'Unknown'))] =  []
    inputFile.close()
  else:
    sys.stderr.write('Missing filename after option empty\n')
    sys.exit(1)
  i+= 1

if (len(sys.argv) > i) and (sys.argv[i] != '-'):
  outputFile = open(sys.argv[i], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout

if len(sys.argv) > 2:
  mode = sys.argv[2].lower()
  if mode not in MODE_CHOICES:
    sys.stderr.write(f'Option mode ({mode}) must be {"|".join(MODE_CHOICES)}\n')
    sys.exit(1)

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin
inputCSV = csv.DictReader(inputFile, quotechar=QUOTE_CHAR)

for row in inputCSV:
  group = row['group']
  Groups.setdefault(group, [])
  Groups[group].append((row['email'], row['type']))
if mode == INDENTED:
  for group in sorted(Groups):
    printIndentedGroupTree(group, 0)
elif mode == JSON:
  groupJSONList = []
  for group in sorted(Groups):
    printJSONGroupTree(group, [])
  json.dump(groupJSONList, outputFile, indent=JSON_INDENTATION, sort_keys=True)
  outputFile.write('\n')
else: # mode == LIST
  for group in sorted(Groups):
    printListGroupTree(group, [])

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
