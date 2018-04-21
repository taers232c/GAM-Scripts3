#!/usr/bin/env python3
"""
# Purpose: Update Owner column from permissions.n.emailAddress column where permissions.n.role == owner
#  $ python UpdateOwnerFromPermissions.py filelist.csv updatedfilelist.csv
"""

import csv
import re
import sys

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

PERMISSIONS_N_ROLE = re.compile(r"permissions.(\d+).role")

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w')
else:
  outputFile = sys.stdout

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin
inputCSV = csv.DictReader(inputFile, quotechar=QUOTE_CHAR)

outputCSV = csv.DictWriter(outputFile, inputCSV.fieldnames, lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

for row in inputCSV:
  for k, v in iter(row.items()):
    mg = PERMISSIONS_N_ROLE.match(k)
    if mg and v == 'owner':
      permissions_N = mg.group(1)
      row['Owner'] = row['permissions.{0}.emailAddress'.format(permissions_N)]
      break
  outputCSV.writerow(row)

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
