#!/usr/bin/env python3
"""
# Purpose: Convert a CSV file showing group settigs to one with the settings in JSON format
# Note: This script can use GAM7 or Advanced GAM:
#	https://github.com/taers232c/GAMADV-XTD3
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
#  $ python ConvertGroupColsToJSON.py ./Groups.csv ./GroupsJSON.csv
"""

import csv
import json
import sys

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

GROUP_JSON_SKIP_FIELDS = [
  'adminCreated',
  'directMembersCount',
  'members',
  'aliases',
  'nonEditableAliases',
  'kind',
  ]

# Set INCLUDE_XXX_ATTRIBUTES = True
# to include deprecated or merged attributes

INCLUDE_DEPRECATED_ATTRIBUTES = False
GROUP_DEPRECATED_ATTRIBUTES = [
  'allowGoogleCommunication',
  'favoriteRepliesOnTop',
  'maxMessageBytes',
  'messageDisplayFont',
  'whoCanAddReferences',
  'whoCanMarkFavoriteReplyOnOwnTopic',
  ]

INCLUDE_DISCOVER_ATTRIBUTES = False
GROUP_DISCOVER_ATTRIBUTES = [
  'showInGroupDirectory',
  ]

INCLUDE_ASSIST_CONTENT_ATTRIBUTES = False
GROUP_ASSIST_CONTENT_ATTRIBUTES = [
  'whoCanAssignTopics',
  'whoCanEnterFreeFormTags',
  'whoCanHideAbuse',
  'whoCanMakeTopicsSticky',
  'whoCanMarkDuplicate',
  'whoCanMarkFavoriteReplyOnAnyTopic',
  'whoCanMarkNoResponseNeeded',
  'whoCanModifyTagsAndCategories',
  'whoCanTakeTopics',
  'whoCanUnassignTopic',
  'whoCanUnmarkFavoriteReplyOnAnyTopic',
  ]

INCLUDE_MODERATE_CONTENT_ATTRIBUTES = False
GROUP_MODERATE_CONTENT_ATTRIBUTES = [
  'whoCanApproveMessages',
  'whoCanDeleteAnyPost',
  'whoCanDeleteTopics',
  'whoCanLockTopics',
  'whoCanMoveTopicsIn',
  'whoCanMoveTopicsOut',
  'whoCanPostAnnouncements',
  ]

INCLUDE_MODERATE_MEMBERS_ATTRIBUTES = False
GROUP_MODERATE_MEMBERS_ATTRIBUTES = [
  'whoCanAdd',
  'whoCanApproveMembers',
  'whoCanBanUsers',
  'whoCanInvite',
  'whoCanModifyMembers',
  ]

def includeFields(include, fields):
  if not include:
    for field in fields:
      row.pop(field, None)

with open(sys.argv[1], 'r', encoding='utf-8') as inputFile:
  with open(sys.argv[2], 'w', encoding='utf-8', newline='') as outputFile:
    outputCSV = csv.DictWriter(outputFile, ['email', 'id', 'JSON-settings'], lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
    outputCSV.writeheader()
    for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
      groupEmail = row.pop('email')
      groupId = row.pop('id', '')
      groupName = row.pop('name', '')
      groupDescription = row.pop('description', '')
      includeFields(False, GROUP_JSON_SKIP_FIELDS)
      includeFields(INCLUDE_DEPRECATED_ATTRIBUTES, GROUP_DEPRECATED_ATTRIBUTES)
      includeFields(INCLUDE_DISCOVER_ATTRIBUTES, GROUP_DISCOVER_ATTRIBUTES)
      includeFields(INCLUDE_ASSIST_CONTENT_ATTRIBUTES, GROUP_ASSIST_CONTENT_ATTRIBUTES)
      includeFields(INCLUDE_MODERATE_CONTENT_ATTRIBUTES, GROUP_MODERATE_CONTENT_ATTRIBUTES)
      includeFields(INCLUDE_MODERATE_MEMBERS_ATTRIBUTES, GROUP_MODERATE_MEMBERS_ATTRIBUTES)
      outputCSV.writerow({'email': groupEmail,
                          'id': groupId,
                          'JSON-settings': json.dumps(row, ensure_ascii=False, sort_keys=True)})
