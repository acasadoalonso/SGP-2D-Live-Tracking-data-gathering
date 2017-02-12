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


def lt24login(LT24path, username, password): 	# login into livetrack24.com 

	global LT24qwe
	global LT24_appSecret
	global LT24_appKey
	global LT24login
	f=open(LT24path+"clientid")             # open the file with the client id
	client=f.read()                         # read it
	LT24_appKey=client.rstrip()             # clear the whitespace at the end
	f=open(LT24path+"secretkey")            # open the file with the secret key
	secretkey=f.read()                      # read it
	LT24_appSecret=secretkey.rstrip()       # clear the whitespace at the end
	LT24qwe=" "				# init the seed
	lt24req("op/ping")			# the first time always is in error but we get the first QWE
	replylogin = lt24req("op/6/username/"+username+"/pass/"+password) 
	LT24login = json.loads(replylogin)	# parse the JSON string
	print "LT24 login:", LT24login['userID'], LT24login['username']
	if LT24login["error"] == "":
		LT24login=True
		return (0)
	else:
		return (-1)


#-------------------------------------------------------------------------------------------------------------------#
def lt24unpackDelta(deltaStr):			# unpack the deltta string formated
    	deltaStr=deltaStr.replace( "-" , ",-")	# LT24 defined
    	deltaArray = deltaStr.split(",")	# break it on indivual list
	if deltaArray[0] == ' ' or  deltaArray[0] == '' :
		deltaArray[0] = 0.0
	else:
		deltaArray[0]=float(deltaArray[0])# convert from unicode to int
    	for i in range(len(deltaArray)):	# unpack the lists
       		 if i > 0:
				#print ">>", deltaArray[i], "||", deltaArray [i-1],"<<"
				if deltaArray[i-1] == ' ' or deltaArray[i-1] == '':
					delta=0.0
				else:
					delta=float(deltaArray[ i - 1 ])

				deltaArray[i] = float(deltaArray[i] ) + delta
    	return deltaArray

#-------------------------------------------------------------------------------------------------------------------#
def lt24otpReply(question):			# set the LT24 AK & VC
	global LT24_appSecret
	global LT24_appKey
        signature = hmac.new(LT24_appSecret, msg=question, digestmod=hashlib.sha256).hexdigest()
        #print signature
        vc=signature[0:16]
        #print vc
        return "/ak/" + LT24_appKey + "/vc/" + vc

#-------------------------------------------------------------------------------------------------------------------#
def lt24req(cmd):				# get the rsponse from the LT24 server
        global LT24qwe
        lt24req="http://api.livetrack24.com/api/v2/"	# the initial part of the URL
        reply=lt24otpReply(LT24qwe)		# build the AK & VK
        lt24url=lt24req+cmd+reply		# build the complete URL
        f=urllib2.urlopen(lt24url)		# call the server
        response = f.read()			# read the data
        qwepos= response.find("qwe")		# find where is the key for next request
        LT24qwe=response[qwepos+6:qwepos+22]	# build the seed for next request
        return (response)
#-------------------------------------------------------------------------------------------------------------------#
def lt24getapidata(url, auth):                  # get the data from the API server
	req = urllib2.Request(url)                      
	req.add_header('Authorization', auth)   # build the authorization header
	req.add_header("Accept","application/json")
	req.add_header("Content-Type","application/hal+json")
	r = urllib2.urlopen(req)                # open the url resource
	j_obj = json.load(r)                    # convert to JSON
	return j_obj                            # return the JSON object
#-------------------------------------------------------------------------------------------------------------------#



def lt24storeitindb(datafix, curs, conn):	# store the fix into the database
	for fix in datafix['lt24pos']:		# for each fix on the dict
		id=fix['registration'][0:16]	# extract the information
		dte=fix['date'] 
		hora=fix['time'] 
		station="LT24"
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
		addcmd="insert into SPIDERSPOTDATA values ('" +id+ "','" + dte+ "','" + hora+ "','" + station+ "'," + str(latitude)+ "," + str(longitude)+ "," + str(altim)+ "," + str(speed)+ "," + \
               str(course)+ "," + str(roclimb)+ "," +str(rot) + "," +str(sensitivity) + \
               ",'" + gps+ "','" + uniqueid+ "'," + str(dist)+ ",'" + extpos+ "') ON DUPLICATE KEY UPDATE extpos = '!ZZZ!' "
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

def lt24findpos(ttime, conn, once):	# find all the fixes since TTIME . Scan all the LT24 devices for new data

	curs=conn.cursor()              # set the cursor for storing the fixes
	cursG=conn.cursor()             # set the cursor for searching the devices
	userList=''
	lt24pos={"lt24pos":[]}	# init the dicta
	cursG.execute("select id, Registration, active from TRKDEVICES where devicetype = 'LT24' ; " ) 	# get all the devices with LT24
        for rowg in cursG.fetchall(): 	# look for that registration on the OGN database
                                
        	reg=rowg[0]		# registration to report
        	deviceID=rowg[1]	# Glider registration EC-???
        	active=rowg[2]		# if active or not
		if active == 0:
			continue	# if not active, just ignore it
					# build the userlist to call to the LT24 server
		userList += reg		# build the user list
		userList += ","		# separated by comas

	userList=userList.rstrip(',')	# clear the last comma
					# request for the time being, just the last position of the glider
	req="op/2//detailLevel/-1/userList/"+userList	# the URL request to LT24
	jsondata=lt24req(req)		# get the JSON data from the lt24 server
	pos=json.loads(jsondata)	# convert JSON to dictionary
	#print json.dumps(pos, indent=4) # convert JSON to dictionary
	result=pos["result"]		# get the result part
	k= result.keys()		# get the key or track id
	jsondata = result[str(k[0])] 	# only the first track
	if once:			# only the very first time
		ts=lt24addpos(jsondata, lt24pos, ttime, userList)	# find the gliders since TTIME
	sync=lt24gettrackpoints(lt24pos, ttime, userList)		# get now all the fixes/tracks
	lt24storeitindb(lt24pos, curs, conn)				# and store it on the DDBB
	
	if sync == 0:			# just in case of not tracks at all, built the current time
		now=datetime.utcnow()
		td=now-datetime(1970,1,1)       # number of second until beginning of the day of 1-1-1970
		sync=int(td.total_seconds())	# as an integer
	return (sync+1)			# return TTIME for next call

#-------------------------------------------------------------------------------------------------------------------#
def lt24addpos(msg, lt24pos, ttime, regis):	# extract the data of the last know position from the JSON object

	unixtime=msg["lastPointTM"] 		# the time from the epoch
	if (unixtime < ttime):
		return (ttime)			# if is lower than the last time just ignore it
	reg=regis
	lat=msg["lat"] 				# extract from the JSON object the data that we need
	lon=msg["lon"] 
	alt=msg["alt"] 
	id =msg["userID"] 
	dte=msg["lastTM"] 
	wdir=msg["windDir"]
	wspd=msg["windSpeed"]
	gps="NO"
	extpos="NO"
	roc=0
	date=dte[8:10]+dte[3:5]+dte[0:2]
        time=dte[11:13]+dte[14:16]+dte[17:19]
	
	vitlat   =config.FLOGGER_LATITUDE
	vitlon   =config.FLOGGER_LONGITUDE
	distance=vincenty((lat, lon),(vitlat,vitlon)).km    # distance to the statio
	pos={"registration": regis, "date": date, "time":time, "Lat":lat, "Long": lon, "altitude": alt, "UnitID":id, "dist":distance, "course":wdir, "speed": wspd, "roc":roc, "GPS":gps , "extpos":extpos}
	lt24pos['lt24pos'].append(pos)		# and store it on the dict
	print "LT24POS1:", round(lat,4), round(lon,4), alt, id, round(distance,4), unixtime, dte, date, time, regis
	#print "POS:", pos			# print it as a control
	return (unixtime)			# indicate that we added an entry to the dict


#-------------------------------------------------------------------------------------------------------------------#

def lt24gettrackpoints(lt24pos, since, userid):	# get all the fixes/tracks of a userlist

						# request that to LT24
	replytest = lt24req("/op/getTrackPoints/userList/"+userid+"/fromTM/"+str(since))
	pos = json.loads(replytest)		# parse the JSON string
	#print json.dumps(pos, indent=4) 	# convert JSON to dictionary
	sync=pos["sync"]			# get the sync point for next request
	tracks=pos["tracks"]			# get all the tracks/fixes
	if len(tracks) > 0:			# do we have tracks ???
		trk=tracks.keys()		# get the key or track id
	else:
		return (int(since))		# nothing found
		
	for trackid in trk:			# inspect eack track

		data=tracks[str(trackid)]	# get the data for this track
		trackFields = data.split(":")	# divide it on the different items

		username = trackFields[0]	# the first is the user name
		userID = trackFields[1]		# the second the userID associated to that user name
		TMs  = lt24unpackDelta( trackFields[2] )	# timestamps
		Lats = lt24unpackDelta( trackFields[3] )	# Latitudes
		Lons = lt24unpackDelta( trackFields[4] )	# longitudes
		Alts = lt24unpackDelta( trackFields[5] )	# altitudes
		SOGs = lt24unpackDelta( trackFields[6] )	# Speed
		COGs = lt24unpackDelta( trackFields[7] )	# courses
		AGLs = lt24unpackDelta( trackFields[8] )	# altitude above the ground
		VROs = lt24unpackDelta( trackFields[9] )	# vertical speed / rate of climb
		if len(Lats) != len(Lons) and Lons[0] == 0.0:	# works ourund a bug
			Lons.pop(0)
		for i in range (len(Lats) -1):			# adjust accoring to the formula
    			Lats[i] = Lats[i] / 60000
    			Lons[i] = Lons[i] / 60000
    			VROs[i] = VROs[i] / 100
    			COGs[i] = COGs[i] * 2

		#print ":::", username, "UserID", userID, "\nTM",TMs, "\nlat",Lats, "\nlon", Lons, "\nAlt", Alts, "\nSOG", SOGs, "\nCOG", COGs, "\nAgl", AGLs, "\nVRO", VROs
		for i in range(len(Lats) -1):	# handle the unpacked data of each track
			lon      =Lons[i]
			lat      =Lats[i]
			alt      =Alts[i]
			course   =COGs[i]
			speed    =SOGs[i]
			if i <= len(VROs):
				roc = int(VROs[i])
			else:
				roc = 0
			extpos   =str(AGLs[i])	# we repoort the AGL omn the exppos of the DDBB
			vitlat   =config.FLOGGER_LATITUDE
        		vitlon   =config.FLOGGER_LONGITUDE
        		distance=vincenty((lat, lon),(vitlat,vitlon)).km    # distance to the central location
			dte=datetime.utcfromtimestamp(TMs[i])	# get the data/time for the timestamp
			date=dte.strftime("%y%m%d")		# date format
			time=dte.strftime("%H%M%S")		# time format
			gps="GPS"
			if TMs[i] < since:			# if the timestamp is earlier than the since param
				print "Nothing to do... SINCE=", since, "Time fix:", TMs[i], "SYNC", sync
			else:
	
				pos={"registration": username, "date": date, "time":time, "Lat":lat, "Long": lon, "altitude": alt, "UnitID":userID, "dist":distance, "course": course, "speed": speed, "roc":roc, "GPS":gps , "extpos":extpos}
			#print "POS:", pos
        		lt24pos['lt24pos'].append(pos)          # and store it on the dict
			print "LT24POS2:", round(lat,4), round(lon,4), alt, userID,  round(distance,4), dte, date, time, username, trackid

	return (int(sync))		# return the SYNC for next call


