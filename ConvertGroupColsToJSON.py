#!/usr/bin/env python3
"""
# Purpose: Convert a CSV file showing group settigs to one with the settings in JSON format
# Note: This script can use GAM7 or Advanced GAM:
#	https://github.com/taers232c/GAMADV-XTD3
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
#  $ python ConvertGroupColsToJSON.py ./Groups.csv ./GroupsJSON.csv
"""

import csv
import sys

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

GROUP_JSON_SKIP_FIELDS = ['adminCreated', 'directMembersCount', 'members', 'aliases', 'nonEditableAliases', 'kind']

inputFile = open(sys.argv[1], 'r', encoding='utf-8')

outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
outputFieldnames = ['email', 'id', 'name', 'description', 'JSON-settings']
outputCSV = csv.DictWriter(outputFile, outputFieldnames, lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  groupEmail = row.pop('email')
  groupId = row.pop('id', '')
  groupName = row.pop('name', '')
  groupDescription = row.pop('description', '')
  for field in GROUP_JSON_SKIP_FIELDS:
    row.pop(field, None)
  outputCSV.writerow({'email': groupEmail,
                      'id': groupId,
                      'name': groupName,
                      'description': groupDescription,
                      'JSON-settings': row})

inputFile.close()
outputFile.close()
