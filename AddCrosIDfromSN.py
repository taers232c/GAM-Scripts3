#!/usr/bin/env python3
"""
# Purpose: For a CSV file containing CrOS device serial numbers and other data, create a new CSV file with the same columns
# plus a deviceId column based on the serial number. The updated file can be used to more efficiently process large
# numbers of CrOS devices.
#
# Old update method, requires an additional API call per device to convert the serial number to the device ID that the update requires
#  $ gam csv CrosData.csv gam update cros cros_sn "~serialNumber" ...
# New update method
#  $ gam redirect csv ./CrosSNIDMap.csv print cros fields serialnumber
#  $ python3 AddCrosIDfromSN.py ./CrosSNIDMap.csv ./CrosData.csv ./CrosDataID.csv
# An error message is generated for any serial number in CrosData.csv that is not in CrosSNIDMap.csv and the return code is 1
#  $ gam config_csv_input_row_filter "deviceId:regex:^.+$" csv CrosDataID.csv gam update cros "~deviceId" ...
#
# Note: This script can use GAM7 or Advanced GAM:
#       https://github.com/GAM-team/GAM                                                                                                                               
#	https://github.com/taers232c/GAMADV-XTD3
# Customize: DATA_SN_HEADER
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Generate a list of CrOS deviceIds and serial numbers
#  gam print cros fields serialnumber > CrosSNIDMap.csv
# 2: Generate an output CSV file with the same headers as CrosData.csv plus a header for the deviceId
#  $ python3 AddCrosIDfromSN.py ./CrosSNIDMap.csv ./CrosData.csv ./CrosDataID.csv
"""

import csv
import sys

# Do not change these values
CROS_SN_HEADER = 'serialNumber'
CROS_DEVICEID_HEADER = 'deviceId'

# Indicate the header in CrosData.csv that contains the serial number
DATA_SN_HEADER = 'serialNumber'

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

crosSNIDMap = {}
crosSNIDMapFileName = sys.argv[1]
inputFile = open(crosSNIDMapFileName, 'r', encoding='utf-8')
for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  crosSNIDMap[row[CROS_SN_HEADER].upper()] = row[CROS_DEVICEID_HEADER]
inputFile.close()

inputFileName = sys.argv[2]
inputFile = open(inputFileName, 'r', encoding='utf-8')
inputCSV = csv.DictReader(inputFile, quotechar=QUOTE_CHAR)

outputFieldNames = inputCSV.fieldnames[:]
if DATA_SN_HEADER not in outputFieldNames:
  sys.stderr.write(f'Error: field {DATA_SN_HEADER} is not in Data file {inputFileName} field names: {",".join(outputFieldNames)}\n')
  sys.exit(3)
if CROS_DEVICEID_HEADER not in outputFieldNames:
  index = outputFieldNames.index(DATA_SN_HEADER)
  outputFieldNames.insert(index+1, CROS_DEVICEID_HEADER)

outputFile = open(sys.argv[3], 'w', encoding='utf-8', newline='')
outputCSV = csv.DictWriter(outputFile, outputFieldNames, lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

sysRC = 0
for row in inputCSV:
  deviceId = crosSNIDMap.get(row[DATA_SN_HEADER].upper(), '')
  if deviceId:
    row[CROS_DEVICEID_HEADER] = deviceId
  else:
    sys.stderr.write(f'Error: Serial number {row[DATA_SN_HEADER]} is not in Serial Number/DeviceID file {crosSNIDMapFileName}\n')
    sysRC = 1
  outputCSV.writerow(row)

inputFile.close()
outputFile.close()
sys.exit(sysRC)
