#!/usr/bin/env python3
"""
# Purpose: For a Google Drive User(s), output a CSV that shows all user organized events with a start date >= a specified date; they can then be deleted.
# Note: This script requires Advanced GAM:
#	https://github.com/taers232c/GAMADV-X, https://github.com/taers232c/GAMADV-XTD, https://github.com/taers232c/GAMADV-XTD3
# Customize: Set DELETE_EVENTS_WITH_ATTENDEES = True or False to determine whether events with attendees will be deleted.
# Usage:
# 1: Get calendar events for a user
#  $ Example, user's primary calendar: gam redirect csv ./UserEvents.csv user user@domain.com print events primary singleevents orderby starttime maxattendees 1
#  $ Example, all calendars a user owns: gam redirect csv ./UserEvents.csv user user@domain.com print events minaccessrole owner singleevents orderby starttime maxattendees 1
# 2: From that list of Events, output a CSV file with only the rows with an event start date >= a specified date
#  $ python DeleteFutureEvents.py yyyy-mm-dd UserEvents.csv UserFutureEvents.csv
# 3: Delete the events
#    Parallel, faster:
#  $ gam csv UserFutureEvents.csv gam user ~primaryEmail delete event calendars ~calendarId events ~id doit
#    Serial, cleaner output:
#  $ gam csvkmd users UserFutureEvents.csv keyfield primaryEmail subkeyfield calendarId datafield id delete event calendars csvsubkey calendarId events csvdata id doit
# 4: Empty the calendars trash
#  $ gam csvkmd users UserFutureEvents.csv keyfield primaryEmail datafield calendarId empty calendartrash calendars csvdata calendarId
"""

import csv
import datetime
import sys

DELETE_EVENTS_WITH_ATTENDEES = False

YYYYMMDD_FORMAT = u'%Y-%m-%d'

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

if (len(sys.argv) > 3) and (sys.argv[3] != '-'):
  outputFile = open(sys.argv[3], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  inputFile = open(sys.argv[2], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin

if len(sys.argv) > 1:
  startDate = sys.argv[1]
  try:
    datetime.datetime.strptime(startDate, YYYYMMDD_FORMAT)
  except ValueError:
    sys.stderr.write('ERROR: date ({0}) is not valid, it must be (yyyy-mm-dd)\n'.format(startDate))
    sys.exit(1)
else:
  startDate = datetime.datetime.now().strftime(YYYYMMDD_FORMAT)

inputCSV = csv.DictReader(inputFile, quotechar=QUOTE_CHAR)
outputCSV = csv.DictWriter(outputFile, inputCSV.fieldnames, lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

for row in inputCSV:
  if row['primaryEmail'] != row.get('creator.email'):
    continue
  if row.get('start.date'):
    if row['start.date'] < startDate:
      continue
  elif row.get('start.dateTime'):
    if row['start.dateTime'][:10] < startDate:
      continue
  else:
    continue
  if not DELETE_EVENTS_WITH_ATTENDEES:
    numAttendees = row.get('attendees', '')
    if numAttendees and int(numAttendees) > 0:
      continue
  outputCSV.writerow(row)
if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
