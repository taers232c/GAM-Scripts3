#!/usr/bin/env python3
"""
# Purpose: For a Google Drive User, show all drive file ACLs except those indicating the user as owner, one ACL per row per file path
# Note: This script requires Advanced GAM:
#	https://github.com/taers232c/GAMADV-XTD3
# Usage:
# 1: Use print filelist to get selected ACLs
#    Syntax: gam <UserTypeEntity> print filelist [anyowner|(showownedby any|me|others)]
#		[query <QueryDriveFile>] [fullquery <QueryDriveFile>] [select <DriveFileEntity>|orphans] [depth <Number>] [showparent] [filepath|fullpath]
#    For a full description of print filelist, see: https://github.com/taers232c/GAMADV-XTD/wiki/Users-Drive-Files
#    Example: gam redirect csv ./filelistperms.csv user testuser@domain.com print filelist id title permissions fullpath
# 2: From that list of ACLs, output a CSV file with headers "path,type,value,role"
#    that lists the file path and ACL for all ACLs except those indicating the user as owner.
#    There is one row per ACL per file path
#  $ python GetPermissionsByPath.py filelistperms.csv pathperms.csv
"""

import csv
import re
import sys

FILE_NAME = 'name'
ALT_FILE_NAME = 'title'

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

PERMISSIONS_N_TYPE = re.compile(r"permissions.(\d+).type")

def getWithLink(r, n):
  withLink = r.get(f'permissions.{n}.withLink')
  if withLink is not None:
    return withLink == 'True'
  withLink = r.get(f'permissions.{n}.allowFileDiscovery')
  if withLink is not None:
    return withLink == 'False'
  return False

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['path', 'type', 'value', 'role'], lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin

pathPerms = []
for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  numPaths = int(row.get('paths', '0'))
  if numPaths > 0:
    pathList = []
    for p in range(0, numPaths):
      pathList.append(row[f'path.{p}'])
  else:
    pathList = [row.get(FILE_NAME, row.get(ALT_FILE_NAME, 'Unknown'))]
  for k, v in iter(row.items()):
    mg = PERMISSIONS_N_TYPE.match(k)
    if mg and v:
      permissions_N = mg.group(1)
      if v == 'domain':
        value = row[f'permissions.{permissions_N}.domain']
        if getWithLink(row, permissions_N):
          v += 'WithLink'
      elif v in ['user', 'group']:
        if row.get(f'permissions.{permissions_N}.deleted') == 'True':
          continue
        value = row[f'permissions.{permissions_N}.emailAddress']
      else:
        value = ''
        if getWithLink(row, permissions_N):
          v += 'WithLink'
      role = row[f'permissions.{permissions_N}.role']
      if v != 'user' or role != 'owner' or value != row['Owner']:
        for path in pathList:
          pathPerms.append({'path': path, 'type': v, 'value': value, 'role': role})
outputCSV.writerows(sorted(pathPerms, key=lambda row: row['path']))

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
