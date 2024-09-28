#!/usr/bin/env python3
"""
# Purpose: For a Google Drive User(s), show all shared file permissions organized into lists by type and role
# Note: This script can use GAM7 or Advanced GAM:
#       https://github.com/GAM-team/GAM                                                                                                                               
#	https://github.com/taers232c/GAMADV-XTD3
# Customize: Set SHOW_USERS, SHOW_GROUPS, SHOW_DOMAINS, SHOW_ANYONES, SHOW_COUNTS, LIST_DELIMITER
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Get ACLs for all files, if you don't want all users, replace all users with your user selection in the command below
#  $ gam config auto_batch_min 1 redirect csv ./filelistperms.csv multiprocess all users print filelist fields id,name,mimetype,basicpermissions,owners.emailaddress pm not role owner em pmfilter
#  $ gam redirect csv ./filelistperms.csv user user@domain.com print filelist fields id,name,mimetype,basicpermissions,owners.emailaddress pm not role owner em pmfilter
# 2: From that list of ACLs, output a CSV file that lists the shared file permissions organized into lists by type and role
#  $ python3 GetSharedFilePermissionsTypeRoleLists.py filelistperms.csv filetyperoleperms.csv
"""

import copy
import csv
import re
import sys

SHOW_USERS = True # True: show user ACLs; False: do not show user ACLs
SHOW_GROUPS = True # True: show group ACLs; False: do not show group ACLs
SHOW_DOMAINS = True # True: show domain ACLs; False: do not show domain ACLs
SHOW_ANYONES = True # True: show anyone ACLs; False: do not show anyone ACLs

SHOW_COUNTS = False  # True: show ACL counts columns; False: do not show ACL count columns

LIST_DELIMITER = ' '

FILE_NAME = 'name'
ALT_FILE_NAME = 'title'

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

PERMISSIONS_N_TYPE = re.compile(r"permissions.(\d+).type")

USER_GROUP_ROLES = ['commenter', 'reader', 'writer', 'fileOrganizer', 'organizer']
DOMAIN_ANYONE_ROLES = ['commenter', 'reader', 'writer']

ZERO_COUNTS = {
  'user': {
    'commenter': {'count': 0, 'addresses': []},
    'reader': {'count': 0, 'addresses': []},
    'writer': {'count': 0, 'addresses': []},
    'fileOrganizer': {'count': 0, 'addresses': []},
    'organizer': {'count': 0, 'addresses': []}
    },
  'group': {
    'commenter': {'count': 0, 'addresses': []},
    'reader': {'count': 0, 'addresses': []},
    'writer': {'count': 0, 'addresses': []},
    'fileOrganizer': {'count': 0, 'addresses': []},
    'organizer': {'count': 0, 'addresses': []}
    },
  'domain': {
    'commenter': {'count': 0, 'addresses': []},
    'reader': {'count': 0, 'addresses': []},
    'writer': {'count': 0, 'addresses': []}
    },
  'domainWithlink': {
    'commenter': {'count': 0, 'addresses': []},
    'reader': {'count': 0, 'addresses': []},
    'writer': {'count': 0, 'addresses': []}
    },
  'anyone': {
    'commenter': {'count': 0},
    'reader': {'count': 0},
    'writer': {'count': 0}
    },
  'anyoneWithlink': {
    'commenter': {'count': 0},
    'reader': {'count': 0},
    'writer': {'count': 0}
    },
  }

fieldnames = ['Owner', 'driveFileId', 'driveFileTitle', 'mimeType']
if SHOW_COUNTS:
  if SHOW_USERS:
    fieldnames.extend(['userCommenterCount', 'userCommenter',
                       'userReaderCount', 'userReader',
                       'userWriterCount', 'userWriter',
                       'userFileorganizerCount', 'userFileorganizer',
                       'userOrganizerCount', 'userOrganizer'])
  if SHOW_GROUPS:
    fieldnames.extend(['groupCommenterCount', 'groupCommenter',
                       'groupReaderCount', 'groupReader',
                       'groupWriterCount', 'groupWriter',
                       'groupFileorganizerCount', 'groupFileorganizer',
                       'groupOrganizerCount', 'groupOrganizer'])
  if SHOW_DOMAINS:
    fieldnames.extend(['domainCommenterCount', 'domainCommenter',
                       'domainReaderCount', 'domainReader',
                       'domainWriterCount', 'domainWriter'])
    fieldnames.extend(['domainWithlinkCommenterCount', 'domainWithlinkCommenter',
                       'domainWithlinkReaderCount', 'domainWithlinkReader',
                       'domainWithlinkWriterCount', 'domainWithlinkWriter'])
  if SHOW_ANYONES:
    fieldnames.extend(['anyoneCommenterCount', 'anyoneCommenter',
                       'anyoneReaderCount', 'anyoneReader',
                       'anyoneWriterCount', 'anyoneWriter'])
    fieldnames.extend(['anyoneWithlinkCommenterCount', 'anyoneWithlinkCommenter',
                       'anyoneWithlinkReaderCount', 'anyoneWithlinkReader',
                       'anyoneWithlinkWriterCount', 'anyoneWithlinkWriter'])
else:
  if SHOW_USERS:
    fieldnames.extend(['userCommenter',
                       'userReader',
                       'userWriter',
                       'userFileorganizer',
                       'userOrganizer'])
  if SHOW_GROUPS:
    fieldnames.extend(['groupCommenter',
                       'groupReader',
                       'groupWriter',
                       'groupFileorganizer',
                       'groupOrganizer'])
  if SHOW_DOMAINS:
    fieldnames.extend(['domainCommenter',
                       'domainReader',
                       'domainWriter'])
    fieldnames.extend(['domainWithlinkCommenter',
                       'domainWithlinkReader',
                       'domainWithlinkWriter'])
  if SHOW_ANYONES:
    fieldnames.extend(['anyoneCommenter',
                       'anyoneReader',
                       'anyoneWriter'])
    fieldnames.extend(['anyoneWithlinkCommenter',
                       'anyoneWithlinkReader',
                       'anyoneWithlinkWriter'])

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, fieldnames, lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin

for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  permCounts = copy.deepcopy(ZERO_COUNTS)
  for k, v in iter(row.items()):
    mg = PERMISSIONS_N_TYPE.match(k)
    if mg and v:
      permissions_N = mg.group(1)
      role = row[f'permissions.{permissions_N}.role']
      if role == 'owner':
        continue
      if v in ['user', 'group']:
        permCounts[v][role]['count'] += 1
        permCounts[v][role]['addresses'].append(row[f'permissions.{permissions_N}.emailAddress'].lower())
        continue
      if v == 'domain':
        if not row.get(f'permissions.{permissions_N}.allowFileDiscovery',
                       str(row.get(f'permissions.{permissions_N}.withLink') == 'False')):
          v = 'domainWithlink'
        permCounts[v][role]['count'] += 1
        permCounts[v][role]['addresses'].append(row[f'permissions.{permissions_N}.domain'])
        continue
      # if v == 'anyone'
      if not row.get(f'permissions.{permissions_N}.allowFileDiscovery',
                     str(row.get(f'permissions.{permissions_N}.withLink') == 'False')):
        v = 'anyoneWithlink'
      permCounts[v][role]['count'] += 1
  orow = {'Owner': row['owners.0.emailAddress'],
          'driveFileId': row['id'],
          'driveFileTitle': row.get(FILE_NAME, row.get(ALT_FILE_NAME, 'Unknown')),
          'mimeType': row['mimeType']}
  if SHOW_USERS:
    atype = 'user'
    for role in USER_GROUP_ROLES:
      atypeRole = f'{atype}{role.capitalize()}'
      if SHOW_COUNTS:
        orow[f'{atypeRole}Count'] = permCounts[atype][role]['count']
      orow[atypeRole] = LIST_DELIMITER.join(permCounts[atype][role]['addresses'])
  if SHOW_GROUPS:
    atype = 'group'
    for role in USER_GROUP_ROLES:
      atypeRole = f'{atype}{role.capitalize()}'
      if SHOW_COUNTS:
        orow[f'{atypeRole}Count'] = permCounts[atype][role]['count']
      orow[atypeRole] = LIST_DELIMITER.join(permCounts[atype][role]['addresses'])
  if SHOW_DOMAINS:
    for atype in ['domain', 'domainWithlink']:
      for role in DOMAIN_ANYONE_ROLES:
        atypeRole = f'{atype}{role.capitalize()}'
        if SHOW_COUNTS:
          orow[f'{atypeRole}Count'] = permCounts[atype][role]['count']
        orow[atypeRole] = LIST_DELIMITER.join(permCounts[atype][role]['addresses'])
  if SHOW_ANYONES:
    for atype in ['anyone', 'anyoneWithlink']:
      for role in DOMAIN_ANYONE_ROLES:
        atypeRole = f'{atype}{role.capitalize()}'
        if SHOW_COUNTS:
          orow[f'{atypeRole}Count'] = permCounts[atype][role]['count']
  outputCSV.writerow(orow)

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
