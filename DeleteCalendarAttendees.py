#!/usr/bin/env python3
"""
# Purpose: Delete attendees from calendar events
# Note: This script requires Advanced GAM version 4.89.02 or later:
#	https://github.com/taers232c/GAMADV-XTD3
# Customize: Set DELETE_ATTENDEES_SET, DELETE_ATTENDEES_PATTERN, ALL_ATTENDEES_ONE_ROW
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Produce a CSV file AllEvents.csv of calendar events
# 2: You need a list of calendars.
#    See: https://github.com/taers232c/GAMADV-XTD3/wiki/Users-Calendars#display-calendar-lists
#    For example, to get all user's owned calendars
#  $ gam config auto_batch_min 1 redirect csv ./AllCalendars.csv multiprocess all users print calendars minaccessrole owner
#    For example, to get all user's primary calendar
#  $ gam config auto_batch_min 1 redirect csv ./AllCalendars.csv multiprocess all users print calendars primary
# 3: From that calendar list, you need a list of events that contain the attendees you wish to delete
#    See: https://github.com/taers232c/GAMADV-XTD3/wiki/Users-Calendars-Events#display-calendar-events
#    For example, to get events with attendee foo@bar.com
#  $ gam redirect csv ./AllEvents.csv multiprocess csv ./AllCalendars.csv gam user "~primaryEmail" print events "~calendarId" starttime now matchfield attendees "foo@bar.com" fields id,summary,attendees.email
#    Set DELETE_ATTENDEES_SET = set(['foo@bar.com'])
#    For example, to get events with any attendees from the domain bar.com
#    The examples use "starttime now" to select future events only; eliminate it if you want to remove the attendees from past events as well.
#  $ gam redirect csv ./AllEvents.csv multiprocess csv ./AllCalendars.csv gam user "~primaryEmail" print events "~calendarId" starttime now matchfield attendeespattern "^.*@bar.com$" fields id,summary,attendees.email
#    Set DELETE_ATTENDEES_PATTERN = re.compile(r'^.*@bar.com$')
# 4: From that list of events, output a CSV file with headers "primaryEmail,calendarId,id,aummary,emails"
#    thats lists the attendees to delete from each event
#  $ python3 ./DeleteCalendarAttendees.py AllEvents.csv DeleteAttendees.csv
# 5: Inspect DeleteAttendees.csv, verify that it makes sense and then proceed
# 6: Delete the attendees
#  $ gam csv DeleteAttendees.csv gam user "~primaryEmail" update calattendees "~calendarId" id "~id" deleteentity "~emails" doit
"""

import csv
import re
import sys

# Specific email addresses to delete
# None: DELETE_ATTENDEES_SET = set([])
# List: DELETE_ATTENDEES_SET = set(['foo@bar.com, 'goo@bar.com'])
DELETE_ATTENDEES_SET = set([])

# Delete email addresses that match a pattern
# None: DELETE_ATTENDEES_PATTERN = None
# Pattern: DELETE_ATTENDEES_PATTERN = re.compile(r'^.*@bar.com$')
DELETE_ATTENDEES_PATTERN = None

# Should all attendees to delete for an event be on one row
ALL_ATTENDEES_ONE_ROW = True

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

ATTENDEES_N_EMAIL = re.compile(r"attendees.(\d+).email")

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['primaryEmail', 'calendarId', 'id', 'summary', 'emails'], lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin

for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  deleteAttendees = []
  for k, v in iter(row.items()):
    mg = ATTENDEES_N_EMAIL.match(k)
    if mg and ((v in DELETE_ATTENDEES_SET) or (DELETE_ATTENDEES_PATTERN and DELETE_ATTENDEES_PATTERN.match(v))):
      deleteAttendees.append(v)
  if deleteAttendees:
    if ALL_ATTENDEES_ONE_ROW:
      outputCSV.writerow({'primaryEmail': row['primaryEmail'],
                          'calendarId': row['calendarId'],
                          'id': row['id'],
                          'summary': row.get('summary', ''),
                          'emails': ' '.join(deleteAttendees)})
    else:
      for attendee in deleteAttendees:
        outputCSV.writerow({'primaryEmail': row['primaryEmail'],
                            'calendarId': row['calendarId'],
                            'id': row['id'],
                            'summary': row.get('summary', ''),
                            'emails': attendee})
if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
