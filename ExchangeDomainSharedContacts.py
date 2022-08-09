#!/usr/bin/env python3
"""
# Purpose: Make all users in DomainB be domain shared contacts in DomainA and all users in DomainA be domain shared contacts in DomainB
# Note: This script requires Advanced GAM:
#	https://github.com/taers232c/GAMADV-XTD3
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# Make DomainB users be domain shared contacts in DomainA
# 1: Generate the two data files, DomainB users and DomainA domain shared contacts
#  $ gam select DomainB redirect csv ./DomainBUsers.csv print users fields primaryemail,name
#  $ gam select DomainA redirect csv ./DomainAContacts.csv print contacts fields email,familyname,givenname,name emailmatchpattern ".*@DomainB.com$"
# 2: Find add, deletes, updates for DomainA domain shared contacts
#  $ python3 ExchangeDomainSharedContacts.py DomainB.com ./DomainBUsers.csv ./DomainAContacts.csv ./DomainAContactUpdates.csv
$ 3: Perform updates for DomainA domain shared contacts
#  $ gam select DomainA redirect stdout ./DomainAContactDeletes.txt redirect stderr stdout loop ./DomainAContactUpdates.csv matchfield Action Delete gam delete contact "~ContactID"
#  $ gam select DomainA redirect stdout ./DomainAContactUpdates.txt redirect stderr stdout loop ./DomainAContactUpdates.csv matchfield Action Update gam update contact "~ContactID" givenName "~givenName" familyname "~familyName" name "~fullName"
#  $ gam select DomainA redirect stdout ./DomainAContactAdds.txt redirect stderr stdout loop ./DomainAContactUpdates.csv matchfield Action Add gam create contact email work '~ContactID' primary givenName "~givenName" familyname "~familyName" name "~fullName"
# Make DomainA users be domain shared contacts in DomainB
# 1: Generate the two data files, DomainA users and DomainB domain shared contacts
#  $ gam select DomainA redirect csv ./DomainAUsers.csv print users fields primaryemail,name
#  $ gam select DomainB redirect csv ./DomainBContacts.csv print contacts fields email,familyname,givenname,name emailmatchpattern ".*@DomainA.com$"
# 2: Find add, deletes, updates for DomainB domain shared contacts
#  $ python3 ExchangeDomainSharedContacts.py DomainA.com ./DomainAUsers.csv ./DomainBContacts.csv ./DomainBContactUpdates.csv
$ 3: Perform updates for DomainB domain shared contacts
#  $ gam select DomainB redirect stdout ./DomainBContactDeletes.txt redirect stderr stdout loop ./DomainBContactUpdates.csv matchfield Action Delete gam delete contact "~ContactID"
#  $ gam select DomainB redirect stdout ./DomainBContactUpdates.txt redirect stderr stdout loop ./DomainBContactUpdates.csv matchfield Action Update gam update contact "~ContactID" givenName "~givenName" familyname "~familyName" name "~fullName"
#  $ gam select DomainB redirect stdout ./DomainBContactAdds.txt redirect stderr stdout loop ./DomainBContactUpdates.csv matchfield Action Add gam create contact email work '~ContactID' primary givenName "~givenName" familyname "~familyName" name "~fullName"
"""

import csv
import sys

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

CONTACTID = 'ContactID'
GIVENNAME = 'givenName'
FAMILYNAME = 'familyName'
FULLNAME = 'fullName'

userDomains = set(sys.argv[1].lower().replace(',', ' ').split())

userData = {}
userSet = set()
with open(sys.argv[2], 'r', encoding='utf-8') as inputFile:
  for user in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
    emailAddress = user['primaryEmail'].lower()
    _, domain = emailAddress.split('@')
    if domain in userDomains:
      userData[emailAddress] = {GIVENNAME: user[f'name.{GIVENNAME}'].strip(), FAMILYNAME: user[f'name.{FAMILYNAME}'].strip(),
                                FULLNAME: user[f'name.{FULLNAME}'].strip()}
      userSet.add(emailAddress)

contactData = {}
contactSet = set()
with open(sys.argv[3], 'r', encoding='utf-8') as inputFile:
  for contact in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
    emailAddress = contact['Emails.1.address'].lower()
    _, domain = emailAddress.split('@')
    if domain in userDomains:
      contactData[emailAddress] = {GIVENNAME: contact['Given Name'].strip(), FAMILYNAME: contact['Family Name'].strip(),
                                   FULLNAME: contact['Name'].strip(), CONTACTID: contact[CONTACTID]}
      contactSet.add(emailAddress)

addContacts = userSet-contactSet
delContacts = contactSet-userSet
chkContacts = contactSet-delContacts

with open(sys.argv[4], 'w', encoding='utf-8', newline='') as outputFile:
  outputCSV = csv.DictWriter(outputFile, ['Action', CONTACTID, GIVENNAME, FAMILYNAME, FULLNAME],
                             lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
  outputCSV.writeheader()
  for emailAddress in sorted(delContacts):
    contact = contactData[emailAddress]
    outputCSV.writerow({'Action': 'Delete',
                        CONTACTID: contact[CONTACTID],
                        GIVENNAME: contact[GIVENNAME],
                        FAMILYNAME: contact[FAMILYNAME],
                        FULLNAME: contact[FULLNAME]})
  for emailAddress in sorted(chkContacts):
    user = userData[emailAddress]
    contact = contactData[emailAddress]
    for field in [GIVENNAME, FAMILYNAME, FULLNAME]:
      if user[field] != contact[field]:
        outputCSV.writerow({'Action': 'Update',
                            CONTACTID: contact[CONTACTID],
                            GIVENNAME: user[GIVENNAME],
                            FAMILYNAME: user[FAMILYNAME],
                            FULLNAME: user[FULLNAME]})
        break
  for emailAddress in sorted(addContacts):
    user = userData[emailAddress]
    outputCSV.writerow({'Action': 'Add',
                        CONTACTID: emailAddress,
                        GIVENNAME: user[GIVENNAME],
                        FAMILYNAME: user[FAMILYNAME],
                        FULLNAME: user[FULLNAME]})
