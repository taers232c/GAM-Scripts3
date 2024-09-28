#!/usr/bin/env python3
"""
# Purpose: Convert a CSV file showing course participants one per row to single row per course
# Note: This script can use GAM7 or Advanced GAM:
#       https://github.com/GAM-team/GAM                                                                                                                               
#	https://github.com/taers232c/GAMADV-XTD3
# Customize: Set DELIMITER to the single character that will separate participants
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Get course participants
#  $ gam config csv_output_header_filter "courseId,courseName,userRole,profile.emailAddress" redirect csv ./CourseParticipants.csv print course-participants
#    See: https://github.com/taers232c/GAMADV-XTD3/wiki/Classroom-Membership#display-course-membership
# 2: From that list of group members, output a CSV file with headers primaryEmail,GroupsCount,Groups that shows the groups for each user
#  $ python3 CombineCourseParticipants.py ./CourseParticipants.csv ./CombinedCourseParticipants.csv

"""

import csv
import sys

DELIMITER = ' '
QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
outputCSV = csv.DictWriter(outputFile, ['courseId', 'courseName', 'Teacher', 'Student'], lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

inputFile = open(sys.argv[1], 'r', encoding='utf-8')

CourseParticipants = {}
for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  courseId = row['courseId']
  CourseParticipants.setdefault(courseId, {'courseName': row['courseName'], 'Teacher': [], 'Student': []})
  CourseParticipants[courseId][row['userRole'].capitalize()].append(row['profile.emailAddress'])

for courseId, courseInfo in sorted(iter(CourseParticipants.items())):
  outputCSV.writerow({'courseId': courseId,
                      'courseName': courseInfo['courseName'],
                      'Teacher': DELIMITER.join(courseInfo['Teacher']),
                      'Student': DELIMITER.join(courseInfo['Student'])})

inputFile.close()
outputFile.close()
