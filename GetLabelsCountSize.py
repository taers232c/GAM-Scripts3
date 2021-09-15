#!/usr/bin/env python3
"""
# Purpose: Create a CSV file that totals message label data: count and size
# Note: This script requires Advanced GAM:
#	https://github.com/taers232c/GAMADV-XTD3
# Customize: DELIMITER, SHOW_TOTALS
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Get the label data
#  Single user
#  $ gam redirect csv ./LabelData.csv user user@domain.com print messages showlabels showsize headers "" delimiter '|'
#  Multiple users; replace all users as desired
#  $ gam config auto_batch_min 1 redirect csv ./LabelData.csv multiprocess all users print messages showlabels showsize headers "" delimiter '|'
# 2: python3 GetLabelsCountSize.py LabelData.csv LabelSummary.csv
"""

import csv
import sys

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

DELIMITER = '|' # Must match delimiter from command line
SHOW_TOTALS = False # False: Don't show total label counts/size for each user; True: Do show

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['User', 'Label', 'Count', 'SizeEstimate'], lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin

Users = {}
for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  user = row['User']
  Users.setdefault(user, {})
  size = int(row['SizeEstimate'])
  for label in row['Labels'].split(DELIMITER):
    Users[user].setdefault(label, {'Count': 0, 'SizeEstimate': 0})
    Users[user][label]['Count'] +=1
    Users[user][label]['SizeEstimate'] += size

for user in sorted(Users):
  count = 0
  size = 0
  for label, data in sorted(iter(Users[user].items())):
    count += data['Count']
    size += data['SizeEstimate']
    outputCSV.writerow({'User': user,
                        'Label': label,
                        'Count': data['Count'],
                        'SizeEstimate': data['SizeEstimate']})
  if SHOW_TOTALS:
    outputCSV.writerow({'User': user,
                        'Label': 'Total',
                        'Count': count,
                        'SizeEstimate': size})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
