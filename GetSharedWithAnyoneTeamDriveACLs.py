#!/usr/bin/env python3
"""
# Purpose: For a Google Drive User(s), delete all drive file ACLs for Team Drive files shared with anyone
# Note: This script requires Advanced GAM:
#	https://github.com/taers232c/GAMADV-XTD3
# Customize: Set DOMAIN_LIST and DESIRED_ALLOWFILEDISCOVERY
# Usage:
# For all Team Drives, start at step 1; For Team Drives selected by user/group/OU, start at step 7
# All Team Drives
# 1: Get all Team Drives.
#  $ gam redirect csv ./TeamDrives.csv print teamdrives fields id,name
# 2: Get ACLs for all Team Drives
#  $ gam redirect csv ./TeamDriveACLs.csv multiprocess csv TeamDrives.csv gam print drivefileacls ~id fields emailaddress,role,type
# 3: Customize GetTeamDriveOrganizers.py for this task:
#    Set DOMAIN_LIST as required
#    Set ONE_ORGANIZER = True
#    Set SHOW_GROUP_ORGANIZERS = False
#    Set SHOW_USER_ORGANIZERS = True
# 4: From that list of ACLs, output a CSV file with headers "id,name,organizers"
#    that shows the organizers for each Team Drive
#  $ python GetTeamDriveOrganizers.py TeamDriveACLs.csv TeamDrives.csv TeamDriveOrganizers.csv
# 5: Get ACLs for all team drive files; you can use permission matching to narrow the number of files listed; add to the end of the command line
#    DESIRED_ALLOWFILEDISCOVERY = 'Any' - pm type anyone em
#    DESIRED_ALLOWFILEDISCOVERY = 'True' - pm type anyone allowfilediscovery true em
#    DESIRED_ALLOWFILEDISCOVERY = 'False' - pm type anyone allowfilediscovery false em
#  $ gam redirect csv ./filelistperms.csv multiprocess csv TeamDriveOrganizers.csv gam user ~organizers print filelist select teamdriveid ~id fields teamdriveid,id,title,permissions pm type anyone em
# 6: Go to step 11
# Selected Team Drives
# 7: If want Team Drives for a specific set of organizers, replace <UserTypeEntity> with your user selection in the command below
#  $ gam redirect csv ./AllTeamDrives.csv <UserTypeEntity> print teamdrives role organizer fields id,name
# 8: Customize DeleteDuplicateRows.py for this task:
#    Set ID_FIELD = 'id'
# 9: Delete duplicate Team Drives (some may have multiple organizers).
#  $ python DeleteDuplicateRows.py ./AllTeamDrives.csv ./TeamDrives.csv
# 10: Get ACLs for all team drive files; you can use permission matching to narrow the number of files listed; add to the end of the command line
#    DESIRED_ALLOWFILEDISCOVERY = 'Any' - pm type anyone em
#    DESIRED_ALLOWFILEDISCOVERY = 'True' - pm type anyone allowfilediscovery true em
#    DESIRED_ALLOWFILEDISCOVERY = 'False' - pm type anyone allowfilediscovery false em
#  $ gam redirect csv ./filelistperms.csv multiprocess csv TeamDrives.csv gam user ~User print filelist select teamdriveid ~id fields teamdriveid,id,title,permissions pm type anyone em
# Common code
# 11: From that list of ACLs, output a CSV file with headers "Owner,driveFileId,driveFileTitle,permissionId,role,allowFileDiscovery"
#    that lists the driveFileIds and permissionIds for all ACLs shared with anyone
#    (n.b., driveFileTitle, role and allowFileDiscovery are not used in the next step, they are included for documentation purposes)
#  $ python GetSharedWithAnyoneTeamDriveACLs.py filelistperms.csv deleteperms.csv
# 12: Inspect deleteperms.csv, verify that it makes sense and then proceed
# 13: Delete the ACLs
#  $ gam csv deleteperms.csv gam user "~Owner" delete drivefileacl "~driveFileId" "~permissionId"
"""

import csv
import re
import sys

FILE_NAME = 'name'
ALT_FILE_NAME = 'title'

# Specify desired value of allowFileDiscovery field: True, False, Any (matches True and False)
# allowFileDiscovery False = withLink True
# allowFileDiscovery True = withLink False
DESIRED_ALLOWFILEDISCOVERY = 'Any'

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

PERMISSIONS_N_TYPE = re.compile(r"permissions.(\d+).type")

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['Owner', 'driveFileId', 'driveFileTitle', 'permissionId', 'role', 'allowFileDiscovery'], lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin

for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  for k, v in iter(row.items()):
    mg = PERMISSIONS_N_TYPE.match(k)
    if mg and v == 'anyone':
      permissions_N = mg.group(1)
      allowFileDiscovery = row.get(f'permissions.{permissions_N}.allowFileDiscovery', str(row.get(f'permissions.{permissions_N}.withLink') == 'False'))
      if DESIRED_ALLOWFILEDISCOVERY in ('Any', allowFileDiscovery):
        outputCSV.writerow({'Owner': row['Owner'],
                            'driveFileId': row['id'],
                            'driveFileTitle': row.get(FILE_NAME, row.get(ALT_FILE_NAME, 'Unknown')),
                            'permissionId': f'id:{row[f"permissions.{permissions_N}.id"]}',
                            'role': row[f'permissions.{permissions_N}.role'],
                            'allowFileDiscovery': allowFileDiscovery})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
