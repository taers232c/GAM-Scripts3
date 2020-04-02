#!/usr/bin/env python3
"""
# Purpose: Convert output from print filelist to put one ACL per row
# Note: This script can use Basic or Advanced GAM:
#	https://github.com/jay0lee/GAM
#	https://github.com/taers232c/GAMADV-XTD3
# Usage:
# 1: Get ACLs for all files, replace user@domain.com with your user selection in the command below
#    For enhanced file selection in Advanced gam see: https://github.com/taers232c/GAMADV-XTD3/wiki/Users-Drive-Files#display-file-lists
#  $ Basic: gam user user@domain.com print filelist id title permissions > filelistperms.csv
#  $ Advanced: gam redirect csv ./filelistperms.csv user user@domain.com print filelist fields id,name,permissions
# 2: From that list of files, output a CSV file that lists one ACL per row
#  $ python MakeOneItemPerRowACLs.py filelistperms.csv filelistpermsoipr.csv
"""

import csv
import re
import sys

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

PERMISSIONS_N_FIELD = re.compile(r"permissions.(\d+).(.+)")

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin

inputCSV = csv.DictReader(inputFile, quotechar=QUOTE_CHAR)
inputFieldnames = []
for fieldname in inputCSV.fieldnames:
  mg = PERMISSIONS_N_FIELD.match(fieldname)
  if mg:
    if mg.group(1) == '0':
      inputFieldnames.append(f'permission.{mg.group(2)}')
  else:
    inputFieldnames.append(fieldname)

outputCSV = csv.DictWriter(outputFile, inputFieldnames, lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

for row in inputCSV:
  baseRow = {}
  permissions = {}
  for k, v in iter(row.items()):
    mg = PERMISSIONS_N_FIELD.match(k)
    if mg:
      permissions_N = mg.group(1)
      permissions.setdefault(permissions_N, {})
      permissions[permissions_N][mg.group(2)] = v
    else:
      baseRow[k] = v
  for k, v in iter(permissions.items()):
    newRow = baseRow.copy()
    for kp, kv in sorted(v.items()):
      newRow[f'permission.{kp}'] = kv
    outputCSV.writerow(newRow)

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
