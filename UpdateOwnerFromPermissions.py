#!/usr/bin/env python3
"""
# Purpose: Update Owner column from permissions.n.emailAddress column where permissions.n.role == owner
#  $ python UpdateOwnerFromPermissions.py filelist.csv updatedfilelist.csv
"""

import csv
import re
import sys

id_n_address = re.compile(r"permissions.(\d+).id")

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w')
else:
  outputFile = sys.stdout

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin
inputCSV = csv.DictReader(inputFile)

outputCSV = csv.DictWriter(outputFile, inputCSV.fieldnames, lineterminator='\n')
outputCSV.writeheader()

for row in inputCSV:
  for k, v in iter(row.items()):
    mg = id_n_address.match(k)
    if mg:
      perm_group = mg.group(1)
      if v:
        if row['permissions.{0}.role'.format(perm_group)] == 'owner':
          row['Owner'] = row['permissions.{0}.emailAddress'.format(perm_group)]
          break
  outputCSV.writerow(row)

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
