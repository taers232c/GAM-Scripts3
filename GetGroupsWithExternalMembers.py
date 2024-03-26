#!/usr/bin/env python3
"""
# Purpose: Produce a CSV file showing groups with external members, i.e, those in domains other than ones you specify.
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
#  $ python3 GetGroupsWithExternalMembers.py ./GroupMembers.csv ./GroupsWithExternalMembers.csv
# 3: If you want a list of the external members, add another filename to the command, the external members will be output to that file
#  $ python3 GetGroupsWithExternalMembers.py ./GroupMembers.csv ./GroupsWithExternalMembers.csv ./ExternalMembers.csv
# 4: If you want to delete the external members from their groups, you can do the following which uses one API call per member
#  $ gam csv ./ExternalMembers.csv gam update group "~group" delete member "~email"
# 5: With Advanced GAM, you can delete the members in batches
#  $ gam update group csvkmd ./ExternalMembers.csv keyfield group datafield email delete member csvdata email
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

if len(sys.argv) > 3:
  matchFile = open(sys.argv[3], 'w', encoding='utf-8', newline='')
  matchCSV = csv.DictWriter(matchFile, inputCSV.fieldnames, lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
  matchCSV.writeheader()
else:
  matchFile = None

Groups = {}
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
      if matchFile:
        matchCSV.writerow(row)

if matchFile:
  matchFile.close()

for group, domains in sorted(iter(Groups.items())):
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
