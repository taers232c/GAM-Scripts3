#!/usr/bin/env python3
"""
# Purpose: Extract sheet protected sheet ranges from a Google Sheet so they can be deleted
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Produce a CSV file showing the protected ranges in JSON format with a quote character on single quote;
#      the headers must be User, spreadsheetId and JSON
#  $ gam redirect csv ./ProtectedRanges.csv user user@domain.com print sheet query "'me' in owners and mimeType = 'application/vnd.google-apps.spreadsheet'" sheetsfields protectedranges formatjson quotechar "'"
# 2: Produce a CSV file DeleteProtectedRanges.csv with requests to delete the protected ranges for each spreadsheet
#  $ python3 ./DeleteProtectedRanges.py ProtectedRanges.csv DeleteProtectedRanges.csv
# 3: Delete the protected ranges
#  $ gam redirect stdout ./DeleteProtectedRanges.txt multiprocess redirect stderr stdout csv DeleteProtectedRanges.csv quotechar "'" gam user "~User" update sheet "~spreadsheetId" json "~JSON"

"""

import csv
import json
import sys

QUOTE_CHAR = "'" # Must be "'"
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
inputFile = open(sys.argv[1], 'r', encoding='utf-8')

inputCSV = csv.DictReader(inputFile, quotechar=QUOTE_CHAR)
outputCSV = csv.DictWriter(outputFile, ['User', 'spreadsheetId', 'JSON'], lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

for row in inputCSV:
  deleteProtectedRanges = {'requests': []}
  jsonData = json.loads(row['JSON'])
  for sheet in jsonData.get('sheets', []):
    for protectedRange in sheet.get('protectedRanges', []):
      deleteProtectedRanges['requests'].append({'deleteProtectedRange': {'protectedRangeId': protectedRange['protectedRangeId']}})
  if deleteProtectedRanges['requests']:
    outputCSV.writerow({'User': row['User'],
                        'spreadsheetId': row['spreadsheetId'],
                        'JSON': json.dumps(deleteProtectedRanges)})

inputFile.close()
outputFile.close()
