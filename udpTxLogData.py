#!/usr/bin/env python

# Reads the nohup log file for VicPark and plays jsons to 

import socket
import json
import time

def is_json(myjson):
  try:
    json_object = json.loads(myjson)
  except ValueError, e:
    return False
  return True

LoopDelay = 1
Replay_Start = 0
Replay_End = 0

# open config.json and read
file = open('Car-config.json', 'r')
data = file.read()
file.close()

# parse config info
json_data = json.loads(data)
car_name = json_data['Car_Name']
DEST_IP = json_data['DEST_IP']
DEST_PORT = int(json_data['DEST_PORT'])

DEST_ADDR = (DEST_IP, DEST_PORT)
msg_type = "GPS"
Header = '{"car_name":"' + car_name + '","msg_type":"' + msg_type + '",'


print "UDP target IP:", DEST_IP
print "UDP target port:", DEST_PORT

UDPsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# open log file for reading
file = open('VicParkRaceData.log', 'r')

prevprevMSG = ""
prevMSG = ""
MSG = file.readline()
LINEcount = 1

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
		MSG = Header + MSG[1:MSG.count('')-1]
#		print "Sending message...", JSONcount
#		print MSG
		UDPsock.sendto(MSG, DEST_ADDR)
		time.sleep(LoopDelay)
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
			print "BROKEN 1=================================================="
			print prevMSG
			print "BROKEN 2--------------------------------------------------"
			print MSG
			FIXEDcount += 1
			JSONcount += 1
			TEST = Header + TEST[1:TEST.count('')-1]
			print "FIXED-----------------------------------------------------"
			print TEST
			UDPsock.sendto(TEST, DEST_ADDR)
			time.sleep(LoopDelay)

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
	
	UDPsock.close()
