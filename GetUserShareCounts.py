#!/usr/bin/env python3
"""
# Purpose: For a Google Drive User(s), output a CSV file showing the share type counts for files shared by the user(s)
# Customize: Set the separateWithLink = True below if you want separate withLink counts for types anyone and domain
# Note: This script can use basic GAM: https://github.com/jay0lee/GAM or advanced GAM: https://github.com/taers232c/GAMADV-X
# Usage:
# 1: Get ACLs for all files, if you don't want all users, replace all users with your user selection in the command below
#  $ Example, Basic GAM: gam all users print filelist id title permissions > filelistperms.csv
#  $ Example, advanced GAM: gam config auto_batch_min 1 redirect csv ./filelistperms.csv multiprocess all users print filelist id title permissions
# 2: From that list of ACLs, output a CSV file that shows the owner and various share type counts
#  $ python GetUserShareCounts.py filelistperms.csv usersharecounts.csv
"""

import csv
import re
import sys

id_n_type = re.compile(r"permissions.(\d+).type")
separateWithLink = False

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w')
else:
  outputFile = sys.stdout
if separateWithLink:
  outputCSV = csv.DictWriter(outputFile, ['Owner', 'anyone', 'anyone.withLink', 'domain', 'domain.withLink', 'group', 'user'], lineterminator='\n')
  zeroCounts = {'anyone': 0, 'anyone.withLink': 0, 'domain': 0, 'domain.withLink': 0, 'group': 0, 'user': 0}
else:
  outputCSV = csv.DictWriter(outputFile, ['Owner', 'anyone', 'domain', 'group', 'user'], lineterminator='\n')
  zeroCounts = {'anyone': 0, 'domain': 0, 'group': 0, 'user': 0}
outputCSV.writeheader()

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin

userShareCounts = {}
for row in csv.DictReader(inputFile):
  owner = row['Owner']
  userShareCounts.setdefault(owner, zeroCounts.copy())
  for k, v in iter(row.items()):
    mg = id_n_type.match(k)
    if mg and v:
      perm_id = mg.group(1)
      if row['permissions.{0}.role'.format(perm_id)] != 'owner':
        if v in ['anyone', 'domain']:
          if separateWithLink:
            if row['permissions.{0}.withLink'.format(perm_id)] == 'True':
              v += '.withLink'
        userShareCounts[owner][v] += 1
for owner, counts in sorted(iter(userShareCounts.items())):
  row = {'Owner': owner}
  row.update(counts)
  outputCSV.writerow(row)

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
