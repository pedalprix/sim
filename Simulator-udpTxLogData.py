#!/usr/bin/env python
# GPS UDP Tx

import socket
import json
import time
import datetime
import sys

def printusage():
   print "ERROR with command line arguements"
   print "USAGE: sudo python Log-popRFID-UID.py [-clear|-append] <filename>"
   print "   Eg: sudo python Log-popRFID-UID.py Log-config-UID_rider.json"
   print "       => will process Log-config-UID_rider.json WITHOUT clearing database \n"
   print "       sudo python Log-popRFID-UID.py -clear Log-config-UID_rider.json"
   print "       => will process Log-config-UID_rider.json AFTER clearing database table"
   sys.exit()
   return

# Command line arg processing
try:
   # Get args passed in command line
   args = len(sys.argv) - 1
   if args == 2:
      REPLAY_SPEED = float(sys.argv[1])
      START_REPLAY_LINE = int(sys.argv[2])
   elif args == 1:
      REPLAY_SPEED = float(sys.argv[1])
      START_REPLAY_LINE = 0
   elif args == 0:
      REPLAY_SPEED = 1.0
      START_REPLAY_LINE = 0
   else:
      printusage()
   print "Happy here"
   print "REPLAY_SPEED = ",REPLAY_SPEED
   print "START_REPLAY_LINE = ",START_REPLAY_LINE
   # Do some range checking
   if REPLAY_SPEED > 0.1:
      pass
   if REPLAY_SPEED <= 1000:
      pass
   else:
      printusage()

   if START_REPLAY_LINE >= 0:
      pass
   else:
      print "Failed range checking"
      printusage()

except:
   printusage()


def is_json(myjson):
  try:
    json_object = json.loads(myjson)
  except ValueError, e:
    return False
  return True

# open car_config.json and read
configfile = open('Simulator-config.json', 'r')
configjson = configfile.read()
configfile.close()

# parse configdata
json_data = json.loads(configjson)
car_name = json_data['Car_Name']
GPS_LOG_IP = json_data['GPS_LOG_IP']
GPS_LOG_PORT = int(json_data['GPS_LOG_PORT'])
# REPLAY_SPEED = float(json_data['REPLAY_SPEED'])
REPLAY_DELAY = 1/REPLAY_SPEED

msg_type = "GPS"

GPS_LOG_ADDR = (GPS_LOG_IP, GPS_LOG_PORT)

GPS_Log_Msg_Count = 0

def JSON_Header():
   global car_name
   global msg_type
   global GPS_Log_Msg_Count
   GPS_Log_Msg_Count += 1
   Header = '{"TimeACST":"' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
   Header +='","Msg_Count":"'+ str(GPS_Log_Msg_Count)
   Header +='","Car_Name":"' + car_name
   Header +='","Msg_Type":"' + msg_type
   Header +='","Msg":['
   return Header

JSON_Footer = ']}'

# open UDP socket to GPS Log server
sGPS_Log = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# open log file for reading
file = open('VicParkRaceData.log', 'r')

LINEcount = 0
prevprevMSG = ""
prevMSG = ""
MSG = ""

while LINEcount <= START_REPLAY_LINE:
   prevprevMSG = prevMSG
   prevMSG = MSG
   MSG = file.readline()
   LINEcount += 1


JSONcount = 0
blankcount = 0
INVALIDcount = 0
FIXEDcount = 0
ERRORcount = 0

try:
   while MSG:
	MSG = MSG.strip()

	if not MSG:
		blankcount += 1

		MSG = file.readline()
		LINEcount += 1

	elif is_json(MSG):
		JSONcount += 1
		MSG = JSON_Header() + MSG + JSON_Footer
		sGPS_Log.sendto(MSG, GPS_LOG_ADDR)
		print "Good message sent.  Count =", JSONcount
		time.sleep(REPLAY_DELAY)
		MSG = file.readline()
		LINEcount += 1

	else: # length > 0  but not valid json so look at appending next line
		INVALIDcount += 1
		prevprevMSG = prevMSG
		prevMSG = MSG
		MSG = file.readline()
		LINEcount += 1

		TEST = prevMSG + MSG
		if is_json (TEST):

			FIXEDcount += 1
			JSONcount += 1
			TEST = JSON_Header() + TEST + JSON_Footer
			sGPS_Log.sendto(TEST, GPS_LOG_ADDR)
                        print "Fixed message sent. Count = ", JSONcount
			time.sleep(REPLAY_DELAY)

			MSG = file.readline()
			LINEcount += 1

		else:
			ERRORcount += 1
			print "========================================="
			print "ERROR No: ", ERRORcount
			print "prevprevMSG=============================="
			print prevprevMSG
			print "prevMSG=================================="
			print prevMSG


	TESTING = False
	if TESTING and JSONcount > 470 and JSONcount < 480:
		print "========================================="
		print "JSON Count: ",JSONcount
		print MSG

   print "### EOF REACHED ###"

finally:
	print "Total lines read: ", LINEcount
	print "Blank lines: ", blankcount
	print "Invalid MSGs: ", INVALIDcount
	print "MSGs: ", JSONcount
	print "Fixed MSGs: ", FIXEDcount
	print "Unfixed MSGs: ", ERRORcount
	
	sGPS_Log.close()
