#!/usr/bin/env python33!!!
"""
# Purpose: For a Google Drive User(s), delete all drive file ACls for files shared outside of a list of specified domains
# Note: This script can use basic GAM: https://github.com/jay0lee/GAM or advanced GAM: https://github.com/taers232c/GAMADV-X
# Usage:
# 1: Get ACLS for all files, if you don't want all users, replace all users with your user selection in the command below
#  $ Example, Basic GAM: gam all users print filelist id title permissions > filelistperms.csv
#  $ Example, advanced GAM: gam config auto_batch_min 1 redirect csv ./filelistperms.csv multiprocess all users print filelist id title permissions
# 2: From that list of ACLs, output a CSV file with headers "Owner,driveFileId,driveFileTitle,permissionId,role,type,emailAddress"
#    that lists the driveFileIds and permissionIds for all ACls except those from the specified domains.
#    (n.b., role, type, emailAddress and title are not used in the next step, they are included for documentation purposes)
#  $ python GetNonDomainDriveACLs.py filelistperms.csv deleteperms.csv
# 3: Inspect deleteperms.csv, verify that it makes sense and then proceed
# 4: Delete the ACLS
#  $ gam csv deleteperms.csv gam user "~Owner" delete drivefileacl "~driveFileId" "~permissionId"
"""

import csv
import re
import sys

email_n_address = re.compile(r"permissions.(\d+).emailAddress")
# Substitute your domain(s) in the list below, e.g., domainList = ['domain.com',] domainList = ['domain1.com', 'domain2.com',]
domainList = []

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w')
else:
  outputFile = sys.stdout
outputFile.write('Owner,driveFileId,driveFileTitle,permissionId,role,type,emailAddress\n')
if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r')
else:
  inputFile = sys.stdin

for row in csv.DictReader(inputFile):
  for k, v in iter(row.items()):
    mg = email_n_address.match(k)
    if mg and v:
      perm_group = mg.group(1)
      if row['permissions.{0}.domain'.format(perm_group)] not in domainList:
        outputFile.write('{0},{1},{2},id:{3},{4},{5},{6}\n'.format(row['Owner'],
                                                                   row['id'],
                                                                   row['title'],
                                                                   row['permissions.{0}.id'.format(perm_group)],
                                                                   row['permissions.{0}.role'.format(perm_group)],
                                                                   row['permissions.{0}.type'.format(perm_group)],
                                                                   v))

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
