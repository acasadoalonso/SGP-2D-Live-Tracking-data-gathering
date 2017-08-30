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
import config
import kglid
from flarmfuncs import *


def captgetapidata(url, prt=False):                      	# get the data from the API server

	req = urllib2.Request(url)		# build the request
	req.add_header("Content-Type","application/json")
	req.add_header("Content-type", "application/x-www-form-urlencoded")
    	r = urllib2.urlopen(req)                # open the url resource
	j_obj = json.load(r)                    # convert to JSON
	if prt:
		print json.dumps(j_obj, indent=4)
    	return j_obj                            # return the JSON object


def captaddpos(msg, captpos, ttime, captID, flarmid):	# extract the data from the JSON object

	unixtime=msg["timestamp"] 		# the time from the epoch
	if (unixtime < ttime):
		return (False)			# if is lower than the last time just ignore it
	lat	=msg["latitude"] 		# extract from the JSON object the data that we need
	lon	=msg["longitude"]
	alt	=msg["altitude"]		# low accuracy altitude
	device 	=msg["device"]			# the CAPTURS device ID
	speed	=msg["speed"]			# low accuracy speed
	dte	=msg["date"]			# date on format: :"Wed Jan 25 2017 22:52:41 GMT"
	tme	=datetime.utcfromtimestamp(unixtime)	# get the time from the timestamp
	date	=tme.strftime("%y%m%d")		# the date
	time	=tme.strftime("%H%M%S")		# the time
	vitlat  =config.FLOGGER_LATITUDE
	vitlon  =config.FLOGGER_LONGITUDE
	distance=vincenty((lat, lon),(vitlat,vitlon)).km    # distance to the statio
	pos={"registration": flarmid, "date": date, "time":time, "Lat":lat, "Long": lon, "altitude": alt, "speed":speed, "dist":distance, "device":captID}
	captpos['captpos'].append(pos)		# and store it on the dict
	print "CAPTPOS :", lat, lon, alt, device, distance, unixtime, dte, captID, flarmid
	return (True)				# indicate that we added an entry to the dict

def captgetaircraftpos(data, captpos, ttime, captID, flarmid, prt=False):	# return on a dictionary the position of all spidertracks
	msgcount    =data['result']		# get the count of messages
	messages    =data['position']		# get the messages
	found=False
	#print "M:", message
	for msg in messages:		# if not iterate the set of messages
		if prt:
			print json.dumps(msg, indent=4)        # convert JSON to dictionary
		found=captaddpos(msg, captpos, ttime, captID, flarmid)
	return (found)				# return if we found a message or not

def captstoreitindb(datafix, curs, conn):	# store the fix into the database
	for fix in datafix['captpos']:		# for each fix on the dict
		id=fix['registration'] 		# extract the information
		if len(id) > 9:
			id=id[0:9]
		dte=fix['date']
		hora=fix['time']
		station=config.location_name
		latitude=fix['Lat']
		longitude=fix['Long']
		altim=fix['altitude']
		speed=fix['speed']
		course=0
		roclimb=0
		rot=0
		sensitivity=0
		gps=' '
		uniqueid=' '
		dist=fix['dist']
		extpos=' '
		addcmd="insert into OGNDATA values ('" +id+ "','" + dte+ "','" + hora+ "','" + station+ "'," + str(latitude)+ "," + str(longitude)+ "," + str(altim)+ "," + str(speed)+ "," + \
               str(course)+ "," + str(roclimb)+ "," +str(rot) + "," +str(sensitivity) + \
               ",'" + gps+ "','" + uniqueid+ "'," + str(dist)+ ",'" + extpos+ "', 'CAPT' ) "
        	try:				# store it on the DDBB
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


def captfindpos(ttime, conn, prt=True, store=True):	# find all the fixes since TTIME

	captLOGIN=config.CAPTURSlogin	# login of the control capture account
	captPASSWD=config.CAPTURSpasswd
	curs=conn.cursor()              # set the cursor for storing the fixes
	cursG=conn.cursor()             # set the cursor for searching the devices
	cursG.execute("select id, active, flarmid, registration from TRKDEVICES where devicetype = 'CAPT'; " ) 	# get all the devices with CAPT
        for rowg in cursG.fetchall(): 	# look for that registration on the OGN database

        	captID=rowg[0]		# registration to report
        	active=rowg[1]		# if active or not
        	flarmid=rowg[2]		# Flamd id to be linked
        	registration=rowg[3]	# registration id to be linked
		if active == 0:
			continue	# if not active, just ignore it
		if flarmid == None or flarmid == '': 		# if flarmid is not provided
			flarmid=getflarmid(conn, registration)	# get it from the registration
		else:
			chkflarmid(flarmid)

					# build the URL to call to the CAPTURS server
# http://api.capturs.com/device/1AC32E/position/from/1484053861/to/1484917861/limit/1?login=myLogin&password=myPassword
		url="https://api.capturs.com/device/"+captID+"/position/from/"+str(ttime)+"?login="+captLOGIN+"password="+str(captPASSWD)
		captpos={"captpos":[]}				# init the dict
		jsondata=captgetapidata(url)			# get the JSON data from the CAPT server
		if prt:						# if we require printing the raw data
			j=json.dumps(jsondata, indent=4)	# convert JSON to dictionary
			print j
		found=captgetaircraftpos(jsondata, captpos, ttime, captID, flarmid, prt=False)	# find the gliders since TTIME
		if prt:
			print captpos
		if store:
			captstoreitindb(captpos, curs, conn)	# and store it on the DDBB

	now=datetime.utcnow()
	td=now-datetime(1970,1,1)       # number of second until beginning of the day of 1-1-1970
	ts=int(td.total_seconds())	# as an integer
	return (ts)			# return TTIME for next call

#-------------------------------------------------------------------------------------------------------------------#
