#!/usr/bin/env python3
"""
# Purpose: Convert a CSV file showing group members in JSON format to a JSON file importable by Canvas
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Get group members
#  $ gam redirect csv ./GroupUsers.json print group-members group group@domain.com fields email userfields fullname formatjson quotechar " " nogroupemail
# 2: From that list of group members, output a JSON file importable by Canvas
#  $ python3 ConvertGroupUsersToCanvas.py ./GroupUsers.csv ./CanvasUsers.json
"""

import csv
import json
import sys

with open(sys.argv[1], 'r', encoding='utf-8') as inputFile:
  inputCSV = csv.DictReader(inputFile, quotechar=' ')
  canvasData = {"result": []}
  for row in inputCSV:
    canvasData["result"].append({"student": json.loads(row['JSON'])})

with open(sys.argv[2], 'w', encoding='utf-8', newline='') as outputFile:
  outputFile.write(json.dumps(canvasData, indent=2, sort_keys=True))
