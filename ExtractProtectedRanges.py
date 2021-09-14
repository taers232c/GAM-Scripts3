#!/usr/bin/env python3
"""
# Purpose: Extract sheet protected ranges from a Google Sheet so they can be applied to a copied Google Sheet
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Produce a CSV file Input.json eom the original Google Sheet
#  $ gam redirect stdout Input.json user user@domain.com show sheet <OldFileId> formatjson fields sheets
# 2: Produce a JSON file Output.json with the protected ranges
#  $ python3 ./ExtractProtectedRanges.py Input.json Output.json
# 3: Copy the Google Sheet
#  $ gam user user@domain.com copy drivefile <OldFileId> newfilename CopiedSheet copyfilepermissions true
# 3: Update copied Google Sheet with protected ranges from original Google Sheet
#  $ gam user user@domain.com update sheet <NewFileId> json file Output.json

"""

import json
import sys

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin

updateProtectedRanges = {'requests': []}
jsonData = json.load(inputFile)
for sheet in jsonData['JSON'].get('sheets', []):
  for protectedRange in sheet.get('protectedRanges', []):
    updateProtectedRanges['requests'].append({'updateProtectedRange': {'protectedRange': protectedRange, 'fields': 'editors'}})
json.dump(updateProtectedRanges, outputFile, indent=2)
if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
