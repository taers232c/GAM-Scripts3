#!/usr/bin/env python3
"""
# Purpose: For a Google Drive User(s), delete all drive file ACLs for files shared with a list of specified domains
# Note: This script can use Basic or Advanced GAM:
#	https://github.com/jay0lee/GAM
#	https://github.com/taers232c/GAMADV-X, https://github.com/taers232c/GAMADV-XTD, https://github.com/taers232c/GAMADV-XTD3
# Customize: Set FILE_NAME and ALT_FILE_NAME based on your environment. Set DOMAIN_LIST.
# Usage:
# 1: Get ACLs for all files, if you don't want all users, replace all users with your user selection in the command below
#  $ Example, Basic GAM: gam all users print filelist id title permissions > filelistperms.csv
#  $ Example, Advanced GAM: gam config auto_batch_min 1 redirect csv ./filelistperms.csv multiprocess all users print filelist id title permissions
# 2: From that list of ACLs, output a CSV file with headers "Owner,driveFileId,driveFileTitle,permissionId,role,domain,withLink"
#    that lists the driveFileIds and permissionIds for all ACLs except those from the specified domains.
#    (n.b., role, type, emailAddress and title are not used in the next step, they are included for documentation purposes)
#  $ python GetSharedWithDomainDriveACLs.py filelistperms.csv deleteperms.csv
# 3: Inspect deleteperms.csv, verify that it makes sense and then proceed
# 4: Delete the ACLs
#  $ gam csv deleteperms.csv gam user "~Owner" delete drivefileacl "~driveFileId" "~permissionId"
"""

import csv
import re
import sys

# For GAM, GAMADV-X or GAMADVX-TD/GAMADVX-TD3 with drive_v3_native_names = false
FILE_NAME = 'title'
ALT_FILE_NAME = 'name'
# For GAMADVX-TD/GAMADVX-TD3 with drive_v3_native_names = true
#FILE_NAME = 'name'
#ALT_FILE_NAME = 'title'

# Substitute your domain(s) in the list below, e.g., DOMAIN_LIST = ['domain.com',] DOMAIN_LIST = ['domain1.com', 'domain2.com',]
DOMAIN_LIST = ['domain.com',]
# Specify desired value of withLink field: True, False, Any (matches True and False)
DESIRED_WITHLINK = 'Any'

PERMISSIONS_N_TYPE = re.compile(r"permissions.(\d+).type")

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['Owner', 'driveFileId', 'driveFileTitle', 'permissionId', 'role', 'domain', 'withLink'], lineterminator='\n')
outputCSV.writeheader()

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin

for row in csv.DictReader(inputFile):
  for k, v in iter(row.items()):
    mg = PERMISSIONS_N_TYPE.match(k)
    if mg and v:
      permissions_N = mg.group(1)
      if v == 'domain':
        domain = row['permissions.{0}.domain'.format(permissions_N)]
        if domain in DOMAIN_LIST and (DESIRED_WITHLINK == 'Any' or DESIRED_WITHLINK == row['permissions.{0}.withLink'.format(permissions_N)]):
          outputCSV.writerow({'Owner': row['Owner'],
                              'driveFileId': row['id'],
                              'driveFileTitle': row.get(FILE_NAME, row.get(ALT_FILE_NAME, 'Unknown')),
                              'permissionId': 'id:{0}'.format(row['permissions.{0}.id'.format(permissions_N)]),
                              'role': row['permissions.{0}.role'.format(permissions_N)],
                              'domain': domain,
                              'withLink': row['permissions.{0}.withLink'.format(permissions_N)]})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
