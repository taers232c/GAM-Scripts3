#!/usr/bin/env python3
"""
# Purpose: Produce a file to show hierarchial group membership
# Note: This requires Advanced GAM:
#	https://github.com/taers232c/GAMADV-XTD3
# Customize: INDENTED_INDENTATION, JSON_INDENTATION, LIST_DELIMITER
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Get group members of type group
#  $ gam redirect csv ./GroupMembers.csv print group-members fields email,type types group
# 2: From that list of group members, output a file showing hierarchial group membership
#  $ python3 ShowNestedGroupTree.py ./GroupMembers.csv indented|list|json ./NextedGroupTree.txt
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

if (len(sys.argv) > 3) and (sys.argv[3] != '-'):
  outputFile = open(sys.argv[3], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout

if len(sys.argv) > 2:
  mode = sys.argv[2].lower()
  if mode not in MODE_CHOICES:
    sys.stderr.write(f'mode ({mode}) must be {"|".join(MODE_CHOICES)}\n')
    sys.exit(1)

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin
inputCSV = csv.DictReader(inputFile, quotechar=QUOTE_CHAR)

Groups = {}
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
