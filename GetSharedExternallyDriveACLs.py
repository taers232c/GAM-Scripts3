#!/usr/bin/env python3
"""
# Purpose: For a Google Drive User(s), show all drive file ACLs for files shared outside of a list of specified domains
#          You specify a list of domains, DOMAIN_LIST, and indicate whether this list is exclusive/inclusive
#          EXCLUSIVE_DOMAINS = True: exclude domains in DOMAIN_LIST from the output
#          EXCLUSIVE_DOMAINS = False: include domains in DOMAIN_LIST in the output
#          You can include/exclude shares to anyone in the ouput
#          INCLUDE_ANYONE = True: include shares to anyone in the output
#          INCLUDE_ANYONE = False: exclude shares to anyone from the output
# Note: This script can use Basic or Advanced GAM:
#	https://github.com/jay0lee/GAM
#	https://github.com/taers232c/GAMADV-XTD3
# Customize: Set DOMAIN_LIST, EXCLUSIVE_DOMAINS, INCLUDE_ANYONE
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Get ACLs for all files, if you don't want all users, replace all users with your user selection in the command below
#  $ Basic GAM: gam all users print filelist id title permissions owners > filelistperms.csv
#  $ Advanced GAM: You can have GAM do some pre-filtering
#  $ EXCLUSIVE_DOMAINS = True:
#    Add the following clause to the command for each domain in DOMAIN_LIST: pm not domain domainx.com em
#  $ EXCLUSIVE_DOMAINS = False:
#    Add the following clause to the command for each domain in DOMAIN_LIST: pm domain domainx.com em
#  $ INCLUDE_ANYONE = True
#    Add the following clause to the command: pm type anyone em
#  $ gam config auto_batch_min 1 redirect csv ./filelistperms.csv multiprocess all users print filelist fields id,name,permissions,owners.emailaddress <pm clauses>
# 2: From that list of ACLs, output a CSV file with headers "Owner,driveFileId,driveFileTitle,permissionId,role,type,emailAddress,domain"
#    that lists the driveFileIds and permissionIds for all ACLs shared with the selected domains.
#    (n.b., role, type, emailAddress, domain and driveFileTitle are not used in the next step, they are included for documentation purposes)
#  $ python3 GetSharedExternallyDriveACLs.py filelistperms.csv deleteperms.csv
# 3: Inspect deleteperms.csv, verify that it makes sense and then proceed
# 4: If desired, delete the ACLs
#  $ gam csv deleteperms.csv gam user "~Owner" delete drivefileacl "~driveFileId" "~permissionId"
"""

import csv
import re
import sys

FILE_NAME = 'name'
ALT_FILE_NAME = 'title'

# Substitute your domain(s) in the list below, e.g., DOMAIN_LIST = ['domain.com',] DOMAIN_LIST = ['domain1.com', 'domain2.com',]
DOMAIN_LIST = ['domain.com']
# EXCLUSIVE_DOMAINS = True: You're interested only in domains not in DOMAIN_LIST which would typically be your internal domains
# EXCLUSIVE_DOMAINS = False: You're interested only in domains in DOMAIN_LIST which would typically be external domains
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
outputCSV = csv.DictWriter(outputFile, ['Owner', 'driveFileId', 'driveFileTitle',
                                        'permissionId', 'role', 'type', 'emailAddress', 'domain'],
                           lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
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
        emailAddress = ''
        domain = row[f'permissions.{permissions_N}.domain']
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
      if ((v == 'anyone') or # Can only be true if INCLUDE_ANYONE = True
          (EXCLUSIVE_DOMAINS and domain not in DOMAIN_LIST) or
          (not EXCLUSIVE_DOMAINS and domain in DOMAIN_LIST)):
        outputCSV.writerow({'Owner': row['owners.0.emailAddress'],
                            'driveFileId': row['id'],
                            'driveFileTitle': row.get(FILE_NAME, row.get(ALT_FILE_NAME, 'Unknown')),
                            'permissionId': f'id:{row[f"permissions.{permissions_N}.id"]}',
                            'role': row[f'permissions.{permissions_N}.role'],
                            'type': v,
                            'emailAddress': emailAddress,
                            'domain': domain})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
