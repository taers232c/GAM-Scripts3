#!/usr/bin/env python3
"""
# Purpose: Produce a CSV file showing groups with only external members, i.e, those in domains other than ones you specify.
# Note: This script can use Basic or Advanced GAM:
#	https://github.com/GAM-team/GAM
#	https://github.com/taers232c/GAMADV-XTD3
# Customize: DELIMITER, DOMAIN_LIST, AGGREGATE_DOMAINS
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Get group members
#  $ Basic: gam print group-members fields email,type > GroupMembers.csv
#  $ Advanced: gam redirect csv ./GroupMembers.csv print group-members fields email,type
# 2: From that list of group members, output a CSV file with headers group,domain,count
#  $ python3 GetGroupsWithOnlyExternalMembers.py ./GroupMembers.csv ./GroupsWithOnlyExternalMembers.csv
"""

import csv
import sys

DELIMITER = ' ' # Character to separate domains in output CSV
QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

# Substitute your internal domain(s) in the list below, e.g., DOMAIN_LIST = ['domain.com',] DOMAIN_LIST = ['domain1.com', 'domain2.com',]
DOMAIN_LIST = ['domain.com',]

# False - show one group/one external domain per line
# True - show one group/all external domains per line
AGGREGATE_DOMAINS = True

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['group', 'domain', 'count'], lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin
inputCSV = csv.DictReader(inputFile, quotechar=QUOTE_CHAR)

Groups = {}
GroupsWithInternalMembers = set()

for row in inputCSV:
  if row['type'] in ['USER', 'GROUP']:
    group = row['group']
    emailAddress = row['email'].lower()
    atLoc = emailAddress.find('@')
    if atLoc > 1:
      domain = emailAddress[atLoc+1:]
    else:
      domain = 'unknown'
    if domain not in DOMAIN_LIST:
      Groups.setdefault(group, {})
      Groups[group].setdefault(domain, 0)
      Groups[group][domain] += 1
    else:
      GroupsWithInternalMembers.add(group)

for group, domains in sorted(iter(Groups.items())):
  if group in GroupsWithInternalMembers:
    continue
  if not AGGREGATE_DOMAINS:
    for domain, count in sorted(iter(domains.items())):
      outputCSV.writerow({'group': group,
                          'domain': domain,
                          'count': count})
  else:
    total = 0
    domainsList = []
    for domain, count in sorted(iter(domains.items())):
      domainsList.append(domain)
      total += count
    outputCSV.writerow({'group': group,
                        'domain': DELIMITER.join(domainsList),
                        'count': total})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
