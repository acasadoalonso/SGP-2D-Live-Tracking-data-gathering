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

def spigetapidata(url, data, username, password): 	# get the data from the API server

        req = urllib2.Request(url, data)	# build the req

	req.add_header("Content-Type","application/xml")
	req.add_header("Content-type", "application/x-www-form-urlencoded")
	req.add_header('Authorization', encodeUserData(username, password))
        r = urllib2.urlopen(req)                # open the url resource
	html=r.read()				# read the data received
        return(html)				# return the data received

def  spigetdataXML(ttime): 			# prepare the data POST request

	data='<?xml version="1.0" encoding="utf-8"?> <data xmlns="https://aff.gov/affSchema" sysId="Club de Planeadores de Vitacura" rptTime="'+ttime+'" version="2.23"> <msgRequest to="Spidertracks" from="Club de Planeadores de Vitacura" msgType="Data Request" subject="Async" dateTime="'+ttime+'"> <body>'+ttime+'</body> </msgRequest> </data>'
	return (data)


def spigetaircraftpos(html, spipos):		# return on a dictionary the position of all spidertracks
	doc = ET.fromstring(html)		# parse the html data into a XML tree
	ttime=doc.attrib['rptTime']
	for child in doc:			# one level down
		for ch in child:		# second level down
			#print "TTT:", ch.tag, "AAA:", ch.attrib
			UnitID  =ch.attrib['UnitID']
			DateTime=ch.attrib['dateTime'] 
			ttime	=ch.attrib['dataCtrDateTime']	# store the ttime for next request
			source	=ch.attrib['source']	# store the source 
			fix	=ch.attrib['fix']	# store the fix 
			hdop	=ch.attrib['HDOP']	# store the hdop 
			#print "T:", ttime
			dte=DateTime[2:4]+DateTime[5:7]+DateTime[8:10] 		# get the date
			tme=DateTime[11:13]+DateTime[14:16]+DateTime[17:19] 	# and the time
			pos={"UnitID" : UnitID}					# save the unitID as a check
			pos["GPS"]         = source	# store the Source GPS 
			pos["sensitivity"] = hdop	# store the GPS accuracy on the sensitivity		
			pos["extpos"]      = fix	# store 3D/2D on the extended position
			pos["date"]        = dte
			pos["time"]        = tme
			reg="CC-UFO"		# by defualt
			for chh in ch:		# third level down
				#print "TTTT:", chh.tag, "AAAA:", chh.attrib, "X:",chh.text
				name=chh.tag
				p=name.find('}')
				nm=name[p+1:]
				if nm=="telemetry":
					if chh.attrib['name'] == "registration":
						reg=chh.attrib['value']
						pos['registration']=reg
				else:
					pos[nm]=chh.text
			lat=pos["Lat"] 
			lon=pos["Long"] 
			vitlat   =config.FLOGGER_LATITUDE
			vitlon   =config.FLOGGER_LONGITUDE
			distance=vincenty((lat, lon),(vitlat,vitlon)).km    	# distance to the station VITACURA
			pos["dist"]=distance
			if pos['registration'] == 'HBEAT':
				print "SPIDPOS : HBEAT", ttime
			else:
				print "SPIDPOS :", pos, ttime
			spipos['spiderpos'].append(pos) 			# append the position infomatio to the dict
	return (ttime)								# return the ttime as a reference for next request

def spistoreitindb(data, curs, conn):		# store the spider position into the database
	for fix in data['spiderpos']:		# for each position that we have on the dict
		id=fix['registration'] 		# extract the information to store on the DDBB
		dte=fix['date'] 
		hora=fix['time'] 
		station="SPIDER"
		latitude=fix['Lat'] 
		longitude=fix['Long'] 
		altim=fix['altitude'] 
		speed=fix['speed'] 
		course=fix['heading'] 
		roclimb=0
		rot=0
		sensitivity=fix['sensitivity']
		gps=fix['GPS']
		uniqueid=fix["UnitID"]
		dist=fix['dist']
		extpos=fix['extpos']
		if id == "HBEAT":		# if it is the heartbeat just ignore it
			continue
		addcmd="insert into SPIDERSPOTDATA values ('" +id+ "','" + dte+ "','" + hora+ "','" + station+ "'," + str(latitude)+ "," + str(longitude)+ "," + str(altim)+ "," + str(speed)+ "," + \
               str(course)+ "," + str(roclimb)+ "," +str(rot) + "," +str(sensitivity) + \
               ",'" + gps+ "','" + uniqueid+ "'," + str(dist)+ ",'" + extpos+ "') ON DUPLICATE KEY UPDATE extpos = '!ZZZ!' "
        	try:
              		curs.execute(addcmd)	# store it on the DDBB
        	except MySQLdb.Error, e:
              		try:
                     		print ">>>MySQL Error [%d]: %s" % (e.args[0], e.args[1])
              		except IndexError:
                     		print ">>>MySQL Error: %s" % str(e)
                     		print ">>>MySQL error:", cout, addcmd
                    		print ">>>MySQL data :",  data
			return (False)	# report the error
        conn.commit()                   # commit the DB updates
	return(True)			# report success


def spifindspiderpos(ttime, conn, username, password):	# find all the fixes since last time

	curs=conn.cursor()		# gen the cursor
	url="https://go.spidertracks.com/api/aff/feed" 	# the URL for the SPIDER server
	spipos={"spiderpos":[]}		# init the dict
	data=spigetdataXML(ttime)	# get the data for the POST request passing the TTIME
	html=spigetapidata(url,data, username, password) # get the data on HTML format
	ttime=spigetaircraftpos(html, spipos)	# extract the aircraft position from the XML data
	spistoreitindb(spipos, curs, conn)	# store the fixes on the DDBB
	return (ttime)			# return the TTIME for the next request


