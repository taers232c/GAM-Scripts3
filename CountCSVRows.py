#!/usr/bin/env python3
"""
# Purpose: Count rows in a CSV file
#
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# python3 CountCSVRows.py File.csv
#
"""

import csv
import sys

QUOTE_CHAR = '"' # Adjust as needed

if sys.argv[1] != '-':
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin
rows = 0
for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  rows += 1
print(rows)
if inputFile != sys.stdin:
  inputFile.close()
