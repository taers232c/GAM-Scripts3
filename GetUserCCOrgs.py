#!/usr/bin/env python3
"""
# Purpose: Move root users to an Org Unit based on their work address countryCode
# Note: This script requires Advanced GAM:
#	https://github.com/taers232c/GAMADV-XTD3
# Customize: Set ORG_UNIT_FORMAT_MAP or ORG_UNIT_DICT_MAP
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Get primaryEmail, orgUnitPath, addresses for all root users
#  $ gam redirect csv ./UserAddresses.csv org "/" print users fields primaryemail,orgunitpath,addresses
# 2: From that list of users, output a CSV file with headers "Org,primaryEmail"
#    that lists the Org Unit derived from the root user's work address and their primaryEmail
#  $ python3 GetUserCCOrgs.py ./UserAddresses.csv ./UserCCOrgs.csv
# 3: Inspect UserCCOrgs.csv, verify that it makes sense and then proceed
# 4: Move the users
#  $ gam update orgs csvkmd ./UserCCOrgs.csv keyfield Org datafield primaryEmail add csvdata primaryEmail
"""

import csv
import re
import sys

# If you simply want to substitute the country code into a string that defines the OU,
# use ORG_UNIT_FORMAT_MAP, Change the format as desired, {0} is replaced by countryCode
# For example, ORG_UNIT_FORMAT_MAP = '/SalesByCountry/{0}'
ORG_UNIT_FORMAT_MAP = '{0}'

# If you want to map the country codes to OUs in a more cmplex manner, use ORG_UNIT_DICT_MAP.
# For example, ORG_UNIT_DICT_MAP = {'US': '/SalesByCountry/UnitedStates', 'CA': '/SalesByCountry/Canada'}
ORG_UNIT_DICT_MAP = {}

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

ADDRESSES_N_TYPE = re.compile(r"addresses.(\d+).type")

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['Org', 'primaryEmail'], lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin

for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  if row['orgUnitPath'] == '/':
    for k, v in iter(row.items()):
      mg = ADDRESSES_N_TYPE.match(k)
      if mg and v == 'work':
        addresses_N = mg.group(1)
        cc = row[f'addresses.{addresses_N}.countryCode']
        if cc:
          if ORG_UNIT_DICT_MAP:
            org = ORG_UNIT_DICT_MAP.get(cc, None)
            if org:
              outputCSV.writerow({'Org': org, 'primaryEmail': row['primaryEmail']})
              break
            sys.stderr.write(f'ERROR: No OU for country code {cc} for user {row["primaryEmail"]}\n')
          else:
            outputCSV.writerow({'Org': ORG_UNIT_FORMAT_MAP.format(cc), 'primaryEmail': row['primaryEmail']})
            break

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
