#!/usr/bin/env python3
"""
# Purpose: Convert output from print events to put one attendee per row; you can filter for specific attendees.
# Note: This script requires Advanced GAM:
#	https://github.com/taers232c/GAMADV-XTD3
# Customize: Set ATTENDEE_LIST, DROP_GENERAL_COLUMNS, DROP_ATTENDEE_COLUMNS.
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
#    For example, to get events with any attendees from the domain bar.com
#    The example uses "starttime now" to select future events only; eliminate it if you want to remove the attendees from past events as well.
#  $ gam redirect csv ./AllEvents.csv multiprocess csv ./AllCalendars.csv gam user "~primaryEmail" print events "~calendarId" starttime now matchfield attendeespattern "^.*@bar.com$" fields id,summary,attendees
# 2: From that list of files, output a CSV file that lists one attendee per row
#  $ python3 MakeOneAttendeePerRowEvents.py AllEvents.csv AllEventsOAPR.csv
"""

import csv
import re
import sys

# Specify specific user(s), e.g., ATTENDEE_LIST = ['user1@domain.com'] ATTENDEE_LIST = ['user1@domain.com', 'user2@domain.com']
# The list should be empty if you're only specifiying domains in DOMAIN_LIST, e.g. ATTENDEE_LIST = []
ATTENDEE_LIST = []

# Specify specific domain(s) if you want all attendees in the domain, e.g., DOMAIN_LIST = ['domain.com'] DOMAIN_LIST = ['domain1.com', 'domain2.com']
# The list should be empty if you're only specifiying attendees in ATTENDEE_LIST, e.g. DOMAIN__LIST = []
DOMAIN_LIST = []

# Specify general columns you don't want in the output. e.g., photoLink.
# The list should be empty if you want all general columns, e.g, DROP_GENERAL_COLUMNS = []
DROP_GENERAL_COLUMNS = ['attendees']

# Specify permission columns you don't want in the output. e.g., photoLink.
# The list should be empty if you want all permission columns, e.g, DROP_ATTENDEE_COLUMNS = []
DROP_ATTENDEE_COLUMNS = ['photoLink']

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

ATTENDEES_N_FIELD = re.compile(r"attendees.(\d+).(.+)")

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin

inputCSV = csv.DictReader(inputFile, quotechar=QUOTE_CHAR)
attendeeFields = set()
inputFieldnames = []
for fieldname in inputCSV.fieldnames:
  mg = ATTENDEES_N_FIELD.match(fieldname)
  if mg:
    field = mg.group(2)
    if (not DROP_ATTENDEE_COLUMNS or field not in DROP_ATTENDEE_COLUMNS) and field not in attendeeFields:
      attendeeFields.add(field)
      inputFieldnames.append(f'attendee.{field}')
  elif not DROP_GENERAL_COLUMNS or fieldname not in DROP_GENERAL_COLUMNS:
    inputFieldnames.append(fieldname)

outputCSV = csv.DictWriter(outputFile, inputFieldnames, lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

for row in inputCSV:
  baseRow = {}
  attendees = {}
  for k, v in iter(row.items()):
    mg = ATTENDEES_N_FIELD.match(k)
    if mg:
      attendees_N = mg.group(1)
      attendees.setdefault(attendees_N, {})
      attendees[attendees_N][mg.group(2)] = v
    elif not DROP_GENERAL_COLUMNS or k not in DROP_GENERAL_COLUMNS:
      baseRow[k] = v
  for k, v in iter(attendees.items()):
    newRow = baseRow.copy()
    emailAddress = v['email']
    domain = emailAddress[emailAddress.find('@')+1:]
    if DOMAIN_LIST and domain not in DOMAIN_LIST:
      continue
    if ATTENDEE_LIST and emailAddress not in ATTENDEE_LIST:
      continue
    for kp, kv in sorted(v.items()):
      if not DROP_ATTENDEE_COLUMNS or kp not in DROP_ATTENDEE_COLUMNS:
        newRow[f'attendee.{kp}'] = kv
    outputCSV.writerow(newRow)

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
