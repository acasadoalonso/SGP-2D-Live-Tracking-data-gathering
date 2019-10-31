#!/bin/python3
import urllib.request, urllib.error, urllib.parse
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
from geopy.distance import vincenty         # use the Vincenty algorithm^M
import MySQLdb                              # the SQL data base routines^M
import config
from flarmfuncs import *
from parserfuncs import deg2dmslat, deg2dmslon


                                            # get the data from the API server
def inreachgetapidata(url, prt=False):

    req = urllib.request.Request(url, headers={'User-Agent': "Magic Browser"})
    req.add_header("Content-Type", "application/kml")
    req.add_header("Content-type", "application/x-www-form-urlencoded")
    try:
        r = urllib.request.urlopen(req)     # open the url resource
    except urllib.error.HTTPError as e:
        print("InReach read error:", e.fp.read())
        return ' '
    kml = r.read().decode('UTF-8')          # read the data on KML format
    if kml == "An error occured.":
        return ' '
    if prt:
        print(kml)                          # print it if requested
    return kml


                                            # extract the data from the JSON object
def inreachaddpos(msg, inreachpos, ttime, regis, flarmid):

    # print msg                             # print the input
    timeutc = msg["Time UTC"] 		    # the time in UTC
    if timeutc[1] == '/':                   # parsed, it is not zero padded
        mm = '0'+timeutc[0:1]
        if timeutc[3] == '/':
            dd = '0'+timeutc[2]
            yy = timeutc[6:8]
            i = 8
        else:
            dd = timeutc[2:4]
            yy = timeutc[7:9]
            i = 9
    else:
        mm = timeutc[0:2]
        if timeutc[5] == '/':
            dd = '0'+timeutc[3]
            yy = timeutc[9:9]
            i = 9
        else:
            dd = timeutc[3:5]
            yy = timeutc[8:10]
            i = 10
    date = yy+mm+dd                         # date in format YYMMDD
                                            # convert to datettime the rest of the data
    timett = datetime.strptime(timeutc[i+1:], "%I:%M:%S %p")
    yyy = int(yy)+2000                      # year on integer format
    mmm = int(mm)
    ddd = int(dd)
    hhh = timett.hour                       # hour on integer format
    min = timett.minute
    sss = timett.second
                                            # rebuild now on datetime format/object
    tt = datetime(yyy, mmm, ddd, hhh, min, sss)
                                            # number of second until beginning of the day of 1-1-1970
    td = tt-datetime(1970, 1, 1)
    unixtime = int(td.total_seconds())      # unixtime as an integer
    #print "TT", date, tt, unixtime
    alt = msg["Elevation"]                  # get the altitude
    altidx = alt.find(' ')                  # delete the extra info
    altitude = alt[0:altidx]
    if (unixtime < ttime or altitude == 0):
        return (False)			    # if is lower than the last time just ignore it
    reg = regis
                                            # extract from the JSON object the data that we need
    lat = msg["Latitude"]
    lon = msg["Longitude"]
    id = msg["IMEI"] 			    # identifier for the final user
    mid = msg["Device Type"] 		    # inreach model number
    sspeed = msg["Velocity"]                # speed
    spdidx = sspeed.find(" ")               # delete the extra information
    speed = sspeed[0:spdidx]
    ccourse = msg["Course"]
    couidx = ccourse.find(" ")              # delete the extra information
    course = ccourse[0:couidx]
    extpos = msg["Valid GPS Fix"] 	    # check if from valid GPS
    name = msg["Name"]                      # pilot name
                                            # convert to ISO format in order to extract all the DATE
    dte = tt.isoformat()
    date = dte[2:4]+dte[5:7]+dte[8:10]
    time = dte[11:13]+dte[14:16]+dte[17:19]
    vitlat = config.FLOGGER_LATITUDE        
                                            # get the coordinates of the BASE station
    vitlon = config.FLOGGER_LONGITUDE
                                            # distance to the station
    distance = vincenty((lat, lon), (vitlat, vitlon)).km
    pos = {"registration": flarmid, "date": date, "time": time, "Lat": lat, "Long": lon, "altitude": altitude,
           "UnitID": id, "GPS": mid, "speed": speed, "course": course, "dist": distance, "extpos": extpos, "PilotName": name}
    inreachpos['inreachpos'].append(pos)		# and store it on the dict
    print("INREACHPOS :", lat, lon, altitude, id, distance, unixtime, dte, date, time, reg, flarmid, extpos, name)
    return (True)			    # indicate that we added an entry to the dict


                                            # return on a dictionary the position of all fix positions
def inreachgetaircraftpos(kml, inreachpos, ttime, regis, flarmid, prt=True):
    msg = {}                                # create the local object
    found = False                           # assume no entries initailly
    doc = ET.fromstring(kml)		    # parse the html data into a XML tree
    for child in doc:                       # go down to the level 5
        #print "L1", child.tag, child.attrib
        for ch in child:
            #print "L2", ch.tag, ch.attrib
            if ch.tag == "{http://www.opengis.net/kml/2.2}Folder":
                for c in ch:
                    #print "L3", c.tag, c.attrib
                    for cc in c:
                        #print "L4", cc.tag, cc.attrib
                        if cc.tag == "{http://www.opengis.net/kml/2.2}ExtendedData":
                            for ccc in cc:  # up to the extended data level
                                #print "L5", ccc.tag, ccc.attrib
                                for cccc in ccc:  # get the data from the dict itself and build our own dict... msg
                                    item = ccc.attrib["name"]
                                    value = ccc.find(
                                        '{http://www.opengis.net/kml/2.2}value').text
                                    msg[item] = value
                                    found = True  # we found some data on the KML string
                                    if prt:
                                        print("InreachPos", item, "==>", value)

    if found:
                                            # add the position for this fix
        found = inreachaddpos(msg, inreachpos, ttime, regis, flarmid)
    #print inreachpos
    return (found)			    # return if we found a message or not


def inreachstoreitindb(datafix, curs, conn):  # store the fix into the database
    for fix in datafix['inreachpos']:       # for each fix on the dict
        id = fix['registration'] 	    # extract the information
        if len(id) > 9:
            id = id[0:9]
        dte = fix['date']
        hora = fix['time']
        station = config.location_name
        latitude = fix['Lat']
        longitude = fix['Long']
        altim = fix['altitude']
        speed = fix['speed']
        course = fix['course']
        roclimb = 0                         # no rate of climd in Inreach
        rot = 0                             # no reate of turn
        sensitivity = 0                     # no sensitivity
        gps = fix['GPS']		    # model id
        gps = gps[0:6]                      # only six chars
        uniqueid = str(fix["UnitID"])       # identifier of the owner
        dist = fix['dist']                  # distance to the base
        extpos = fix['extpos']		    # battery state
        addcmd = "insert into OGNDATA values ('" + id + "','" + dte + "','" + hora + "','" + station + "'," + str(latitude) + "," + str(longitude) + "," + str(altim) + "," + str(speed) + "," + \
            str(course) + "," + str(roclimb) + "," + str(rot) + "," + str(sensitivity) + \
            ",'" + gps + "','" + uniqueid + "'," + \
            str(dist) + ",'" + extpos + "', 'INRE' ) "
        try:				    # store it on the DDBB
            curs.execute(addcmd)
        except MySQLdb.Error as e:
            try:
                print(">>>MySQL Error [%d]: %s" % (e.args[0], e.args[1]))
            except IndexError:
                print(">>>MySQL Error: %s" % str(e))
                print(">>>MySQL error:", cout, addcmd)
                print(">>>MySQL data :",  data)
            return (False)	            # indicate that we have errors
    conn.commit()                           # commit the DB updates
    return(True)			    # indicate that we have success


def inreachaprspush(datafix, prt=False):    # push the data into the OGN APRS
    for fix in datafix['inreachpos']:       # for each fix on the dict
        id = fix['registration'] 	    # extract the information
        if len(id) > 9:
            id = id[0:9]
        dte = fix['date']                   # date
        hora = fix['time']
        latitude = float(fix['Lat'])
        longitude = float(fix['Long'])
        altitude = float(fix['altitude']) * 3.28084
        speed = fix['speed']
        course = fix['course']
        roclimb = 0
        rot = 0
        sensitivity = 0
        gps = fix['GPS']		    # model ID
        gps = gps[0:6]                      # only six chars
        uniqueid = str(fix["UnitID"])       # identifier of the owner
        dist = fix['dist']		    # distance to BASE
        extpos = fix['extpos']		    # GPS valid fix
        pilotname = fix['PilotName']        # Pilot name
                                            # build the APRS message
                                            # convert the latitude to the format required by APRS
        lat = deg2dmslat(abs(latitude))
        if latitude > 0:
            lat += 'N'
        else:
            lat += 'S'
                                            # convert longitude to the DDMM.MM format
        lon = deg2dmslon(abs(longitude))
        if longitude > 0:
            lon += 'E'
        else:
            lon += 'W'

        aprsmsg = id+">OGINRE,qAS,INREACH:/"+hora+'h'+lat+"/"+lon+"'000/000/"
        if altitude > 0:
            aprsmsg += "A=%06d" % int(altitude)
        aprsmsg += " id"+uniqueid+" "+gps+" "+extpos+" "+pilotname+" \n"
        print("APRSMSG : ", aprsmsg)
        rtn = config.SOCK_FILE.write(aprsmsg)
    return(True)


                                            # find all the fixes since TTIME
def inreachfindpos(ttime, conn, prt=False, store=True, aprspush=False):

    foundone = False			    # asume no found
    curs = conn.cursor()                    # set the cursor for storing the fixes
    cursG = conn.cursor()                   # set the cursor for searching the devices
                                            # get all the devices with INRE
    cursG.execute(
        "select id, spotid as inreachid, spotpasswd as inreachpasswd, active, flarmid, registration from TRKDEVICES where devicetype = 'INRE'; ")
    for rowg in cursG.fetchall(): 	    # look for that registration on the OGN database

        reg = rowg[0]		            # registration to report
        inreachID = rowg[1]	            # INREach
        inreachpasswd = rowg[2]	            # InReach password
        active = rowg[3]		    # if active or not
        flarmid = rowg[4]		    # Flamd id to be linked
        registration = rowg[5]	            # registration id to be linked
        if active == 0:
            continue	                    # if not active, just ignore it
        if flarmid == None or flarmid == '': 		# if flarmid is not provided
                                            # get it from the registration
            flarmid = getflarmid(conn, registration)
        else:
            chkflarmid(flarmid)

                                            # build the URL to call to the InReach server
        if ttime == 0:
            url = "http://inreach.garmin.com/feed/share/"+inreachID
        else:
                                            # get the date in ISO format to be used on the URL
            tt = datetime.utcfromtimestamp(ttime)
            ts = tt.isoformat()
            url = "http://inreach.garmin.com/feed/share/" + \
                inreachID+"?d1="+str(ts)
        if prt:
            print(url)
        print(url)
        inreachpos = {"inreachpos": []}     # init the dict
                                            # get the KML data from the InReach server
        kml = inreachgetapidata(url)
        if kml == ' ':
            return -1                       # return error
        if prt:				    # if we require printing the raw data
            print("KML ===>", kml)          # print the KML data
                                            # find the gliders since TTIME
        found = inreachgetaircraftpos(
            kml, inreachpos, ttime, reg, flarmid, prt=prt)
        if found:
            foundone = True
        if prt:
            print(inreachpos)
        if store:
                                            # and store it on the DDBB
            inreachstoreitindb(inreachpos, curs, conn)
        if aprspush:
            inreachaprspush(inreachpos, prt)	# and push the data into the APRS

    if foundone:
        now = datetime.utcnow()
                                            # number of second until beginning of the day of 1-1-1970
        td = now-datetime(1970, 1, 1)
        ts = int(td.total_seconds())        # as an integer
        return (ts)			    # return TTIME for next call
    else:
        return (ttime)			    # keep old value

#-------------------------------------------------------------------------------------------------------------------#
