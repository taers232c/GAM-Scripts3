#!/usr/bin/env python3
"""
# Purpose: For a Google Drive User(s), get all drive file ACLs for Team Drive files shared with a list of specified domains
# Note: This script requires Advanced GAM:
#	https://github.com/taers232c/GAMADV-XTD3
# Customize: Set DOMAIN_LIST, DESIRED_ALLOWFILEDISCOVERY, NON_INHERITED_ACLS_ONLY
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# For all Team Drives, start at step 1; For Team Drives selected by user/group/OU, start at step 7
# All Team Drives
# 1: Get all Team Drives.
#  $ gam redirect csv ./TeamDrives.csv print teamdrives fields id,name
# 2: Get ACLs for all Team Drives
#  $ gam redirect csv ./TeamDriveACLs.csv multiprocess csv ./TeamDrives.csv gam print drivefileacls "~id" fields emailaddress,role,type
# 3: Customize GetTeamDriveOrganizers.py for this task:
#    Set DOMAIN_LIST as required
#    Set ONE_ORGANIZER = True
#    Set SHOW_GROUP_ORGANIZERS = False
#    Set SHOW_USER_ORGANIZERS = True
# 4: From that list of ACLs, output a CSV file with headers "id,name,organizers"
#    that shows the organizers for each Team Drive
#  $ python3 GetTeamDriveOrganizers.py TeamDriveACLs.csv TeamDrives.csv TeamDriveOrganizers.csv
# 5: Get ACLs for all team drive files; you can use permission matching to narrow the number of files listed; add to the end of the command line
#    You can minimize the number of files downloaded by using a query with the visibility keyword.
#    DESIRED_ALLOWFILEDISCOVERY = 'Any' - query "(visibility='domainCanFind' or visibility='domainWithLink')"
#    DESIRED_ALLOWFILEDISCOVERY = 'True' - query "visibility='domainCanFind'"
#    DESIRED_ALLOWFILEDISCOVERY = 'False' - query "visibility='domainWithLink'"
#    Change the query as desired.
#    Note!!! The visibility query will find files shared to your primary domain; it will not find files shared only to other domains.
#    If you are looking for ACLs referencing specific domains, list them in DOMAIN_LIST.
#    Add the following clause to the command for each domain: pm type domain domain xyz.com em
#  $ gam redirect csv ./filelistperms.csv multiprocess csv ./TeamDriveOrganizers.csv gam user "~organizers" print filelist select teamdriveid "~id" fields teamdriveid,id,name,permissions,mimetype <PutQueryHere>
# 6: Go to step 11
# Selected Team Drives
# 7: If you want Team Drives for a specific set of organizers, replace <UserTypeEntity> with your user selection in the command below
#  $ gam redirect csv ./AllTeamDrives.csv <UserTypeEntity> print teamdrives role organizer fields id,name
# 8: Customize DeleteDuplicateRows.py for this task:
#    Set ID_FIELD = 'id'
# 9: Delete duplicate Team Drives (some may have multiple organizers).
#  $ python3 DeleteDuplicateRows.py ./AllTeamDrives.csv ./TeamDrives.csv
# 10: Get ACLs for all team drive files; you can use permission matching to narrow the number of files listed; add to the end of the command line
#    You can minimize the number of files downloaded by using a query with the visibility keyword.
#    DESIRED_ALLOWFILEDISCOVERY = 'Any' - query "(visibility='domainCanFind' or visibility='domainWithLink')"
#    DESIRED_ALLOWFILEDISCOVERY = 'True' - query "visibility='domainCanFind'"
#    DESIRED_ALLOWFILEDISCOVERY = 'False' - query "visibility='domainWithLink'"
#    Change the query as desired.
#    Note!!! The visibility query will find files shared to your primary domain; it will not find files shared only to other domains.
#    If you are looking for ACLs referencing specific domains, list them in DOMAIN_LIST.
#    Add the following clause to the command for each domain: pm type domain domain xyz.com em
#  $ gam redirect csv ./filelistperms.csv multiprocess csv ./TeamDrives.csv gam user "~User" print filelist select teamdriveid "~id" fields teamdriveid,id,name,permissions,mimetype <PutQueryHere>
# Common code
# 11: From that list of ACLs, output a CSV file with headers "Owner,driveFileId,driveFileTitle,permissionId,role,domain,allowFileDiscovery"
#    that lists the driveFileIds and permissionIds for all ACLs shared with the selected domains.
#    (n.b., driveFileTitle, role, domain and allowFileDiscovery are not used in the next step, they are included for documentation purposes)
#  $ python3 GetSharedWithDomainTeamDriveACLs.py filelistperms.csv deleteperms.csv
# 12: Inspect deleteperms.csv, verify that it makes sense and then proceed
# 13: If desired, delete the ACLs
#  $ gam csv ./deleteperms.csv gam user "~Owner" delete drivefileacl "~driveFileId" "~permissionId"
"""

import csv
import re
import sys

FILE_NAME = 'name'
ALT_FILE_NAME = 'title'

# If you want to limit finding ACLS for a specific list of domains, use the list below, e.g., DOMAIN_LIST = ['domain.com',] DOMAIN_LIST = ['domain1.com', 'domain2.com',]
DOMAIN_LIST = []
# Specify desired value of allowFileDiscovery field: 'True', 'False', 'Any' (matches True and False)
DESIRED_ALLOWFILEDISCOVERY = 'Any'

# Specify whether only non-inherited ACLs should be output; inherited ACLs can't be deleted
NON_INHERITED_ACLS_ONLY = True

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

PERMISSIONS_N_TYPE = re.compile(r"permissions.(\d+).type")

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['Owner', 'driveFileId', 'driveFileTitle', 'mimeType', 'permissionId', 'role', 'domain', 'allowFileDiscovery'],
                           lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin

for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  for k, v in iter(row.items()):
    mg = PERMISSIONS_N_TYPE.match(k)
    if mg and v == 'domain':
      permissions_N = mg.group(1)
      if NON_INHERITED_ACLS_ONLY and str(row.get(f'permissions.{permissions_N}.permissionDetails.0.inherited', False)) == 'True':
        continue
      domain = row[f'permissions.{permissions_N}.domain']
      allowFileDiscovery = row.get(f'permissions.{permissions_N}.allowFileDiscovery', str(row.get(f'permissions.{permissions_N}.withLink') == 'False'))
      if (not DOMAIN_LIST or domain in DOMAIN_LIST) and (DESIRED_ALLOWFILEDISCOVERY in ('Any', allowFileDiscovery)):
        outputCSV.writerow({'Owner': row['Owner'],
                            'driveFileId': row['id'],
                            'driveFileTitle': row.get(FILE_NAME, row.get(ALT_FILE_NAME, 'Unknown')),
                            'mimeType': row['mimeType'],
                            'permissionId': f'id:{row[f"permissions.{permissions_N}.id"]}',
                            'role': row[f'permissions.{permissions_N}.role'],
                            'domain': domain,
                            'allowFileDiscovery': allowFileDiscovery})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
