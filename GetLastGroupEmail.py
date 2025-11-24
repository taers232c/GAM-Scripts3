#!/usr/bin/env python3
"""
# Purpose: Make a CSV file showing the last message sent to a group
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3.9 or greater
#  $ python -V   or python3 -V
#  Python 3.x.y
# Usage:
# 1: Get messages to groups listed in Groups.csv with column header gmail
#    gam redirect csv ./GroupEmails.csv multiprocess redirect stderr - multiprocess  csv Groups.csv gam group "~email" print messages query "list:~~email~~" maxtoprint 1 showdate addcsvdata Group "~email" 
# 2: From that list of message Froms, output a CSV file that shows the last message sent to the group
#  $ python3 GetLastGroupEmail.py ./GroupEmails.csv ./LastGroupEmails.csv
"""

import csv
import sys

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

inputFile = open(sys.argv[1], 'r', encoding='utf-8')
inputCSV = csv.DictReader(inputFile, quotechar=QUOTE_CHAR)
inputFieldNames = inputCSV.fieldnames

outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
outputCSV = csv.DictWriter(outputFile, inputFieldNames, lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

lastGroupEmail = {}
for row in inputCSV:
  group = row['Group'].lower()
  if group == row['To'].lower():
    if group not in lastGroupEmail:
      lastGroupEmail.setdefault(group, row)
    elif row['Date'] > lastGroupEmail[group]['Date']:
      lastGroupEmail[group] = row
for _, message in sorted(lastGroupEmail.items()):
  outputCSV.writerow(message)

inputFile.close()
outputFile.close()
