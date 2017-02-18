#!/bin/python
import urllib2
import json
from ctypes import *
from datetime import datetime, timedelta
import socket
import time
import string
import sys
import os
import signal
from   geopy.distance import vincenty       # use the Vincenty algorithm^M
import MySQLdb                              # the SQL data base routines^M
from pprint import pprint
import hashlib
import base64
import hmac
import urllib
import random
import config


#-------------------------------------------------------------------------------------------------------------------#
def skylgetapidata(url): 	                 # get the data from the API server
	req = urllib2.Request(url)                      
	req.add_header("Accept","application/json")
	req.add_header("Content-Type","application/json")
	r = urllib2.urlopen(req)                # open the url resource
	j_obj = json.load(r)                    # convert to JSON
	return j_obj                            # return the JSON object
#-------------------------------------------------------------------------------------------------------------------#



def skylstoreitindb(datafix, curs, conn):	# store the fix into the database
	for fix in datafix['skylpos']:		# for each fix on the dict
		id=fix['registration'][0:9]	# extract the information
		dte=fix['date'] 
		hora=fix['time'] 
		station="SKYL"
		latitude=fix['Lat'] 
		longitude=fix['Long'] 
		altim=fix['altitude'] 
		speed=fix['speed'] 
		course=fix['course'] 
		roclimb=fix['roc'] 
		rot=0
		sensitivity=0
		gps=fix['GPS']
		uniqueid=str(fix["UnitID"])
		dist=fix['dist']
		extpos=fix['extpos']
		addcmd="insert into OGNDATA values ('" +id+ "','" + dte+ "','" + hora+ "','" + station+ "'," + str(latitude)+ "," + str(longitude)+ "," + str(altim)+ "," + str(speed)+ "," + \
               str(course)+ "," + str(roclimb)+ "," +str(rot) + "," +str(sensitivity) + \
               ",'" + gps+ "','" + uniqueid+ "'," + str(dist)+ ",'" + extpos+ "', 'SKYL' ) ON DUPLICATE KEY UPDATE extpos = '!ZZZ!' "
        	try:				# store it on the DDBB
			#print addcmd
              		curs.execute(addcmd)
        	except MySQLdb.Error, e:
              		try:
                     		print ">>>MySQL Error [%d]: %s" % (e.args[0], e.args[1])
              		except IndexError:
                     		print ">>>MySQL Error: %s" % str(e)
                     		print ">>>MySQL error:", cout, addcmd
                    		print ">>>MySQL data :",  data
			return (False)	# indicate that we have errors
        conn.commit()                   # commit the DB updates
	return(True)			# indicate that we have success


#-------------------------------------------------------------------------------------------------------------------#

def skylfindpos(ttime, conn):		# find all the fixes since TTIME . Scan all the SKYL devices for new data

	curs=conn.cursor()              # set the cursor for storing the fixes
	cursG=conn.cursor()             # set the cursor for searching the devices
	url="https://skylines.aero/api/live" 
	skylpos={"skylpos":[]}		# init the dicta
	pos=skylgetapidata(url)	# get the JSON data from the Skylines server
	#print json.dumps(pos, indent=4) # convert JSON to dictionary
	tracks=pos['tracks']
	cursG.execute("select id, Registration, active from TRKDEVICES where devicetype = 'SKYL' ; " ) 	# get all the devices with SKYL
        for rowg in cursG.fetchall(): 	# look for that registration on the OGN database
                                
        	reg=rowg[0]		# registration to report
        	deviceID=rowg[1]	# Glider registration EC-???
        	active=rowg[2]		# if active or not
		if active == 0:
			continue	# if not active, just ignore it
					# build the userlist to call to the SKYL server
		skyladdpos(tracks, skylpos, ttime, reg)	# find the gliders since TTIME

	skylstoreitindb(skylpos, curs, conn)			# and store it on the DDBB
	now=datetime.utcnow()
	td=now-datetime(1970,1,1)       # number of second until beginning of the day of 1-1-1970
	sync=int(td.total_seconds())	# as an integer
	return (sync+1)			# return TTIME for next call

#-------------------------------------------------------------------------------------------------------------------#
def skyladdpos(tracks, skylpos, ttime, regis):	# extract the data of the last know position from the JSON object

	for msg in tracks:
		pilot=msg['pilot']		# get the pilot infor id/name
		name=pilot['name']		# pilot name
		id=pilot['id']			# pilot ID
		if regis != name:		# if is not this pilot nothing to do
			continue
		dte=msg['time']			# get the time on ISO format
		ttt=datetime.strptime(dte,"%Y-%m-%dT%H:%M:%S+00:00") # parser the time
		td=ttt-datetime(1970,1,1)      	# number of second until beginning of the day
		ts=int(td.total_seconds())	# Unix time - seconds from the epoch
		if ts < ttime:			# check if the data is from before
			continue		# in that case nothing to do
		location=msg['location']
		lon=location[0] 
		lat=location[1] 		# extract the longitude and latitude
		alt=msg["altitude"] 		# and the altitude
		gps="NO"
		extpos="NO"
		roc=0
		dir=0
		spd=0
		date=dte[2:4]+dte[5:7]+dte[8:10]
        	time=dte[11:13]+dte[14:16]+dte[17:19]
	
		vitlat   =config.FLOGGER_LATITUDE
		vitlon   =config.FLOGGER_LONGITUDE
		distance=vincenty((lat, lon),(vitlat,vitlon)).km    # distance to the statio
		pos={"registration": regis, "date": date, "time":time, "Lat":lat, "Long": lon, "altitude": alt, "UnitID":id, "dist":distance, "course":dir, "speed": spd, "roc":roc, "GPS":gps , "extpos":extpos}
		skylpos['skylpos'].append(pos)		# and store it on the dict
		print "SKYLPOS :", round(lat,4), round(lon,4), alt, id, round(distance,4), ts, dte, date, time, regis
		#print "POS:", pos			# print it as a control


	return 					# indicate that we added an entry to the dict


#-------------------------------------------------------------------------------------------------------------------#
