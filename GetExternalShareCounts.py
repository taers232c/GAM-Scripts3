#!/usr/bin/env python3
"""
# Purpose: For a Google Drive User(s), output a CSV file showing the share type counts for files shared by the user(s) externally
# Note: This script can use Basic or Advanced GAM:
#	https://github.com/jay0lee/GAM
#	https://github.com/taers232c/GAMADV-XTD3
# Customize: Set DOMAIN_LIST to the list of domains you consider internal. Set LINK_FIELD and LINK_VALUE.
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Get ACLs for all files, if you don't want all users, replace all users with your user selection in the command below
#  $ Basic GAM: gam all users print filelist id title permissions > filelistperms.csv
#  $ Advanced GAM: You can have GAM do some pre-filtering
#  $ EXCLUSIVE_DOMAINS = True:
#    Add the following clause to the command for each domain in DOMAIN_LIST: pm not domain domainx.com em
#  $ EXCLUSIVE_DOMAINS = False:
#    Add the following clause to the command for each domain in DOMAIN_LIST: pm domain domainx.com em
#  $ INCLUDE_ANYONE = True
#    Add the following clause to the command: pm type anyone em
#  $ gam config auto_batch_min 1 redirect csv ./filelistperms.csv multiprocess all users print filelist fields id,name,permissions <pm clauses>
# 2: From that list of ACLs, output a CSV file with headers:
#      Type,ExternalShare,Count
#  $ python3 GetExternalShareCounts.py filelistperms.csv externalsharecounts.csv
"""

import csv
import re
import sys

# Substitute your domain(s) in the list below, e.g., DOMAIN_LIST = ['domain.com',] DOMAIN_LIST = ['domain1.com', 'domain2.com',]
DOMAIN_LIST = ['domain.com']
# Indicate whether the list is exclusive or inclusive
# EXCLUSIVE_DOMAINS = True: You're interested only in domains not in DOMAIN_LIST which would typically be your internal domains
# EXCLUSIVE_DOMAINS = False: You're interested only in domains in DOMAIN_LIST which would typically be external domains
EXCLUSIVE_DOMAINS = True
# Indicate whether shares to anyone should be included
INCLUDE_ANYONE = True

# For GAM or GAMADV-XTD3 with drive_v3_native_names = false
#LINK_FIELD = 'withLink'
#LINK_VALUE = 'True'
# For GAMADV-XTD3 with drive_v3_native_names = true
LINK_FIELD = 'allowFileDiscovery'
LINK_VALUE = 'False'

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

PERMISSIONS_N_TYPE = re.compile(r"permissions.(\d+).type")

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['Type', 'ExternalShare', 'Count'], lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin

anyoneShareCount = anyoneWithLinkShareCount = 0
domainShareCounts = {}
domainWithLinkShareCounts = {}
groupShareCounts = {}
userShareCounts = {}
for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  for k, v in iter(row.items()):
    mg = PERMISSIONS_N_TYPE.match(k)
    if mg and v:
      permissions_N = mg.group(1)
      if row[f'permissions.{permissions_N}.role'] == 'owner':
        continue
      if row.get(f'permissions.{permissions_N}.deleted') == 'True':
        continue
      if v == 'anyone':
        if not INCLUDE_ANYONE:
          continue
        if row[f'permissions.{permissions_N}.{LINK_FIELD}'] == LINK_VALUE:
          anyoneWithLinkShareCount += 1
        else:
          anyoneShareCount += 1
      elif v == 'domain':
        domain = row[f'permissions.{permissions_N}.domain']
        if ((EXCLUSIVE_DOMAINS and domain in DOMAIN_LIST) or
            (not EXCLUSIVE_DOMAINS and domain not in DOMAIN_LIST)):
          continue
        if row[f'permissions.{permissions_N}.{LINK_FIELD}'] == LINK_VALUE:
          domainWithLinkShareCounts.setdefault(domain, 0)
          domainWithLinkShareCounts[domain] += 1
        else:
          domainShareCounts.setdefault(domain, 0)
          domainShareCounts[domain] += 1
      else: # group, user
        if row.get(f'permissions.{permissions_N}.deleted') == 'True':
          continue
        emailAddress = row[f'permissions.{permissions_N}.emailAddress']
        domain = row.get(f'permissions.{permissions_N}.domain', '')
        if not domain:
          domain = emailAddress[emailAddress.find('@')+1:]
        if ((EXCLUSIVE_DOMAINS and domain in DOMAIN_LIST) or
            (not EXCLUSIVE_DOMAINS and domain not in DOMAIN_LIST)):
          continue
        if v == 'group':
          groupShareCounts.setdefault(emailAddress, 0)
          groupShareCounts[emailAddress] += 1
        else:
          userShareCounts.setdefault(emailAddress, 0)
          userShareCounts[emailAddress] += 1
outputCSV.writerow({'Type': 'anyone', 'Count': anyoneShareCount})
outputCSV.writerow({'Type': 'anyoneWithLink', 'Count': anyoneWithLinkShareCount})
for externalShare, count in sorted(iter(domainShareCounts.items())):
  outputCSV.writerow({'Type': 'domain', 'ExternalShare': externalShare, 'Count': count})
for externalShare, count in sorted(iter(domainWithLinkShareCounts.items())):
  outputCSV.writerow({'Type': 'domainWithLink', 'ExternalShare': externalShare, 'Count': count})
for externalShare, count in sorted(iter(groupShareCounts.items())):
  outputCSV.writerow({'Type': 'group', 'ExternalShare': externalShare, 'Count': count})
for externalShare, count in sorted(iter(userShareCounts.items())):
  outputCSV.writerow({'Type': 'user', 'ExternalShare': externalShare, 'Count': count})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
