#!/usr/bin/env python3
"""
# Purpose: Generate adds/deletes/updates from files exported from an SMS
# Note: This script can use Basic or Advanced GAM:
#	https://github.com/GAM-team/GAM
#	https://github.com/taers232c/GAMADV-XTD3# Usage:
# Customize: Set the field and file names as required/desired
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Methodology:
# A previous export and a current export from the SMS are compared to find changes.
# If a user was not the the previous export and is in the current export, it can be added.
# If a user was in the previous export and is not in the current export, it can be deleted/suspended/ignored.
# If a user is in both exports but some key fields are different, it can be updated.
# If your SMS outputs a unique ID for each user, the script can detect email address changes,
# otherwise an email address change will be processed as an add and a delete/suspend which is probably
# not what you want.
#
# 1: Rename CurrUsers.csv to PrevUsers.csv
# 2: Export current data from SMS to CurrUsers.csv
# 3: Find the changes
#  $ python3 ./FindUserChanges.py
# 4: Do the deletes/suspends; substitute actual field names from SMS CSV file
#  $ gam csv DeleteUsers.csv gam delete user "~EMAIL_FIELD"
#    Rather than delete, you could suspend the users; you can optionally move the uses to a suspended OU
#  $ gam csv DeleteUsers.csv gam update user "~EMAIL_FIELD" suspended true
#  $ gam csv DeleteUsers.csv gam update user "~EMAIL_FIELD" suspended true ou /Suspended
# 5: Do the adds; substitute actual field names from SMS CSV file
#  $ gam csv AddUsers.csv gam create user "~EMAIL_FIELD" firstname "~FIRSTNAME_FIELD" lastname "~LASTNAME_FIELD" password "~PASSWORD_FIELD" ou "~ORGUNIT_FIELD"
# 6: Do the changes; substitute actual field names from SMS CSV file
#    Update users without an email address change
#  $ gam csv UpdateUsers.csv matchfield new-EMAIL_FIELD "" gam update user "~EMAIL_FIELD" firstname "~FIRSTNAME_FIELD" lastname "~LASTNAME_FIELD" password "~PASSWORD_FIELD" ou "~ORGUNIT_FIELD"
#    Update users with an email address change; previous email address is updated to new email address
#  $ gam csv UpdateUsers.csv skipfield new-EMAIL_FIELD "" gam update user "~EMAIL_FIELD" email "new-~~EMAIL_FIELD~~" firstname "~FIRSTNAME_FIELD" lastname "~LASTNAME_FIELD" password "~PASSWORD_FIELD" ou "~ORGUNIT_FIELD"
"""

import csv

# These are the field names in the SMS CSV files; change as required
# If you don't have a unique ID field, set UID_FIELD to the same value as EMAIL_FIELD
UID_FIELD = 'id'
EMAIL_FIELD = 'primaryEmail'
PASSWORD_FIELD = 'password'
FIRSTNAME_FIELD = 'name.givenName'
LASTNAME_FIELD = 'name.familyName'
ORGUNIT_FIELD = 'orgUnitPath'

NEW_EMAIL_FIELD = f'new-{EMAIL_FIELD}'

# Fields used to compare the previous and current records for a student
MATCH_FIELDS = [FIRSTNAME_FIELD, LASTNAME_FIELD, PASSWORD_FIELD, ORGUNIT_FIELD]

# File names: change as required/desired
PREVUSERS_FILENAME = "PrevUsers.csv"
CURRUSERS_FILENAME = "CurrUsers.csv"
ADDUSERS_FILENAME = "AddUsers.csv"
DELETETUSERS_FILENAME = "DeleteUsers.csv"
UPDATEUSERS_FILENAME = "UpdateUsers.csv"

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

prevStudentsSet = set()
prevStudents = {}
prevFile = open(PREVUSERS_FILENAME, 'r', encoding='utf-8')
prevCSV = csv.DictReader(prevFile, quotechar=QUOTE_CHAR)
delFieldnames = prevCSV.fieldnames[:]
for row in prevCSV:
  uid = row[UID_FIELD]
  prevStudentsSet.add(uid)
  prevStudents[uid] = row
prevFile.close()

currStudentsSet = set()
currStudents = {}
currFile = open(CURRUSERS_FILENAME, 'r', encoding='utf-8')
currCSV = csv.DictReader(currFile, quotechar=QUOTE_CHAR)
addFieldnames = currCSV.fieldnames[:]
for row in currCSV:
  uid = row[UID_FIELD]
  currStudentsSet.add(uid)
  currStudents[uid] = row
currFile.close()

addSet = currStudentsSet-prevStudentsSet
addFile = open(ADDUSERS_FILENAME, 'w', encoding='utf-8', newline='')
addCSV = csv.DictWriter(addFile, addFieldnames, lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
addCSV.writeheader()
for uid in sorted(addSet):
  addCSV.writerow(currStudents[uid])
addFile.close()

delSet = prevStudentsSet-currStudentsSet
delFile = open(DELETETUSERS_FILENAME, 'w', encoding='utf-8', newline='')
delCSV = csv.DictWriter(delFile, delFieldnames, lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
delCSV.writeheader()
for uid in sorted(delSet):
  delCSV.writerow(prevStudents[uid])
delFile.close()

updSet = prevStudentsSet & currStudentsSet
updFieldnames = addFieldnames[:]
updFieldnames.append(NEW_EMAIL_FIELD)
updFile = open(UPDATEUSERS_FILENAME, 'w', encoding='utf-8', newline='')
updCSV = csv.DictWriter(updFile, updFieldnames, lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
updCSV.writeheader()
for uid in sorted(updSet):
  prevStudent = prevStudents[uid]
  currStudent = currStudents[uid]
  if prevStudent[EMAIL_FIELD] != currStudent[EMAIL_FIELD]:
    currStudent[NEW_EMAIL_FIELD] = currStudent[EMAIL_FIELD]
    currStudent[EMAIL_FIELD] = prevStudent[EMAIL_FIELD]
    updCSV.writerow(currStudent)
    continue
  for field in MATCH_FIELDS:
    if prevStudent[field] != currStudent[field]:
      currStudent[NEW_EMAIL_FIELD] = ''
      updCSV.writerow(currStudent)
      break
updFile.close()
