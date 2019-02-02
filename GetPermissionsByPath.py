#!/usr/bin/env python3
"""
# Purpose: For a Google Drive User, show all drive file ACLs except those indicating the user as owner, one ACL per row per file path
# Note: This script requires Advanced GAM:
#	https://github.com/taers232c/GAMADV-X, https://github.com/taers232c/GAMADV-XTD, https://github.com/taers232c/GAMADV-XTD3
# Customize: Set FILE_NAME and ALT_FILE_NAME based on your environment.
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

# For GAMADV-X or GAMADVX-TD/GAMADVX-TD3 with drive_v3_native_names = false
FILE_NAME = 'title'
ALT_FILE_NAME = 'name'
# For GAMADVX-TD/GAMADVX-TD3 with drive_v3_native_names = true
#FILE_NAME = 'name'
#ALT_FILE_NAME = 'title'

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

PERMISSIONS_N_TYPE = re.compile(r"permissions.(\d+).type")

def getWithLink(r, n):
  withLink = r.get('permissions.{0}.withLink'.format(n))
  if withLink is not None:
    return withLink == u'True'
  withLink = r.get('permissions.{0}.allowFileDiscovery'.format(n))
  if withLink is not None:
    return withLink == u'False'
  return False

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w', newline='', encoding='utf-8')
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
      pathList.append(row['path.{0}'.format(p)])
  else:
    pathList = [row.get(FILE_NAME, row.get(ALT_FILE_NAME, 'Unknown'))]
  for k, v in iter(row.items()):
    mg = PERMISSIONS_N_TYPE.match(k)
    if mg and v:
      permissions_N = mg.group(1)
      if v == u'domain':
        value = row['permissions.{0}.domain'.format(permissions_N)]
        if getWithLink(row, permissions_N):
          v += 'WithLink'
      elif v in ['user', 'group']:
        if row['permissions.{0}.deleted'.format(permissions_N)] == u'True':
          continue
        value = row['permissions.{0}.emailAddress'.format(permissions_N)]
      else:
        value = ''
        if getWithLink(row, permissions_N):
          v += 'WithLink'
      role = row['permissions.{0}.role'.format(permissions_N)]
      if v != 'user' or role != 'owner' or value != row['Owner']:
        for path in pathList:
          pathPerms.append({'path': path, 'type': v, 'value': value, 'role': role})
outputCSV.writerows(sorted(pathPerms, key=lambda row: row['path']))

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
