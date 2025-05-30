#!/usr/bin/env python3
"""
# Purpose: Make a CSV file showing the number of groups per domain in a multi-domain workspace
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or python3 -V
#  Python 3.x.y
# Usage:
# 1: Get groups
#  $ gam redirect csv ./Groups.csv print groups email
# 2: From that list of groups, output a CSV file with headers "Domain,Groups" that shows the
#    number of groups per domain
#  $ python3 CountGroupsByDomain.py ./Groups.csv ./GroupsPerDomain.csv
"""

import csv
import sys

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['Domain', 'Groups'], lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin

domainGroupCounts = {}
for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  email = row.get('email', row.get('Email'))
  if email:
    name, domain = email.split('@')
    domainGroupCounts.setdefault(domain, 0)
    domainGroupCounts[domain] += 1
for domain, count in sorted(iter(domainGroupCounts.items())):
  outputCSV.writerow({'Domain': domain, 'Groups': count})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
