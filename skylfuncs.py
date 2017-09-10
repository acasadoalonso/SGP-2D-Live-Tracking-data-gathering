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
import kglid
from flarmfuncs import *
from parserfuncs import deg2dms

#-------------------------------------------------------------------------------------------------------------------#
def skylgetapidata(url): 	                 # get the data from the API server
	req = urllib2.Request(url)                      
	req.add_header("Accept","application/json")
	req.add_header("Content-Type","application/json")
	r = urllib2.urlopen(req)                # open the url resource
	j_obj = json.load(r)                    # convert to JSON
	return j_obj                            # return the JSON object
#-------------------------------------------------------------------------------------------------------------------#

def skyladdpos(tracks, skylpos, ttime, pilotname, gliderreg):	# extract the data of the last know position from the JSON object

	foundone=False
	for msg in tracks:
		pilot=msg['pilot']		# get the pilot infor id/name
		name=pilot['name']		# pilot name
		id=pilot['id']			# pilot ID
		pilotname=pilotname.decode("utf-8")
		if pilotname.isnumeric():	# id numeric is pilot id
			if pilotname.strip(' ') != id.strip(' '):	# if is not this pilot id nothing to do
				continue
		else:
			if pilotname.strip(' ') != name.strip(' '):	# if is not this pilot name nothing to do
				continue
		foundone=True
		dte=msg['time']			# get the time on ISO format
		dte=dte[0:19]			# get the important part			
		ttt=datetime.strptime(dte,"%Y-%m-%dT%H:%M:%S") # parser the time
		td=ttt-datetime(1970,1,1)      	# number of second until beginning of the day
		ts=int(td.total_seconds())	# Unix time - seconds from the epoch
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
		pos={"pilotname": pilotname, "date": date, "time":time, "Lat":lat, "Long": lon, "altitude": alt, "UnitID":id, "dist":distance, "course":dir, "speed": spd, "roc":roc, "GPS":gps , "extpos":extpos, "gliderreg":gliderreg}
		#print "SSS:", ts, ttime, pos
		if ts < ttime+30:		# check if the data is from before
			continue		# in that case nothing to do
		skylpos['skylpos'].append(pos)	# and store it on the dict
		print "SKYLPOS :", round(lat,4), round(lon,4), alt, id, round(distance,4), ts, dte, date, time, pilotname


	return(foundone) 					# indicate that we added an entry to the dict


#-------------------------------------------------------------------------------------------------------------------#


def skylstoreitindb(datafix, curs, conn):	# store the fix into the database

	for fix in datafix['skylpos']:		# for each fix on the dict
		id=fix['pilotname']		# extract the information
		dte=fix['date'] 
		hora=fix['time'] 
		station=config.location_name
		latitude=fix['Lat'] 
		longitude=fix['Long'] 
		altitude=fix['altitude'] 
		speed=fix['speed'] 
		course=fix['course'] 
		roclimb=fix['roc'] 
		rot=0
		sensitivity=0
		gps=fix['GPS']
		uniqueid=str(fix["UnitID"])
		dist=fix['dist']
		extpos=fix['extpos']
		gliderreg=fix['gliderreg']
		flarmid=getflarmid(conn, gliderreg)
		addcmd="insert into OGNDATA values ('" +flarmid+ "','" + dte+ "','" + hora+ "','" + station+ "'," + str(latitude)+ "," + str(longitude)+ "," + str(altitude)+ "," + str(speed)+ "," + \
               str(course)+ "," + str(roclimb)+ "," +str(rot) + "," +str(sensitivity) + \
               ",'" + gps+ "','" + uniqueid+ "'," + str(dist)+ ",'" + extpos+ "', 'SKYL' ) "
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

def skylaprspush(datafix, conn, prt=False):

	for fix in datafix['skylpos']:		# for each fix on the dict
		id=fix['pilotname']		# extract the information
		dte=fix['date'] 
		hora=fix['time'] 
		station=config.location_name
		latitude=fix['Lat'] 
		longitude=fix['Long'] 
		altitude=fix['altitude'] 
		speed=fix['speed'] 
		course=fix['course'] 
		roclimb=fix['roc'] 
		rot=0
		sensitivity=0
		gps=fix['GPS']
		uniqueid=str(fix["UnitID"])
		dist=fix['dist']
		extpos=fix['extpos']
		gliderreg=fix['gliderreg']
		flarmid=getflarmid(conn, gliderreg)
						# build the APRS message
		lat=deg2dms(abs(latitude))
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
		
		ccc="%03d"%int(course)
		sss="%03d"%int(speed)
		aprsmsg=flarmid+">OGSKYL,qAS,SKYLINES:/"+hora+'h'+lat+"/"+lon+"'"+ccc+"/"+sss+"/"
		if altitude > 0:
			aprsmsg += "A=%06d"%int(altitude*3.28084)
		aprsmsg += " %+04dfpm "%(int(roclimb))+" id"+uniqueid+" \n" 
		if True:
			print "APRSMSG: ", aprsmsg
		rtn = config.SOCK_FILE.write(aprsmsg)

	return (True)

#-------------------------------------------------------------------------------------------------------------------#

def skylfindpos(ttime, conn, prt=False, store=True, aprspush=False):	# find all the fixes since TTIME . Scan all the SKYL devices for new data

	curs=conn.cursor()              # set the cursor for storing the fixes
	cursG=conn.cursor()             # set the cursor for searching the devices
	url="https://skylines.aero/api/live" 
	skylpos={"skylpos":[]}		# init the dicta
	pos=skylgetapidata(url)	# get the JSON data from the Skylines server
	if prt:
		print json.dumps(pos, indent=4) # convert JSON to dictionary
	tracks=pos['tracks']
	cursG.execute("select id, Registration, active from TRKDEVICES where devicetype = 'SKYL' ; " ) 	# get all the devices with SKYL
        for rowg in cursG.fetchall(): 	# look for that registration on the OGN database
                                
        	pilotname=rowg[0]	# pilotname to report
        	gliderreg=rowg[1]	# Glider registration EC-???
        	active=rowg[2]		# if active or not
		if active == 0:
			continue	# if not active, just ignore it
					# build the userlist to call to the SKYL server
		found=skyladdpos(tracks, skylpos, ttime, pilotname, gliderreg)	# find the gliders since TTIME
	if prt:
		print skylpos
	if store:
		skylstoreitindb(skylpos, curs, conn)				# and store it on the DDBB
	if aprspush:
		skylaprspush(skylpos, conn, prt=prt)				# and push it into the OGN APRS
	now=datetime.utcnow()
	td=now-datetime(1970,1,1)       # number of second until beginning of the day of 1-1-1970
	sync=int(td.total_seconds())	# as an integer
	return (sync+1)			# return TTIME for next call

#-------------------------------------------------------------------------------------------------------------------#


