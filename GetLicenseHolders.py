#!/usr/bin/env python3
"""
# Purpose: From a collection of users, show the ones holding licenses.
# Note: This script can use Basic or Advanced GAM:
#	https://github.com/GAM-team/GAM
#	https://github.com/taers232c/GAMADV-XTD3
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Get Licenses, all or selected
#  $ gam print licenses > Licenses.csv
#  $ gam print licenses sku <SKUIDList> > Licenses.csv
# 2: Get Users
#    Basic GAM: gam print users [domain <DomainName>] [(query <QueryUser>)|(queries <QueryUserList>)] > Users.csv
#    Advanced GAM: gam redirect csv ./Users.csv <UserTypeEntity> print users primaryEmail
# 3: From those lists of Licenses and Users, output a CSV file showing the licenses held by users in Users.csv
#  $ python3 GetLicenseHolders.py ./Licenses.csv ./Users.csv ./LicenseHolders.csv
# 4: Inspect LicenseHolders.csv, verify that it makes sense and then proceed if desired
# 5: Process LicenseHolders.csv
#    Delete licenses: gam csv ./LicenseHolders.csv gam user "~userId" delete license "~skuId"
#    Update licenses: gam csv ./LicenseHolders.csv gam user "~userId" update license <SKUID> from "~skuId"
"""

import csv
import sys

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

licenses = {}
inputFile = open(sys.argv[1], 'r', encoding='utf-8')
inputCSV = csv.DictReader(inputFile, quotechar=QUOTE_CHAR)
licenseFieldNames = inputCSV.fieldnames
for row in inputCSV:
  user = row['userId']
  licenses.setdefault(user, [])
  licenses[user].append(row)
inputFile.close()

if sys.argv[2] != '-':
  inputFile = open(sys.argv[2], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin
inputCSV = csv.DictReader(inputFile, quotechar=QUOTE_CHAR)

if (len(sys.argv) > 3) and (sys.argv[3] != '-'):
  outputFile = open(sys.argv[3], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, licenseFieldNames, lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

for row in inputCSV:
  for userLicense in licenses.get(row['primaryEmail'], []):
    outputCSV.writerow(userLicense)

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
