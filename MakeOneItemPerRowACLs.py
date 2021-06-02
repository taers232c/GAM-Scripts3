#!/usr/bin/env python3
"""
# Purpose: Convert output from print filelist to put one ACL per row; you can filter for specific ACLs.
# Note: This script can use Basic or Advanced GAM:
#	https://github.com/jay0lee/GAM
#	https://github.com/taers232c/GAMADV-XTD3
# Customize: Set USER_LIST, GROUP_LIST. DOMAIN_LIST, ROLE_LIST, TYPE_LIST, DESIRED_ALLOWFILEDISCOVERY,
#	DROP_GENERAL_COLUMNS, DROP_PERMISSION_COLUMNS.
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Get ACLs for all files, replace user@domain.com with your user selection in the command below
#    For enhanced file selection in Advanced Gam see: https://github.com/taers232c/GAMADV-XTD3/wiki/Users-Drive-Files#display-file-lists
#  $ Basic: gam user user@domain.com print filelist id title permissions > filelistperms.csv
#  $ Advanced: gam redirect csv ./filelistperms.csv user user@domain.com print filelist fields id,name,permissions
# 2: From that list of files, output a CSV file that lists one ACL per row
#  $ python3 MakeOneItemPerRowACLs.py filelistperms.csv filelistpermsoipr.csv
"""

import csv
import re
import sys

# Specify specific user(s), e.g., USER_LIST = ['user1@domain.com'] USER_LIST = ['user1@domain.com', 'user2@domain.com']
# The list should be empty if you're only specifiying domains in DOMAIN_LIST, e.g. USER_LIST = []
USER_LIST = []

# Specify specific group(s), e.g., GROUP_LIST = ['group1@domain.com'] GROUP_LIST = ['group1@domain.com', 'group2@domain.com']
# The list should be empty if you're only specifiying domains in DOMAIN_LIST, e.g. GROUP_LIST = []
GROUP_LIST = []

# Specify specific domain(s) if you want all groups/users in the domain, e.g., DOMAIN_LIST = ['domain.com'] DOMAIN_LIST = ['domain1.com', 'domain2.com']
# The list should be empty if you're only specifiying groups in GROUP_LIST or users in USER_LIST, e.g. DOMAIN__LIST = []
DOMAIN_LIST = []

# Specify specific permission role value(s) ('owner', 'organizer', 'fileOrganizer', 'writer', 'commenter', 'reader'), e.g., ROLE_LIST = ['writer', 'commenter']
# The list should be empty if you want all roles, e.g, ROLE_LIST = []
ROLE_LIST = []

# Specify specific permission type value(s) ('user', 'group, 'domain', 'anyone'), e.g., TYPE_LIST = ['user', 'group']
# The list should be empty if you want all types, e.g, TYPE_LIST = []
TYPE_LIST = []

# Specify desired value of allowFileDiscovery field: True, False, Any (matches True and False)
# allowFileDiscovery False = withLink True
# allowFileDiscovery True = withLink False
DESIRED_ALLOWFILEDISCOVERY = 'Any'

# Specify generalcolumns you don't want in the output. e.g., photoLink.
# The list should be empty if you want all general columns, e.g, DROP_PERMISSION_COLUMNS = []
DROP_GENERAL_COLUMNS = ['permissions']

# Specify permission columns you don't want in the output. e.g., photoLink.
# The list should be empty if you want all permission columns, e.g, DROP_PERMISSION_COLUMNS = []
DROP_PERMISSION_COLUMNS = ['photoLink']

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
permissionFields = set()
inputFieldnames = []
for fieldname in inputCSV.fieldnames:
  mg = PERMISSIONS_N_FIELD.match(fieldname)
  if mg:
    field = mg.group(2)
    if (not DROP_PERMISSION_COLUMNS or field not in DROP_PERMISSION_COLUMNS) and field not in permissionFields:
      permissionFields.add(field)
      inputFieldnames.append(f'permission.{field}')
  elif not DROP_GENERAL_COLUMNS or fieldname not in DROP_GENERAL_COLUMNS:
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
    elif not DROP_GENERAL_COLUMNS or k not in DROP_GENERAL_COLUMNS:
      baseRow[k] = v
  for k, v in iter(permissions.items()):
    newRow = baseRow.copy()
    if ROLE_LIST and v['role'] not in ROLE_LIST:
      continue
    vtype = v['type']
    if not vtype:
      continue
    if TYPE_LIST and vtype not in TYPE_LIST:
      continue
    if vtype == 'user':
      emailAddress = v['emailAddress']
      domain = emailAddress[emailAddress.find('@')+1:]
      if DOMAIN_LIST and domain not in DOMAIN_LIST:
        continue
      if USER_LIST and emailAddress not in USER_LIST:
        continue
    elif vtype == 'group':
      emailAddress = v['emailAddress']
      domain = emailAddress[emailAddress.find('@')+1:]
      if DOMAIN_LIST and domain not in DOMAIN_LIST:
        continue
      if GROUP_LIST and emailAddress not in GROUP_LIST:
        continue
    elif vtype == 'domain':
      domain = v['domain']
      if DOMAIN_LIST and domain not in DOMAIN_LIST:
        continue
      if DESIRED_ALLOWFILEDISCOVERY != 'Any':
        allowFileDiscovery = v.get('allowFileDiscovery', str(row.get('withLink', '') == 'False'))
        if DESIRED_ALLOWFILEDISCOVERY != allowFileDiscovery:
          continue
    else: # vtype == 'anyone'
      if DESIRED_ALLOWFILEDISCOVERY != 'Any':
        allowFileDiscovery = v.get('allowFileDiscovery', str(row.get('withLink', '') == 'False'))
        if DESIRED_ALLOWFILEDISCOVERY != allowFileDiscovery:
          continue
    for kp, kv in sorted(v.items()):
      if not DROP_PERMISSION_COLUMNS or kp not in DROP_PERMISSION_COLUMNS:
        newRow[f'permission.{kp}'] = kv
    outputCSV.writerow(newRow)

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
