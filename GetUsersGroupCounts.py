#!/usr/bin/env python3
"""
# Purpose: Create a CSV file showing users that belong to a number of groups beyond a threshold
# threshold not specified - output all users
# threshold 0 - output all users belonging to at least 1 group
# threshold N - output all users belonging to more than N groups
# Note: This script can use basic GAM: https://github.com/jay0lee/GAM or advanced GAM: https://github.com/taers232c/GAMADV-X
# Usage:
# 1: Get primaryEmail, groups for all users
#  $ Basic: gam print users fields primaryEmail,name groups > UsersGroups.csv
#  $ Advanced: gam config auto_batch_min 1 redirect csv ./UsersGroups.csv multiprocess all users print users fields primaryEmail,name groups
# 2: From that list of users, output a CSV file with headers with the same headers as UsersGroups.csv plus GroupsCount
#    that shows the number of groups
#  $ python GetUsersGroupCounts.py ./UsersGroups.csv ./UsersGroupsCounts.csv <threshold>
"""

import csv
import sys

if len(sys.argv) > 3:
  threshold = int(sys.argv[3])
else:
  threshold = -1

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'wb')
else:
  outputFile = sys.stdout

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'rb')
else:
  inputFile = sys.stdin

inputCSV = csv.DictReader(inputFile)
fieldnames = inputCSV.fieldnames[:]
fieldnames.insert(fieldnames.index('Groups'), 'GroupsCount')
outputCSV = csv.DictWriter(outputFile, fieldnames, lineterminator='\n')
outputCSV.writeheader()

for row in inputCSV:
  groupsCount = len(row['Groups'].split())
  if groupsCount > threshold:
    row['GroupsCount'] = groupsCount
    outputCSV.writerow(row)

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
