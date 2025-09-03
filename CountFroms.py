#!/usr/bin/env python3
"""
# Purpose: Make a CSV file showing the number of messages from each unique from address
# Customize: Set NUM_FROMS_TO_SHOW
# Python: Use python or python3 below as appropriate to your system; verify that you have version  3.9 or greater
#  $ python -V   or python3 -V
#  Python 3.x.y
# Usage:
# 1: Get message froms; replace <UserTypeEntity> as desired, e.g., user user@domain.com
#  $ gam config csv_output_header_filter From redirect csv ./Froms.csv <UserTypeEntity> print messages query "{in:inbox OR has:userlabels}"
#      See: https://support.google.com/mail/answer/7190 for additional query options
# 2: From that list of message Froms, output a CSV file with headers "From,Count" that shows the
#    number of messages per from address srted from most to least
#  $ python3 CountFroms.py ./Froms.csv ./FromCounts.csv
"""

import csv
import re
import sys

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

NUM_FROMS_TO_SHOW = 0 # 0 - Show all froms; N - Show the first N froms

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['From', 'Count'], lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin

fromPattern = re.compile(r'^.+<(.+)>$')
fromCounts = {}
for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  fromMatch = fromPattern.match(row['From'])
  if not fromMatch:
    fromAddr = row['From'].lower()
  else:
    fromAddr = fromMatch.group(1).lower()
  fromCounts.setdefault(fromAddr, 0)
  fromCounts[fromAddr] += 1
fromsShown = 0
for fromAddr, count in sorted(fromCounts.items(), key=lambda item: item[1], reverse=True):
  outputCSV.writerow({'From': fromAddr, 'Count': count})
  fromsShown += 1
  if fromsShown == NUM_FROMS_TO_SHOW:
    break

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
