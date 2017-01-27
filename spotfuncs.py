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


# simple wrapper function to encode the username & pass
def encodeUserData(user, password):
    return "Basic " + (user + ":" + password).encode("base64").rstrip()

def spotgetapidata(url):                      # get the data from the API server

        req = urllib2.Request(url)
	req.add_header("Content-Type","application/json")
	req.add_header("Content-type", "application/x-www-form-urlencoded")
        r = urllib2.urlopen(req)                # open the url resource
	j_obj = json.load(r)                    # convert to JSON
        return j_obj                            # return the JSON object


def spotaddpos(msg, spotpos, ttime, regis):

	unixtime=msg["unixTime"] 
	if (unixtime < ttime):
		return (False)
	reg=regis
	lat=msg["latitude"] 
	lon=msg["longitude"] 
	alt=msg["altitude"] 
	id =msg["id"] 
	mid=msg["modelId"] 
	dte=msg["dateTime"] 
	date=dte[2:4]+dte[5:7]+dte[8:10]
        time=dte[11:13]+dte[14:16]+dte[17:19]
	vitlat   =config.FLOGGER_LATITUDE
	vitlon   =config.FLOGGER_LONGITUDE
	distance=vincenty((lat, lon),(vitlat,vitlon)).km    # distance to the statio
	pos={"registration": reg, "date": date, "time":time, "Lat":lat, "Long": lon, "altitude": alt, "UnitID":id, "dist":distance}
	spotpos['spotpos'].append(pos)
	print "POS:", lat, lon, alt, id, distance, unixtime, dte, date, time, reg
	print "POS:", pos
	return (True)

def spotgetaircraftpos(data, spotpos, ttime, regis):			# return on a dictionary the position of all spidertracks
	response    =data['response']
	if response.get('errors'):
		return(False)
	feed        =response["feedMessageResponse"]
	msgcount    =feed['count']
	messages    =feed['messages']
	message     =messages['message']
	found=False
	#print "M:", message
	if msgcount == 1:
		found=spotaddpos(message, spotpos, ttime, regis)
	else:
		for msg in message:
			found=spotaddpos(msg, spotpos, ttime, regis)
	return (found)

def spotstoreitindb(datafix, curs, conn):
	for fix in datafix['spotpos']:
		id=fix['registration'] 
		dte=fix['date'] 
		hora=fix['time'] 
		station="SPOT"
		latitude=fix['Lat'] 
		longitude=fix['Long'] 
		altim=fix['altitude'] 
		speed=0
		course=0
		roclimb=0
		rot=0
		sensitivity=0
		gps=""
		uniqueid=str(fix["UnitID"])
		dist=fix['dist']
		extpos=""
		addcmd="insert into SPIDERSPOTDATA values ('" +id+ "','" + dte+ "','" + hora+ "','" + station+ "'," + str(latitude)+ "," + str(longitude)+ "," + str(altim)+ "," + str(speed)+ "," + \
               str(course)+ "," + str(roclimb)+ "," +str(rot) + "," +str(sensitivity) + \
               ",'" + gps+ "','" + uniqueid+ "'," + str(dist)+ ",'" + extpos+ "') ON DUPLICATE KEY UPDATE extpos = '!ZZZ!' "
        	try:
              		curs.execute(addcmd)
        	except MySQLdb.Error, e:
              		try:
                     		print ">>>MySQL Error [%d]: %s" % (e.args[0], e.args[1])
              		except IndexError:
                     		print ">>>MySQL Error: %s" % str(e)
                     		print ">>>MySQL error:", cout, addcmd
                    		print ">>>MySQL data :",  data
			return (False)
        conn.commit()                   # commit the DB updates
	return(True)


def spotfindpos(ttime, conn):

	curs=conn.cursor()                      # set the cursor
	cursG=conn.cursor()                      # set the cursor
	cursG.execute("select id, spotid, active from SPOTDEVICES; " )
        for rowg in cursG.fetchall(): # look for that registration on the OGN database
                                
        	reg=rowg[0]
        	spotID=rowg[1]
        	active=rowg[2]
		if active == 0:
			continue
		url="https://api.findmespot.com/spot-main-web/consumer/rest-api/2.0/public/feed/"+spotID+"/message.json"
		spotpos={"spotpos":[]}
		jsondata=spotgetapidata(url)
		j=json.dumps(jsondata, indent=4)
		#print j
		found=spotgetaircraftpos(jsondata, spotpos, ttime, reg)
		spotstoreitindb(spotpos, curs, conn)
	
	now=datetime.utcnow()
	td=now-datetime(1970,1,1)         # number of second until beginning of the day
	ts=int(td.total_seconds())
	return (ts)


