#!/bin/python
import urllib2
import json
import xml.etree.ElementTree as ET
from ctypes import *
import socket
from datetime import *
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
from parserfuncs import deg2dmslat, deg2dmslon


def inreachgetapidata(url, prt=False):                      	# get the data from the API server

        #req = urllib2.Request(url)		# buil the request
        req = urllib2.Request(url, headers={'User-Agent' : "Magic Browser"})
	req.add_header("Content-Type","application/kml")
	req.add_header("Content-type", "application/x-www-form-urlencoded")
        try:
            r = urllib2.urlopen(req)            # open the url resource
        except urllib2.HTTPError, e:
            print e.fp.read()
        kml= r.read()    
	if prt:
		print "doc"
        return kml


def inreachaddpos(msg, inreachpos, ttime, regis, flarmid):	# extract the data from the JSON object

        # print msg                               # print the input
	timeutc=msg["Time UTC"] 		# the time from the epoch
        if timeutc[1] == '/':
            mm='0'+timeutc[0:1]
            if timeutc[3] == '/':
                dd='0'+timeutc[2]
                yy=timeutc[6:8]
                i=8
            else:
                dd=timeutc[2:4]
                yy=timeutc[7:9]
                i=9
        else:
            mm=timeutc[0:2]
            if timeutc[5] == '/':
                dd='0'+timeutc[3]
                yy=timeutc[9:9]
                i=9
            else:
                dd=timeutc[3:5]
                yy=timeutc[8:10]
                i=10
        date=yy+mm+dd
        timett=datetime.strptime(timeutc[i+1:],"%I:%M:%S %p") # convert to datettime
        yyy=int(yy)+2000
        mmm=int(mm)
        ddd=int(dd)
        hhh=timett.hour
        min=timett.minute
        sss=timett.second
        tt=  datetime(yyy, mmm, ddd, hhh, min, sss)
        td=tt-datetime(1970,1,1)       # number of second until beginning of the day of 1-1-1970
        unixtime=int(td.total_seconds())      # as an integer

        #print "TT", date, tt, unixtime
	alt=msg["Elevation"] 
        altidx=alt.find(' ')
        altitude=alt[0:altidx]
	if (unixtime < ttime or altitude == 0):
		return (False)			# if is lower than the last time just ignore it
	reg=regis
	lat=msg["Latitude"] 			# extract from the JSON object the data that we need
	lon=msg["Longitude"] 
	id =msg["IMEI"] 			# identifier for the final user
	mid=msg["Device Type"] 			# inreach model number
        sspeed=msg["Velocity"]                  # speed
        spdidx=sspeed.find(" ")
        speed=sspeed[0:spdidx]
        ccourse=msg["Course"]
        couidx=ccourse.find(" ")
        course=ccourse[0:couidx]
	extpos=msg["Valid GPS Fix"] 		# battery state 
	dte=tt.isoformat()
	date=dte[2:4]+dte[5:7]+dte[8:10]
        time=dte[11:13]+dte[14:16]+dte[17:19]
	vitlat   =config.FLOGGER_LATITUDE
	vitlon   =config.FLOGGER_LONGITUDE
	distance=vincenty((lat, lon),(vitlat,vitlon)).km    # distance to the statioan
        pos={"registration": flarmid, "date": date, "time":time, "Lat":lat, "Long": lon, "altitude": altitude, "UnitID":id, "GPS":mid, "speed":speed, "course":course, "dist":distance, "extpos":extpos}
	inreachpos['inreachpos'].append(pos)		# and store it on the dict
	print "INREACHPOS :", lat, lon, altitude, id, distance, unixtime, dte, date, time, reg, flarmid, extpos
	return (True)				# indicate that we added an entry to the dict

def inreachgetaircraftpos(kml, inreachpos, ttime, regis, flarmid, prt=True):	# return on a dictionary the position of all spidertracks
        msg={}                                  # create the local object
        doc = ET.fromstring(kml)		# parse the html data into a XML tree   
        for child in doc:
            #print "L1", child.tag, child.attrib
            for ch in child:
                #print "L2", ch.tag, ch.attrib
                if ch.tag == "{http://www.opengis.net/kml/2.2}Folder":
                    for c in ch:
                        #print "L3", c.tag, c.attrib
                        for cc in c:
                            #print "L4", cc.tag, cc.attrib
                            if cc.tag == "{http://www.opengis.net/kml/2.2}ExtendedData" :
                                for ccc in cc:
                                   #print "L5", ccc.tag, ccc.attrib
                                   for cccc in ccc:
                                        item=  ccc.attrib["name"]
                                        value= ccc.find('{http://www.opengis.net/kml/2.2}value').text
                                        msg[item]=value
                                        if prt:
                                            print "InreachPos", item, "==>", value

        found=inreachaddpos(msg, inreachpos, ttime, regis, flarmid)   # add the position for this fix
        #print inreachpos
	return (True)			# return if we found a message or not

def inreachstoreitindb(datafix, curs, conn):	# store the fix into the database
	for fix in datafix['inreachpos']:		# for each fix on the dict
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
		course=fix['course']
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
               ",'" + gps+ "','" + uniqueid+ "'," + str(dist)+ ",'" + extpos+ "', 'INRE' ) "
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

def inreachaprspush(datafix, prt=False):	# push the data into the OGN APRS
	for fix in datafix['inreachpos']:	# for each fix on the dict
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
		gps=fix['GPS']			# model ID
		uniqueid=str(fix["UnitID"])	# identifier of the owner
		dist=fix['dist']		# distance to BASE
		extpos=fix['extpos']		# battery state
						# build the APRS message
		lat=deg2dmslat(abs(latitude))	# convert the latitude to the format required by APRS
		if latitude > 0:
			lat += 'N'
		else:
			lat += 'S'
		lon=deg2dmslon(abs(longitude))	# convert longitude to the DDMM.MM format
		if longitude > 0:
			lon += 'E'
		else:
			lon += 'W'
		
		aprsmsg=id+">OGINREACH,qAS,INREACH:/"+hora+'h'+lat+"/"+lon+"'000/000/"
		if altitude > 0:
			aprsmsg += "A=%06d"%int(altitude*3.28084)
		aprsmsg += " id"+uniqueid+" "+gps+" "+extpos+" \n"
		rtn = config.SOCK_FILE.write(aprsmsg) 
		print "APRSMSG : ", aprsmsg
	return(True)

def inreachfindpos(ttime, conn, prt=False, store=True, aprspush=False):	# find all the fixes since TTIME

	foundone=False			# asume no found
	curs=conn.cursor()              # set the cursor for storing the fixes
	cursG=conn.cursor()             # set the cursor for searching the devices
	cursG.execute("select id, spotid as inreachid, spotpasswd as inreachpasswd, active, flarmid, registration from TRKDEVICES where devicetype = 'INRE'; " ) 	# get all the devices with INRE
        for rowg in cursG.fetchall(): 	# look for that registration on the OGN database
                                
        	reg=rowg[0]		# registration to report
        	inreachID=rowg[1]	# INREach
        	inreachpasswd=rowg[2]	# InReach password
        	active=rowg[3]		# if active or not
        	flarmid=rowg[4]		# Flamd id to be linked
        	registration=rowg[5]	# registration id to be linked
		if active == 0:
			continue	# if not active, just ignore it
		if flarmid == None or flarmid == '': 		# if flarmid is not provided 
			flarmid=getflarmid(conn, registration)	# get it from the registration
		else:
			chkflarmid(flarmid)

					# build the URL to call to the InReach server
		if inreachpasswd == '' or inreachpasswd == None:
                        url="http://inreach.garmin.com/feed/share/"+inreachID
		else:
                        url="https://inreach.garmin.com/feed/share/"+inreachID+"?d1="+time
			url="https://api.findmespot.com/spot-main-web/consumer/rest-api/2.0/public/feed/"+inreachID+"/message.json?feedPassword="+str(inreachpasswd)
		if prt:
			print url
		inreachpos={"inreachpos":[]}			# init the dict
		kml=inreachgetapidata(url)			# get the JSON data from the InReach server
		if prt:						# if we require printing the raw data
			print "KML ===>", kml
		found=inreachgetaircraftpos(kml, inreachpos, ttime, reg, flarmid, prt=prt)	# find the gliders since TTIME
		if found:
			foundone=True
		if prt:
			print inreachpos
		if store:
			inreachstoreitindb(inreachpos, curs, conn)	# and store it on the DDBB
		if aprspush:
			inreachaprspush(inreachpos, prt)		# and push the data into the APRS
	
	if foundone:
		now=datetime.utcnow()
		td=now-datetime(1970,1,1)       # number of second until beginning of the day of 1-1-1970
		ts=int(td.total_seconds())	# as an integer
		return (ts)			# return TTIME for next call
	else:
		return (ttime)			# keep old value

#-------------------------------------------------------------------------------------------------------------------#


