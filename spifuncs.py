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

def spigetapidata(url, data):                      # get the data from the API server

	username="acasado@acm.org"
	password="spider123"
        req = urllib2.Request(url, data)
	req.add_header("Content-Type","application/xml")
	req.add_header("Content-type", "application/x-www-form-urlencoded")
	req.add_header('Authorization', encodeUserData(username, password))
        r = urllib2.urlopen(req)                # open the url resource
	html=r.read()
        return(html)

def  spigetdataXML(ttime): 				# prepare the data POST request

	data='<?xml version="1.0" encoding="utf-8"?> <data xmlns="https://aff.gov/affSchema" sysId="Club de Planeadores de Vitacura" rptTime="'+ttime+'" version="2.23"> <msgRequest to="Spidertracks" from="Club de Planeadores de Vitacura" msgType="Data Request" subject="Async" dateTime="'+ttime+'"> <body>'+ttime+'</body> </msgRequest> </data>'
	return (data)


def spigetaircraftpos(html, spipos):			# return on a dictionary the position of all spidertracks
	doc = ET.fromstring(html)
	ttime=doc.attrib['rptTime']
	for child in doc:				# one level down
		for ch in child:			# second level down
			#print "TTT:", ch.tag, "AAA:", ch.attrib
			UnitID  =ch.attrib['UnitID']
			DateTime=ch.attrib['dateTime'] 
			ttime	=ch.attrib['dataCtrDateTime']
			print "T:", ttime
			dte=DateTime[2:4]+DateTime[5:7]+DateTime[8:10] 
			tme=DateTime[11:13]+DateTime[14:16]+DateTime[17:19] 
			pos={"UnitID" : UnitID}
			pos["date"]=dte
			pos["time"]=tme
			reg="CC-UFO"
			for chh in ch:			# therid level down
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
			distance=vincenty((lat, lon),(vitlat,vitlon)).km    # distance to the statio
			pos["dist"]=distance
			if pos['registration'] == 'HBEAT':
				print  "P: HBEAT"
			else:
				print "P:", pos
			spipos['spiderpos'].append(pos)
	return (ttime)

def spistoreitindb(data, curs, conn):
	for fix in data['spiderpos']:
		id=fix['registration'] 
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
		sensitivity=0
		gps=""
		uniqueid=fix["UnitID"]
		dist=fix['dist']
		extpos=""
		if id == "HBEAT":
			continue
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


def spifindspiderpos(ttime, conn):

	curs=conn.cursor()
	url="https://go.spidertracks.com/api/aff/feed" 
	spipos={"spiderpos":[]}
	data=spigetdataXML(ttime)
	html=spigetapidata(url,data)
	ttime=spigetaircraftpos(html, spipos)
	spistoreitindb(spipos, curs, conn)
	return (ttime)


