#!/usr/bin/env python3
"""
# Purpose: Convert output from print events to get unique list of attendee emal/names; you can filter for specific attendees.
# Customize: Set ATTENDEE_LIST, DOMAIN_LIST, ATTENDEE_PATTERN, SHOW_ATENDEES_WITH_NO_NAME
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Generate a list of events that contain the attendees you wish to save
#    See: https://github.com/taers232c/GAMADV-XTD3/wiki/Users-Calendars-Events#display-calendar-events
#    For example, to get events with any attendees from the domain bar.com; omit
#  $ gam redirect csv ./AllEvents.csv user user@domain.com print events <UserCalendarEntity> matchfield attendeespattern "^.*@bar.com$" fields attendees
# 2: From that list of files, output a CSV file with columns email,name that lists one attendee per row
#  $ python3 CollectAttendeesInfo.py AllEvents.csv AttendeesInfo.csv
"""

import csv
import re
import sys

# Specify specific attendees(s), e.g., ATTENDEE_LIST = ['user1@domain.com'] ATTENDEE_LIST = ['user1@domain.com', 'user2@domain.com']
# The list should be empty if you're only specifiying domains in DOMAIN_LIST, e.g. ATTENDEE_LIST = []
ATTENDEE_LIST = []

# Specify specific domain(s) if you want all attendees in the domain, e.g., DOMAIN_LIST = ['domain.com'] DOMAIN_LIST = ['domain1.com', 'domain2.com']
# The list should be empty if you're only specifiying attendees in ATTENDEE_LIST, e.g. DOMAIN__LIST = []
DOMAIN_LIST = []

# Specify attendees that match a pattern
# None: ATTENDEE_PATTERN = None
# Pattern: ATTENDEE_PATTERN = re.compile(r'^.*@bar.com$')
ATTENDEE_PATTERN = None

# Should attendees with no name be shown
# False: attendee with no name will not be shown
# True: attendee with no name will have name set to email address
SHOW_ATTENDEES_WITH_NO_NAME = True

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

ATTENDEES_N_EMAIL = re.compile(r"attendees.(\d+).email")

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin
inputCSV = csv.DictReader(inputFile, quotechar=QUOTE_CHAR)

outputCSV = csv.DictWriter(outputFile, ['email', 'name'], lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

attendees = set()
for row in inputCSV:
  for k, v in iter(row.items()):
    mg = ATTENDEES_N_EMAIL.match(k)
    if mg:
      attendees_N = mg.group(1)
      if not v:
        continue
      _, domain = v.split('@')
      if ((v not in attendees) and
          (not DOMAIN_LIST or domain in DOMAIN_LIST) and
          (not ATTENDEE_LIST or v in ATTENDEE_LIST) and
          (not ATTENDEE_PATTERN or ATTENDEE_PATTERN.match(v))):
        attendees.add(v)
        name = row.get(f'attendees.{attendees_N}.displayName')
        if not name:
          if not SHOW_ATTENDEES_WITH_NO_NAME:
            continue
          name = v
        outputCSV.writerow({'email': v, 'name': name})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
