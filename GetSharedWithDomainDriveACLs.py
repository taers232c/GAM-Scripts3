#!/usr/bin/env python3
"""
# Purpose: For a Google Drive User(s), delete all drive file ACLs for files shared with a list of specified domains
# Note: This script can use basic GAM: https://github.com/jay0lee/GAM or advanced GAM: https://github.com/taers232c/GAMADV-X
# Usage:
# 1: Get ACLs for all files, if you don't want all users, replace all users with your user selection in the command below
#  $ Example, Basic GAM: gam all users print filelist id title permissions > filelistperms.csv
#  $ Example, advanced GAM: gam config auto_batch_min 1 redirect csv ./filelistperms.csv multiprocess all users print filelist id title permissions
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

n_domain = re.compile(r"permissions.(\d+).domain")
# Substitute your domain(s) in the list below, e.g., domainList = ['domain.com',] domainList = ['domain1.com', 'domain2.com',]
domainList = []
# Specify desired value of withLink field: True, False, Any (matches True and False)
desiredWithLink = 'Any'

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['Owner', 'driveFileId', 'driveFileTitle', 'permissionId', 'role', 'domain', 'withLink'], lineterminator='\n')
outputCSV.writeheader()

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r')
else:
  inputFile = sys.stdin

for row in csv.DictReader(inputFile):
  for k, v in iter(row.items()):
    mg = n_domain.match(k)
    if mg and v:
      perm_group = mg.group(1)
      if ((row['permissions.{0}.type'.format(perm_group)] == 'domain')
          and (row['permissions.{0}.domain'.format(perm_group)] in domainList)
          and ((desiredWithLink == 'Any') or (desiredWithLink == row['permissions.{0}.withLink'.format(perm_group)]))):
        outputCSV.writerow({'Owner': row['Owner'],
                            'driveFileId': row['id'],
                            'driveFileTitle': row['title'],
                            'permissionId': 'id:{0}'.format(row['permissions.{0}.id'.format(perm_group)]),
                            'role': row['permissions.{0}.role'.format(perm_group)],
                            'domain': row['permissions.{0}.domain'.format(perm_group)],
                            'withLink': row['permissions.{0}.withLink'.format(perm_group)]})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
