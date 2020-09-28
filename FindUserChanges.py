#!/usr/bin/env python3
"""
# Purpose: Generate adds/deletes/updates from files exported from SMS
# Note: This script can use Basic or Advanced GAM:
#	https://github.com/jay0lee/GAM
#	https://github.com/taers232c/GAMADV-XTD3# Usage:
# Customize: Set the field and file names as required/desired
# 1: Rename CurrUsers.csv to PrevUsers.csv
# 2: Export current data from SMS to CurrUsers.csv
# 3: Find the changes
#  $ python3 ./FindUserChanges.py
# 4: Do the deletes; substitute actual field names from SMS CSV file
#  $ gam csv DeleteUsers.csv gam delete user "~primaryEmail"
#    Rather than delete, you could suspend the users; you can optionally move the uses to a suspended OU
#  $ gam csv DeleteUsers.csv gam update user "~primaryEmail" suspended true
#  $ gam csv DeleteUsers.csv gam update user "~primaryEmail" suspended true ou /Suspended
# 5: Do the adds; substitute actual field names from SMS CSV file
#  $ gam csv AddUsers.csv gam create user "~primaryEmail" firstname "~name.givenName" lastname "~name.familyName" password "~password" ou "~orgUnitPath"
# 6: Do the changes; substitute actual field names from SMS CSV file
#  $ gam csv UpdateUsers.csv gam update user "~primaryEmail" firstname "~name.givenName" lastname "~name.familyName" password "~password" ou "~orgUnitPath"
"""

import csv

# These are the field names in the SMS CSV files; change as required
EMAIL_FIELD = 'primaryEmail'
PASSWORD_FIELD = 'password'
FIRSTNAME_FIELD = 'name.givenName'
LASTNAME_FIELD = 'name.familyName'
ORGUNIT_FIELD = 'orgUnitPath'

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
  email = row[EMAIL_FIELD]
  prevStudentsSet.add(email)
  prevStudents[email] = row
prevFile.close()

currStudentsSet = set()
currStudents = {}
currFile = open(CURRUSERS_FILENAME, 'r', encoding='utf-8')
currCSV = csv.DictReader(currFile, quotechar=QUOTE_CHAR)
addFieldnames = currCSV.fieldnames[:]
for row in currCSV:
  email = row[EMAIL_FIELD]
  currStudentsSet.add(email)
  currStudents[email] = row
currFile.close()

addSet = currStudentsSet-prevStudentsSet
addFile = open(ADDUSERS_FILENAME, 'w', encoding='utf-8', newline='')
addCSV = csv.DictWriter(addFile, addFieldnames, lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
addCSV.writeheader()
for email in sorted(addSet):
  addCSV.writerow(currStudents[email])
addFile.close()

delSet = prevStudentsSet-currStudentsSet
delFile = open(DELETETUSERS_FILENAME, 'w', encoding='utf-8', newline='')
delCSV = csv.DictWriter(delFile, delFieldnames, lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
delCSV.writeheader()
for email in sorted(delSet):
  delCSV.writerow(prevStudents[email])
delFile.close()

updFile = open(UPDATEUSERS_FILENAME, 'w', encoding='utf-8', newline='')
updCSV = csv.DictWriter(updFile, addFieldnames, lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
updCSV.writeheader()
for email in sorted(currStudentsSet):
  if email not in addSet and email not in delSet:
    prevStudent = prevStudents[email]
    currStudent = currStudents[email]
    for field in MATCH_FIELDS:
      if prevStudent[field] != currStudent[field]:
        updCSV.writerow(currStudents[email])
        break
updFile.close()
