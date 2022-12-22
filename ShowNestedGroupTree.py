#!/usr/bin/env python3
"""
# Purpose: Produce a file to show hierarchial group membership
# Note: This requires Advanced GAM:
#	https://github.com/taers232c/GAMADV-XTD3
# Customize: SHOW_INDENTED, INDENTATION, DELIMITER
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Get group members of type group
#  $ gam redirect csv ./GroupMembers.csv print group-members fields email types group
# 2: From that list of group members, output a file showing hierarchial group membership
#  $ python3 ShowNestedGroupTree.py ./GroupMembers.csv ./NextedGroupTree.txt
"""

import csv
import sys

QUOTE_CHAR = '"' # Adjust as needed

SHOW_INDENTED = False
# True  - Show nesting as indented members
# False - Show nesting as list
INDENTATION = 2
DELIMITER = ','

def printIndentedGroupTree(email, depth):
  outputFile.write(' '*depth+email+'\n')
  for member in sorted(Groups.get(email, [])):
    printIndentedGroupTree(member, depth+INDENTATION)

def printListGroupTree(email, nestedList):
  nestedList.append(email)
  memberList = sorted(Groups.get(email, []))
  if memberList:
    for member in memberList:
      printListGroupTree(member, nestedList)
      nestedList.pop()
  else:
    outputFile.write(DELIMITER.join(nestedList)+'\n')

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
  Groups.setdefault(group, [])
  Groups[group].append(row['email'])
if SHOW_INDENTED:
  for group in sorted(Groups):
    printIndentedGroupTree(group, 0)
else:
  for group in sorted(Groups):
    printListGroupTree(group, [])

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
