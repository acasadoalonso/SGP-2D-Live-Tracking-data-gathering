#!/usr/bin/python3
import urllib.request, urllib.error, urllib.parse
import json
from ctypes import *
from datetime import datetime, timedelta
import socket
import time
import string
import sys
import os
import signal
from geopy.distance import geodesic       # use the Vincenty algorithm^M
import MySQLdb                            # the SQL data base routines^M
import config
from flarmfuncs import *
from parserfuncs import deg2dmslat, deg2dmslon


# get the data from the API server
def captgetapidata(url, prt=False):

    req = urllib.request.Request(url)	# build the request
    req.add_header("Content-Type", "application/json")
    req.add_header("Content-type", "application/x-www-form-urlencoded")
    r = urllib.request.urlopen(req)     # open the url resource
    js=r.read().decode('UTF-8')
    j_obj = json.loads(js)                  # convert to JSON

    if prt:
        print(json.dumps(j_obj, indent=4))
    return j_obj                        # return the JSON object


def captaddpos(msg, captpos, ttime, captID, flarmid):  # extract the data from the JSON object

    unixtime = msg["timestamp"] 	# the time from the epoch
    type = msg["type"] 			# the time from the epoch
    if (unixtime < ttime or type != 1): # it should not be needed as we request from/ttime on the URL
        print("CAPTURS TTT>>>", ttime, unixtime, msg["date"], "Type:", type)
        return (False)			# if is lower than the last time just ignore it
    # extract from the JSON object the data that we need
    lat = msg["latitude"]
    lon = msg["longitude"]
    alt = msg["altitude"]		# low accuracy altitude
    device = msg["device"]		# the CAPTURS device ID
    speed = msg["speed"]		# low accuracy speed
    dte = msg["date"]			# date on format: :"Wed Jan 25 2017 22:52:41 GMT"
    # get the time from the timestamp
    tme = datetime.utcfromtimestamp(unixtime)
    date = tme.strftime("%y%m%d")	# the date
    time = tme.strftime("%H%M%S")	# the time
    vitlat = config.FLOGGER_LATITUDE    # the lat/long of the base station
    vitlon = config.FLOGGER_LONGITUDE
    distance = geodesic((lat, lon), (vitlat, vitlon)).km    # distance to the station
    pos = {"registration": flarmid, "date": date, "time": time, "Lat": lat,
           "Long": lon, "altitude": alt, "speed": speed, "dist": distance, "device": captID}
    captpos['captpos'].append(pos)	# and store it on the dict
    print("CAPTPOS :", lat, lon, alt, device, distance, unixtime, dte, captID, flarmid)
    return (True)			# indicate that we added an entry to the dict


# return on a dictionary the position of all captures devices
def captgetaircraftpos(data, captpos, ttime, captID, flarmid, prt=False):

    foundone = False			# assume that we are not going to find one
    msgcount = data['result']		# get the count of messages
    if msgcount == 0:			# check if we found some messages
        return (False)			# nothing to do
    messages = data['position']		# get the multiple messages
    #print "M:", message
    for msg in messages:		# if not iterate the set of messages
        if prt:
            print(json.dumps(msg, indent=4))        # convert JSON to dictionary
        # get the individual entries
        found = captaddpos(msg, captpos, ttime, captID, flarmid)
        if found:
            foundone = True		# found at least one
    return (foundone)			# return if we found a message or not


def captstoreitindb(datafix, curs, conn):  # store the fix into the database

    for fix in datafix['captpos']:	# for each fix on the dict
        id = fix['registration'] 	# extract the information
        if len(id) > 9:
            id = id[0:9]
        dte = fix['date']
        hora = fix['time']
        station = config.location_name
        latitude = fix['Lat']
        longitude = fix['Long']
        altim = fix['altitude']
        speed = fix['speed']
        course = 0
        roclimb = 0
        rot = 0
        sensitivity = 0
        gps = ' '
        uniqueid = fix['device']
        dist = fix['dist']
        extpos = ' '
        addcmd = "insert into OGNDATA values ('" + id + "','" + dte + "','" + hora + "','" + station + "'," + str(latitude) + "," + str(longitude) + "," + str(altim) + "," + str(speed) + "," + \
            str(course) + "," + str(roclimb) + "," + str(rot) + "," + str(sensitivity) + \
            ",'" + gps + "','" + uniqueid + "'," + \
            str(dist) + ",'" + extpos + "', 'CAPT' ) "
        try:				# store it on the DDBB
            curs.execute(addcmd)
        except MySQLdb.Error as e:
            try:
                print(">>>MySQL Error [%d]: %s" % (e.args[0], e.args[1]))
            except IndexError:
                print(">>>MySQL Error: %s" % str(e))
                print(">>>MySQL error:", cout, addcmd)
                print(">>>MySQL data :",  data)
            return (False)              # indicate that we have errors
    conn.commit()                       # commit the DB updates
    return(True)			# indicate that we have success


def captaprspush(datafix, prt=False):	# push the data into the OGN APRS

    for fix in datafix['captpos']:	# for each fix on the dict
        id = fix['registration'] 	# extract the information
        if len(id) > 9:
            id = id[0:9]
        dte = fix['date']
        hora = fix['time']
        station = config.location_name
        latitude = fix['Lat']
        longitude = fix['Long']
        altitude = fix['altitude']
        uniqueid = fix['device']
        speed = fix['speed']
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
        if speed != None:
            sss = "%03d" % speed
        else:
            sss = "000"
        aprsmsg = id+">OGCAPT,qAS,CAPTURS:/"+hora+'h'+lat+"/"+lon+"'000/"+sss+"/"
        if altitude > 0:
            aprsmsg += "A=%06d" % int(altitude*3.28084)
        aprsmsg += " id"+uniqueid+" \n"
        rtn = config.SOCK_FILE.write(aprsmsg)
        config.SOCK_FILE.flush()
        print("APRSMSG : ", aprsmsg)
    return(True)


# find all the fixes since TTIME
def captfindpos(ttime, conn, prt=False, store=True, aprspush=False):

    onefound = False
    captLOGIN = config.CAPTURSlogin     # login of the control capture account
    captPASSWD = config.CAPTURSpasswd
    curs = conn.cursor()                # set the cursor for storing the fixes
    cursG = conn.cursor()               # set the cursor for searching the devices
                                        # get all the devices with CAPT
    cursG.execute("select id, active, flarmid, registration from TRKDEVICES where devicetype = 'CAPT'; ")
    rowgall = cursG.fetchall() 	        # look for that registration on the OGN databasea
    for rowg in rowgall:

        captID = rowg[0].lstrip()       # registration to report
        active = rowg[1]		# if active or not
        flarmid = rowg[2]		# Flamd id to be linked
        registration = rowg[3]          # registration id to be linked
        if active == 0:
            continue                    # if not active, just ignore it
        if flarmid == None or flarmid == '': 		# if flarmid is not provided
                                        # get it from the registration
            flarmid = getflarmid(conn, registration)
        else:
            chkflarmid(flarmid)

                                        # build the URL to call to the CAPTURS server
# http://api.capturs.com/device/1AC32E/position/from/1484053861/to/1484917861/limit/1?login=myLogin&password=myPassword
        url = "http://api.capturs.com/device/"+captID+"/position/from/" + \
            str(ttime)+"?login="+captLOGIN+"&password="+str(captPASSWD)
        if prt:				# if we require printing the raw data
            print("URL:", url)
        captpos = {"captpos": []}	# init the dict
                                        # get the JSON data from the CAPT server
        jsondata = captgetapidata(url)
        if prt:				# if we require printing the raw data
            j = json.dumps(jsondata, indent=4)  # convert JSON to dictionary
            print(j)
                                        # find the gliders since TTIME
        found = captgetaircraftpos(jsondata, captpos, ttime, captID, flarmid, prt=False)
        if found:
            onefound = True
        if prt:
            print(captpos)
        if store:
            captstoreitindb(captpos, curs, conn)  # and store it on the DDBB
        if aprspush:
            captaprspush(captpos, prt=prt)	# and push the date thru the APRS

    if onefound:
        now = datetime.utcnow()
                                        # number of second until beginning of the day of 1-1-1970
        td = now-datetime(1970, 1, 1)
        ts = int(td.total_seconds())	# as an integer
        return (ts)			# return TTIME for next call
    else:
        return(ttime)			# if not found, just return the same time

#-------------------------------------------------------------------------------------------------------------------#
