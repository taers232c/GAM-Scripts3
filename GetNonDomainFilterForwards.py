#!/usr/bin/env python3
"""
# Purpose: For Gmail User(s), list/delete all filters that forward email outside of a list of specified domains
# Note: This script can use basic GAM: https://github.com/jay0lee/GAM or advanced GAM: https://github.com/taers232c/GAMADV-X
# Usage:
# 1: Get filters, if you don't want all users, replace all users with your user selection in the command below
#  $ Example, basic GAM: gam all users print filters > filters.csv
#  $ Example, advanced GAM: gam config auto_batch_min 1 redirect csv ./filters.csv multiprocess all users print filters
# 2: From that list of filters, output a CSV file that lists the filters that forward email outside of the specified domains.
#  $ python GetNonDomainFilterForwards.py filters.csv outsidefilters.csv
# 3: Inspect outsidefilters.csv, verify that it makes sense and then proceed
# 4: Delete the filters
#  $ gam csv outsidefilters.csv gam user "~User" delete filter "~id"
"""

import csv
import re
import sys

forward_domain = re.compile(r"^forward .*@(.*)$")
# Substitute your domain(s) in the list below, e.g., domainList = ['domain.com',] domainList = ['domain1.com', 'domain2.com',]
domainList = ['domain.com',]

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w')
else:
  outputFile = sys.stdout
if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin

filters = csv.DictReader(inputFile)
outsidefilters = csv.DictWriter(outputFile, filters.fieldnames, lineterminator='\n')
outsidefilters.writeheader()
for row in filters:
  v = row.get('forward', '')
  if v:
    mg = forward_domain.match(v)
    if mg and mg.group(1) not in domainList:
      outsidefilters.writerow(row)

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
