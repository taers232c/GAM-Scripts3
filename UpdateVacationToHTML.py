#!/usr/bin/env python3
"""
# Purpose: Convert non-HTML(RTF) vacation messages to HTML(RTF)
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Get vacation
#  $ gam redirect csv Vacation.csv <UserTypeEntity> print vacation compact
# 2: Output a CSV file for users with non-blank/non-HTML vacation messages converted to HTML
#  $ python3 ComvertVacationToHTML.py ./Vacation.csv ./HTMLVacation.csv
# 3: Inspect HTMLVacation.csv, verify that it makes sense and then proceed
# 4: Update vacation
#  $ gam csv HTMLVacation.csv gam user "~User" vacation "~enabled" htmlmessage "~message"
"""

import csv
import sys

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

inputFile = open(sys.argv[1], 'r', encoding='utf-8')
inputCSV = csv.DictReader(inputFile, quotechar=QUOTE_CHAR)

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, inputCSV.fieldnames, lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

for row in inputCSV:
  if row['html'] != 'True' and row['message']:
    row['message'] = "<div>"+row['message'].replace('\\\\n', '<br>').replace('\\\\r', '')+"</div>"
    outputCSV.writerow(row)

if outputFile != sys.stdout:
  outputFile.close()
