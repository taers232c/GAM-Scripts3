#!/usr/bin/env python3
"""
# Purpose: Delete all drive file ACLs for Team Drives shared outside of a list of specified domains
# Note: This script requires Advanced GAM:
#	https://github.com/taers232c/GAMADV-XTD3
#          You specify a list of domains, DOMAIN_LIST, and indicate whether this list is exclusive/inclusive
#          EXCLUSIVE_DOMAINS = True: exclude domains in DOMAIN_LIST from the output
#          EXCLUSIVE_DOMAINS = False: include domains in DOMAIN_LIST in the output
#          You can include/exclude shares to anyone in the ouput
#          INCLUDE_ANYONE = True: include shares to anyone in the output
#          INCLUDE_ANYONE = False: exclude shares to anyone from the output
# Customize: Set DOMAIN_LIST, EXCLUSIVE_DOMAINS, INCLUDE_ANYONE
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Get all Team Drives
#  $ gam redirect csv ./TeamDrives.csv print teamdrives
# 1: Get ACLs for all Team Drives
#  $ gam redirect csv ./TeamDriveACLs.csv multiprocess csv ./TeamDrives.csv gam print drivefileacls teamdriveid ~id fields id,domain,emailaddress,role,type,deleted
# 2: From that list of ACLs, output a CSV file with headers "teamDriveId,permissionId,role,type,emailAddress,domain"
#    that lists the driveFileIds and permissionIds for all ACLs except those from the specified domains.
#    (n.b., role, type, emailAddress and domain are not used in the next step, they are included for documentation purposes)
#  $ python3 GetNonDomainTeamDriveACLs.py ./TeamDriveACLs.csv DeleteTeamDriveACLs.csv
# 3: Inspect DeleteTeamDriveACLs.csv, verify that it makes sense and then proceed
# 4: If desired, delete the ACLs
#  $ gam redirect stdout ./deletetdacls.out multiprocess redirect stderr stdout multiprocess csv DeleteTeamDriveACLs.csv gam delete drivefileacl teamdriveid "~teamDriveId" "~permissionId"
"""

import csv
import re
import sys

# Substitute your domain(s) in the list below, e.g., DOMAIN_LIST = ['domain.com',] DOMAIN_LIST = ['domain1.com', 'domain2.com',]
DOMAIN_LIST = ['domain.com',]
# Indicate whether the list is exclusive or inclusive
EXCLUSIVE_DOMAINS = True
# Indicate whether shares to anyone should be included
INCLUDE_ANYONE = True

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

PERMISSIONS_N_TYPE = re.compile(r"permissions.(\d+).type")

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['teamDriveId', 'permissionId', 'role', 'type', 'emailAddress', 'domain'], lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin

for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  for k, v in iter(row.items()):
    mg = PERMISSIONS_N_TYPE.match(k)
    if mg and v:
      permissions_N = mg.group(1)
      if v == 'domain':
        domain = row[f'permissions.{permissions_N}.domain']
        emailAddress = ''
      elif v in ['user', 'group']:
        if row.get(f'permissions.{permissions_N}.deleted') == 'True':
          continue
        emailAddress = row[f'permissions.{permissions_N}.emailAddress']
        domain = emailAddress[emailAddress.find('@')+1:]
      else: #anyone
        if not INCLUDE_ANYONE:
          continue
        emailAddress = ''
        domain = ''
      if ((v == 'anyone') or # Can only be true is INCLUDE_ANYONE = True
          (EXCLUSIVE_DOMAINS and domain not in DOMAIN_LIST) or
          (not EXCLUSIVE_DOMAINS and domain in DOMAIN_LIST)):
        outputCSV.writerow({'teamDriveId': row['id'],
                            'permissionId': f'id:{row[f"permissions.{permissions_N}.id"]}',
                            'role': row[f'permissions.{permissions_N}.role'],
                            'type': v,
                            'emailAddress': emailAddress,
                            'domain': domain})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
