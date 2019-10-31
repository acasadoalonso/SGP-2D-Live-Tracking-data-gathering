#!/bin/python3
import urllib.request, urllib.error, urllib.parse
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
import base64
from geopy.distance import vincenty         # use the Vincenty algorithm
import MySQLdb                              # the SQL data base routines
# ---------------- #
import config
from flarmfuncs  import *
from ognddbfuncs import *
from parserfuncs import deg2dmslat, deg2dmslon

# ---------------- #

# simple wrapper function to encode the username & pass


def encodeUserData(user, password):
    uplusp = (user + ':' + password).encode('UTF-8')
    ud = "Basic " + base64.b64encode(uplusp).decode('UTF-8')
    return ud


def spigetapidata(url, data, username, password): 	# get the data from the API server

    req = urllib.request.Request(url, data.encode(encoding='utf-8')) # build the req

    req.add_header("Content-Type", "application/xml")
    req.add_header("Content-type", "application/x-www-form-urlencoded")
    req.add_header('Authorization', encodeUserData(username, password))
    r = urllib.request.urlopen(req)         # open the url resource
    html = r.read()			    # read the data received
    return(html)			    # return the data received


def spigetdataXML(ttime, SYSid): 	    # prepare the data POST request

    data = '<?xml version="1.0" encoding="utf-8"?> <data xmlns="https://aff.gov/affSchema" sysId="'+SYSid+'" rptTime="'+ttime + \
        '" version="2.23"> <msgRequest to="Spidertracks" from="'+SYSid + \
        '" msgType="Data Request" subject="Async" dateTime="' + \
        ttime+'"> <body>'+ttime+'</body> </msgRequest> </data>'
    return (data)			    # return data on XML format


# return on a dictionary the position of all spidertracks
def spigetaircraftpos(html, spipos):
    doc = ET.fromstring(html)		    # parse the html data into a XML tree
    ttime = doc.attrib['rptTime']
    for child in doc:			    # one level down
        for ch in child:		    # second level down
            #print "TTT:", ch.tag, "AAA:", ch.attrib
            UnitID = ch.attrib['UnitID']
            DateTime = ch.attrib['dateTime']
            # store the ttime for next request
            ttime = ch.attrib['dataCtrDateTime']
            source = ch.attrib['source']    # store the source
            fix = ch.attrib['fix']          # store the fix
            hdop = ch.attrib['HDOP']        # store the hdop
            #print "T:", ttime
            dte = DateTime[2:4]+DateTime[5:7]+DateTime[8:10] 		# get the date
            tme = DateTime[11:13]+DateTime[14:16] + \
                DateTime[17:19] 	    # and the time
            pos = {"UnitID": UnitID}	    # save the unitID as a check
            pos["GPS"] = source             # store the Source GPS
                                            # store the GPS accuracy on the sensitivity
            pos["sensitivity"] = hdop
            pos["extpos"] = fix             # store 3D/2D on the extended position
            pos["date"] = dte
            pos["time"] = tme
            reg = "CC-UFO"		    # by defualt
            for chh in ch:		    # third level down
                #print "TTTT:", chh.tag, "AAAA:", chh.attrib, "X:",chh.text
                name = chh.tag
                p = name.find('}')
                nm = name[p+1:]
                if nm == "telemetry":
                    if chh.attrib['name'] == "registration":
                        reg = chh.attrib['value']
                        pos['registration'] = reg
                else:
                    pos[nm] = chh.text
            lat = pos["Lat"]
            lon = pos["Long"]
            vitlat = config.FLOGGER_LATITUDE
            vitlon = config.FLOGGER_LONGITUDE
                                            # distance to the station VITACURA
            distance = vincenty((lat, lon), (vitlat, vitlon)).km
            pos["dist"] = distance
            if pos['registration'] == 'HBEAT':
                print("SPIDPOS : HBEAT", ttime)
            else:
                print("SPIDPOS :", pos, ttime)
                                            # append the position infomatio to the dict
            spipos['spiderpos'].append(pos)
    return (ttime)			    # return the ttime as a reference for next request


# function to build the spider table of relation between flramid and registrations
def spibuildtable(conn, spidtable, prt=False):

    cursG = conn.cursor()                   # set the cursor for searching the devices
                                            # get all the devices with SPIDER
    cursG.execute( "select id, flarmid, registration from TRKDEVICES where devicetype = 'SPID' and active = 1; ")
    for rowg in cursG.fetchall(): 	    # look for that registration on the OGN database

        ident = rowg[0]		            # registration to report
        flarmid = rowg[1]		    # Flarm id to be linked
        registration = rowg[2]              # registration id to be linked
        if flarmid == None or flarmid == '': # if flarmid is not provided
                                            # get it from the registration
            flarmid = getflarmid(conn, registration)
        else:
            chkflarmid(flarmid)
        if flarmid == "NOREG":              # in case of no registration on the DDBa
            flarmid=getognflarmid(registration)

        spidtable[ident] = flarmid          # substitute the id by the Flarmid
    if prt:
        print("SPIDtable:", spidtable)
    return(spidtable)


# store the spider position into the database
def spistoreitindb(data, curs, conn, prt=False):

    spidtable = {}
                                            # build the table of registration and flarmid
    spibuildtable(conn, spidtable, prt)
    for fix in data['spiderpos']:	    # for each position that we have on the dict
                                            # extract the information to store on the DDBB
        ident = fix['registration']
        if len(ident) > 9:
            ident = ident[0:9]
        if ident == "HBEAT":		    # if it is the heartbeat just ignore it
            continue
        dte = fix['date']
        hora = fix['time']
        station = config.location_name
        latitude = fix['Lat']
        longitude = fix['Long']
        altim = fix['altitude']
        speed = fix['speed']
        course = fix['heading']
        roclimb = 0
        rot = 0
                                            # store the GPS accuracy on the sensitivity
        sensitivity = fix['sensitivity']
        gps = fix['GPS']
        uniqueid = fix["UnitID"]
        dist = fix['dist']
        extpos = fix['extpos']		    # store 3D/2D on the extended position
        if ident in spidtable:		    # if ID is on the table substitude the spiderid by the flarmID
            reg = spidtable[ident]
        else:
            reg = "XX-"+ident		    # if not ... just add the registration prefix
        addcmd = "insert into OGNDATA values ('" + reg + "','" + dte + "','" + hora + "','" + station + "'," + str(latitude) + "," + str(longitude) + "," + str(altim) + "," + str(speed) + "," + \
            str(course) + "," + str(roclimb) + "," + str(rot) + "," + str(sensitivity) + \
            ",'" + gps + "','" + uniqueid + "'," + \
            str(dist) + ",'" + extpos + "' , 'SPID') "
        try:
            curs.execute(addcmd)            # store it on the DDBB
        except MySQLdb.Error as e:
            try:
                print(">>>MySQL Error [%d]: %s" % (e.args[0], e.args[1]))
            except IndexError:
                print(">>>MySQL Error: %s" % str(e))
                print(">>>MySQL error:", cout, addcmd)
                print(">>>MySQL data :",  data)
            return (False)                  # report the error
    conn.commit()                           # commit the DB updates
    return(True)			    # report success


def spiaprspush(data, conn, prt=False):

    spidtable = {}
                                            # build the table of registration and flarmid
    spibuildtable(conn, spidtable, prt)
    for fix in data['spiderpos']:	    # for each position that we have on the dict
                                            # extract the information to store on the DDBB
        ident = fix['registration']
        if len(ident) > 9:
            ident = ident[0:9]
        if ident == "HBEAT":		    # if it is the heartbeat just ignore it
            continue
        dte = fix['date']
        hora = fix['time']
        station = config.location_name
        latitude = float(fix['Lat'])        # convert to float
        longitude = float(fix['Long'])
        altitude = int(fix['altitude'])
        speed = int(fix['speed'])
        course = int(fix['heading'])
        roclimb = 0
        rot = 0
                                            # store the GPS accuracy on the sensitivity
        sensitivity = fix['sensitivity']
        gps = fix['GPS']		    # if GPS is OK or not
        uniqueid = fix["UnitID"]	    # internal ID
        dist = fix['dist']		    # dist not used
        extpos = fix['extpos']		    # store 3D/2D on the extended position
        if ident in spidtable:		    # if ID is on the table substitude the spiderid by the flramid
            reg = spidtable[ident]
        else:
            reg = "SPI"+ident		    # if not ... just add the registration prefix
                                            # build the APRS message
                                            # conver the latitude to the format required by APRS
        lat = deg2dmslat(abs(latitude))
        if latitude > 0:
            lat += 'N'
        else:
            lat += 'S'
        lon = deg2dmslon(abs(longitude))
        if longitude > 0:
            lon += 'E'
        else:
            lon += 'W'

        ccc = "%03d" % int(course)
        sss = "%03d" % int(speed)

        aprsmsg = reg+">OGSPID,qAS,SPIDER:/"+hora+'h'+lat+"/"+lon+"'"+ccc+"/"+sss+"/"

        if altitude > 0:
            aprsmsg += "A=%06d" % int(altitude*3.28084)
        aprsmsg += " id"+uniqueid+" +"+sensitivity+"dB "+id+" "+extpos + "\n"
        rtn = config.SOCK_FILE.write(aprsmsg)
        print("APRSMSG : ", aprsmsg)

    return(True)


# find all the fixes since last time
def spifindspiderpos(ttime, conn, username, password, SYSid, prt=False, store=True, aprspush=False):

    curs = conn.cursor()		# gen the cursor
    url = "https://go.spidertracks.com/api/aff/feed" 	# the URL for the SPIDER server
    spipos = {"spiderpos": []}		# init the dict
                                        # get the data for the POST request passing the TTIME
    data = spigetdataXML(ttime, SYSid)
                                        # get the data on HTML format
    html = spigetapidata(url, data, username, password)
                                        # extract the aircraft position from the XML data
    ttime = spigetaircraftpos(html, spipos)
    if prt:
        print(spipos)		        # print the raw data
    if store and len(spipos) > 1:
        spistoreitindb(spipos, curs, conn, prt)  # store the fixes on the DDBB
    if aprspush and len(spipos) > 1:
        spiaprspush(spipos, conn, prt)	# push the fixes to the OGN APRS
    return (ttime)			# return the TTIME for the next request
