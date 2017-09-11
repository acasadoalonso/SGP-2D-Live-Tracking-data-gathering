#!/bin/python
import urllib2
import json
import xml.etree.ElementTree as ET
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
from parserfuncs import deg2dms

def spotgetapidata(url, prt=False):                      	# get the data from the API server

        req = urllib2.Request(url)		# buil the request
	req.add_header("Content-Type","application/json")
	req.add_header("Content-type", "application/x-www-form-urlencoded")
        r = urllib2.urlopen(req)                # open the url resource
	j_obj = json.load(r)                    # convert to JSON
	if prt:
		print json.dumps(j_obj, indent=4) 
        return j_obj                            # return the JSON object


def spotaddpos(msg, spotpos, ttime, regis, flarmid):	# extract the data from the JSON object

	unixtime=msg["unixTime"] 		# the time from the epoch
	alt=msg["altitude"] 
	if (unixtime < ttime or altitude == 0):
		return (False)			# if is lower than the last time just ignore it
	reg=regis
	lat=msg["latitude"] 			# extract from the JSON object the data that we need
	lon=msg["longitude"] 
	id =msg["messengerId"] 			# identifier for the final user
	mid=msg["modelId"] 			# spot model number
	dte=msg["dateTime"] 
	extpos=msg["batteryState"] 		# battery state 
	date=dte[2:4]+dte[5:7]+dte[8:10]
        time=dte[11:13]+dte[14:16]+dte[17:19]
	if 'GOOD' not in msg.get('batteryState', 'GOOD'):
       		print "WARNING: spot battery is in state: %s ID=%s " % (msg.get('batteryState'), regis)
	vitlat   =config.FLOGGER_LATITUDE
	vitlon   =config.FLOGGER_LONGITUDE
	distance=vincenty((lat, lon),(vitlat,vitlon)).km    # distance to the statioan
	pos={"registration": flarmid, "date": date, "time":time, "Lat":lat, "Long": lon, "altitude": alt, "UnitID":id, "GPS":mid, "dist":distance, "extpos":extpos}
	spotpos['spotpos'].append(pos)		# and store it on the dict
	print "SPOTPOS :", lat, lon, alt, id, distance, unixtime, dte, date, time, reg, flarmid, extpos
	return (True)				# indicate that we added an entry to the dict

def spotgetaircraftpos(data, spotpos, ttime, regis, flarmid, prt=False):	# return on a dictionary the position of all spidertracks
	foundone=False
	response    =data['response']		# get the response entry
	if response.get('errors'):		# if error found
		return(False)			# return indicating errors

	feed        =response["feedMessageResponse"]	# get the message response
	msgcount    =feed['count']		# get the count of messages
	messages    =feed['messages']		# get the messages
	message     =messages['message']	# get the individual message
	#print "M:", message
	if msgcount == 1:			# if only one message, that is the message
		if prt:
			print json.dumps(feed, indent=4)        # convert JSON to dictionary
		found=spotaddpos(message, spotpos, ttime, regis, flarmid)
		foundone=found
	else:
		for msg in message:		# if not iterate the set of messages
			if prt:
				print json.dumps(msg, indent=4)        # convert JSON to dictionary
			found=spotaddpos(msg, spotpos, ttime, regis, flarmid) 	# add the position for this fix
			if found:
				foundone=True
	return (foundone)			# return if we found a message or not

def spotstoreitindb(datafix, curs, conn):	# store the fix into the database
	for fix in datafix['spotpos']:		# for each fix on the dict
		id=fix['registration'] 		# extract the information
		if len(id) > 9:
			id=id[0:9]
		dte=fix['date'] 
		hora=fix['time'] 
		station=config.location_name
		latitude=fix['Lat'] 
		longitude=fix['Long'] 
		altim=fix['altitude'] 
		speed=0
		course=0
		roclimb=0
		rot=0
		sensitivity=0
		gps=fix['GPS']			# model id
		gps=gps[0:6]
		uniqueid=str(fix["UnitID"])	# identifier of the owner
		dist=fix['dist']
		extpos=fix['extpos']		# battery state
		addcmd="insert into OGNDATA values ('" +id+ "','" + dte+ "','" + hora+ "','" + station+ "'," + str(latitude)+ "," + str(longitude)+ "," + str(altim)+ "," + str(speed)+ "," + \
               str(course)+ "," + str(roclimb)+ "," +str(rot) + "," +str(sensitivity) + \
               ",'" + gps+ "','" + uniqueid+ "'," + str(dist)+ ",'" + extpos+ "', 'SPOT' ) "
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

def spotaprspush(datafix, prt=False):	# push the data into the OGN APRS
	for fix in datafix['spotpos']:	# for each fix on the dict
		id=fix['registration'] 	# extract the information
		if len(id) > 9:
			id=id[0:9]
		dte=fix['date'] 
		hora=fix['time'] 
		latitude=fix['Lat'] 
		longitude=fix['Long'] 
		altitude=fix['altitude'] 
		speed=0
		course=0
		roclimb=0
		rot=0
		sensitivity=0
		gps=fix['GPS']
		uniqueid=str(fix["UnitID"])	# identifier of the owner
		dist=fix['dist']
		extpos=fix['extpos']		# battery state
						# build the APRS message
		lat=deg2dms(abs(latitude))	# conver the latitude to the format required by APRS
		if latitude > 0:
			lat += 'N'
		else:
			lat += 'S'
		lon=deg2dms(abs(longitude))
		if abs(longitude) < 100.0:
			lon = '0'+lon
		if longitude > 0:
			lon += 'E'
		else:
			lon += 'W'
		
		aprsmsg=id+">OGSPOT,qAS,SPOT:/"+hora+'h'+lat+"/"+lon+"'000/000/"
		if altitude > 0:
			aprsmsg += "A=%06d"%int(altitude*3.28084)
		aprsmsg += " id"+uniqueid+" "+gps+" "+extpos+" \n"
		rtn = config.SOCK_FILE.write(aprsmsg) 
		print "APRSMSG : ", aprsmsg
	return(True)

def spotfindpos(ttime, conn, prt=False, store=True, aprspush=False):	# find all the fixes since TTIME

	foundone=False			# asume no found
	curs=conn.cursor()              # set the cursor for storing the fixes
	cursG=conn.cursor()             # set the cursor for searching the devices
	cursG.execute("select id, spotid, spotpasswd, active, flarmid, registration from TRKDEVICES where devicetype = 'SPOT'; " ) 	# get all the devices with SPOT
        for rowg in cursG.fetchall(): 	# look for that registration on the OGN database
                                
        	reg=rowg[0]		# registration to report
        	spotID=rowg[1]		# SPOTID
        	spotpasswd=rowg[2]	# SPOTID password
        	active=rowg[3]		# if active or not
        	flarmid=rowg[4]		# Flamd id to be linked
        	registration=rowg[5]	# registration id to be linked
		if active == 0:
			continue	# if not active, just ignore it
		if flarmid == None or flarmid == '': 		# if flarmid is not provided 
			flarmid=getflarmid(conn, registration)	# get it from the registration
		else:
			chkflarmid(flarmid)

					# build the URL to call to the SPOT server
		if spotpasswd == '' or spotpasswd == None:
			url="https://api.findmespot.com/spot-main-web/consumer/rest-api/2.0/public/feed/"+spotID+"/message.json"
		else:
			url="https://api.findmespot.com/spot-main-web/consumer/rest-api/2.0/public/feed/"+spotID+"/message.json?feedPassword="+str(spotpasswd)
		if prt:
			print url
		spotpos={"spotpos":[]}				# init the dict
		jsondata=spotgetapidata(url)			# get the JSON data from the SPOT server
		if prt:						# if we require printing the raw data
			j=json.dumps(jsondata, indent=4)	# convert JSON to dictionary
			print j
		found=spotgetaircraftpos(jsondata, spotpos, ttime, reg, flarmid, prt=False)	# find the gliders since TTIME
		if found:
			foundone=True
		if prt:
			print spotpos
		if store:
			spotstoreitindb(spotpos, curs, conn)	# and store it on the DDBB
		if aprspush:
			spotaprspush(spotpos, prt)		# and push the data into the APRS
	
	if foundone:
		now=datetime.utcnow()
		td=now-datetime(1970,1,1)       # number of second until beginning of the day of 1-1-1970
		ts=int(td.total_seconds())	# as an integer
		return (ts)			# return TTIME for next call
	else:
		return (ttime)			# keep old value

#-------------------------------------------------------------------------------------------------------------------#


