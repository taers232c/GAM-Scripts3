#!/usr/bin/env python3
"""
# Purpose: Delete old contacts from user's personal contacts
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or  python3 -V
#  Python 3.x.y
# Usage:
# 1: Generate OldContacts.csv, header row primaryEmail, one email address per row
#    You can generate this file by hand, or, for example, if you have an OU of users to remove from all other user's contact lists,
#  $ gam redirect csv ./OldContacts.csv ou "/Path/to/OU" print users primaryemail
# 2: Get current contacts for all users, if you don't want all users, replace all users with your user selection in the command below
#  $ gam redirect csv ./CurrentContacts.csv all users print contacts fields email,name
# 3: From that list of user's contacts, output a CSV file with headers: User,ContactID,Name,Email
#    that shows user's contacts with an email address from OldContacts.csv
#  $ python3 DeleteOldContacts.py ./OldContacts.csv ./CurrentContacts.csv ./DeleteContacts.csv
# 4: Inspect DeleteContacts.csv, verify that it makes sense and then proceed
# 5: If desired, delete the contacts
#  $ gam csv DeleteContacts.csv gam user "~User" delete contact "~ContactID"
"""

import csv
import re
import sys

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

EMAILS_N_ADDRESS = re.compile(r"Emails.(\d+).address")

OldContacts = set()

inputFile = open(sys.argv[1], 'r', encoding='utf-8')
for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  OldContacts.add(row['primaryEmail'].lower())
inputFile.close()

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  inputFile = open(sys.argv[2], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin

if (len(sys.argv) > 3) and (sys.argv[3] != '-'):
  outputFile = open(sys.argv[3], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['User','ContactID','Name','Email'], lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  for k, v in iter(row.items()):
    mg = EMAILS_N_ADDRESS.match(k)
    if mg and v.lower() in OldContacts:
      outputCSV.writerow({'User': row['User'],
                          'ContactID': row['ContactID'],
                          'Name': row['Name'],
                          'Email': v})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
