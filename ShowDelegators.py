#!/usr/bin/env python3
"""
# Purpose: Make a CSV file showing delegators for delegates
# Note: This script can use Basic or Advanced GAM:
#	https://github.com/GAM-team/GAM
#	https://github.com/taers232c/GAMADV-XTD3
# Customize: Set SELECTED_DELEGATES, ONE_DELEGATOR_PER_ROW
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Get delegates
#  $ Basic: gam all users print delegates > ./AllDelegates.csv
#  $ Advanced: gam redirect csv ./AllDelegates.csv all users print delegates shownames
# 2: From that list of delegates, output a CSV file with headers "Delegate,Delegate Email,Delegators
#  $ python3 ShowDelegators.py ./AllDelegates.csv ./AllDelegators.csv
# 3: With SELECTED_DELEGATES and ONE_DELEGATOR_PER_ROW = True, it's easy to delete a delegate from delegator(s)
#    Edit AllDelegators.csv and delete any rows for delegators that are to remain
#  $ gam csv ./AllDelegators.csv gam user "~Delegators" delete delegate "~Delegate Email"
"""

import csv
import sys

# If you are only interested for delegators for a select list of delegates,
# add them to SELECTED_DELEGATES, e.g., SELECTED_DELEGATES = ['delegate1@domain.com',] SELECTED_DELEGATES = ['delegate1@domain.com', 'delegate2@domain.com',]
SELECTED_DELEGATES = []

# For each delegate, you can show all delegators on one row or on separate rows
# ONE_DELEGATOR_PER_ROW = False - All delegators for a delegate on one row
# ONE_DELEGATOR_PER_ROW = True - Each delegator for a delegate on a separate row
ONE_DELEGATOR_PER_ROW = False

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

delegates = {}

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['Delegate', 'Delegate Email', 'Delegators'], lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin

for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  delegate = row['delegateAddress']
  if not SELECTED_DELEGATES or delegate in SELECTED_DELEGATES:
    delegates.setdefault(delegate, {'Delegate': row.get('delegateName', delegate), 'Delegators': []})
    delegates[delegate]['Delegators'].append(row['User'])

for delegate in sorted(delegates):
  if not ONE_DELEGATOR_PER_ROW:
    outputCSV.writerow({'Delegate': delegates[delegate]['Delegate'],
                        'Delegate Email': delegate,
                        'Delegators': ' '.join(delegates[delegate]['Delegators'])})
  else:
    for delegator in delegates[delegate]['Delegators']:
      outputCSV.writerow({'Delegate': delegates[delegate]['Delegate'],
                          'Delegate Email': delegate,
                          'Delegators': delegator})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
