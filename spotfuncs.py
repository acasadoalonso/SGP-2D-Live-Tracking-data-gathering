#!/bin/python3
import urllib.request
import urllib.error
import urllib.parse
import json
from datetime import datetime
from geopy.distance import geodesic         # use the Vincenty algorithm^M
import MySQLdb                              # the SQL data base routines^M
import config
from flarmfuncs import getflarmid, chkflarmid
from ognddbfuncs import getognflarmid, get_by_dvt
from parserfuncs import deg2dmslat, deg2dmslon
from dtfuncs import naive_utcnow

# get the data from the API server
def spotgetapidata(url, prt=False):

    req = urllib.request.Request(url)	    # build the request
    req.add_header("Content-Type", "application/json")
    req.add_header("Content-type", "application/x-www-form-urlencoded")
    r = urllib.request.urlopen(req)         # open the url resource
    js=r.read().decode('UTF-8')
    j_obj = json.loads(js)                  # convert to JSON

    if prt:
        print(json.dumps(j_obj, indent=4))
    return j_obj                            # return the JSON object


def spotaddpos(msg, spotpos, ttime, regis, flarmid):  # extract the data from the JSON object
    if "unixTime" not in msg:		    # check for errors
       return (False)
    unixtime = msg["unixTime"] 		    # the time from the epoch
    altitude = msg["altitude"]
    if (unixtime < ttime or altitude == 0):
        return (False)			    # if is lower than the last time just ignore it
    reg = regis
    # extract from the JSON object the data that we need
    lat = msg["latitude"]
    lon = msg["longitude"]
    id = msg["messengerId"] 		    # identifier for the final user
    mid = msg["modelId"] 		    # spot model number
    dte = msg["dateTime"]
    extpos = msg["batteryState"] 	    # battery state
    date = dte[2:4]+dte[5:7]+dte[8:10]
    time = dte[11:13]+dte[14:16]+dte[17:19]
    if 'GOOD' not in msg.get('batteryState', 'GOOD'):
        print("WARNING: spot battery is in state: %s ID=%s " % (
            msg.get('batteryState'), regis))
    vitlat = config.FLOGGER_LATITUDE
    vitlon = config.FLOGGER_LONGITUDE
    # distance to the station
    distance = geodesic((lat, lon), (vitlat, vitlon)).km
    pos = {"registration": flarmid, "date": date, "time": time, "Lat": lat, "Long": lon,
           "altitude": altitude, "UnitID": id, "GPS": mid, "dist": distance, "extpos": extpos}
    spotpos['spotpos'].append(pos)	    # and store it on the dict
    print("SPOTPOS :", lat, lon, altitude, id, distance, unixtime, dte, date, time, reg, flarmid, extpos)
    return (True)			    # indicate that we added an entry to the dict


# return on a dictionary the position of all spidertracks
def spotgetaircraftpos(data, spotpos, ttime, regis, flarmid, prt=False):
    foundone = False
    response = data['response']		    # get the response entry
    if response.get('errors'):		    # if error found
        return(False)			    # return indicating errors

    feed = response["feedMessageResponse"]  # get the message response
    msgcount = feed['count']		    # get the count of messages
    messages = feed['messages']		    # get the messages
    message = messages['message']           # get the individual message
    #print "M:", message
    if msgcount == 1:			    # if only one message, that is the message
        if prt:
            # convert JSON to dictionary
            print(json.dumps(feed, indent=4))
        found = spotaddpos(message, spotpos, ttime, regis, flarmid)
        foundone = found
    else:
        for msg in message:		    # if not iterate the set of messages
            if prt:
                # convert JSON to dictionary
                print(json.dumps(msg, indent=4))
                # add the position for this fix
            found = spotaddpos(msg, spotpos, ttime, regis, flarmid)
            if found:
                foundone = True
    return (foundone)			    # return if we found a message or not


def spotstoreitindb(datafix, curs, conn):   # store the fix into the database
    for fix in datafix['spotpos']:	    # for each fix on the dict
        id = fix['registration'] 	    # extract the information
        if len(id) > 9:
            id = id[0:9]
        dte = fix['date']
        hora = fix['time']
        station = config.location_name
        latitude = fix['Lat']
        longitude = fix['Long']
        altim = fix['altitude']
        speed = 0
        course = 0
        roclimb = 0
        rot = 0
        sensitivity = 0
        gps = fix['GPS']		    # model id
        gps = gps[0:6]
        uniqueid = str(fix["UnitID"])       # identifier of the owner
        dist = fix['dist']
        extpos = fix['extpos']		    # battery state
        addcmd = "insert into OGNDATA values ('" + id + "','" + dte + "','" + hora + "','" + station + "'," + str(latitude) + "," + str(longitude) + "," + str(altim) + "," + str(speed) + "," + \
            str(course) + "," + str(roclimb) + "," + str(rot) + "," + str(sensitivity) + \
            ",'" + gps + "','" + uniqueid + "'," + \
            str(dist) + ",'" + extpos + "', 'SPOT' ) "
        try:				    # store it on the DDBB
            curs.execute(addcmd)
        except MySQLdb.Error as e:
            try:
                print(">>>MySQL Error [%d]: %s" % (e.args[0], e.args[1]))
            except IndexError:
                print(">>>MySQL Error: %s" % str(e))
                print(">>>MySQL error:", addcmd)
            return (False)                  # indicate that we have errors
    conn.commit()                           # commit the DB updates
    return(True)			    # indicate that we have success


def spotaprspush(datafix, prt=False):       # push the data into the OGN APRS
    for fix in datafix['spotpos']:          # for each fix on the dict
        id = fix['registration'] 	    # extract the information
        if len(id) > 9:
            id = id[0:9]
        dte = fix['date']
        hora = fix['time']
        latitude = fix['Lat']
        longitude = fix['Long']
        altitude = fix['altitude']
        speed = 0
        course = 0
        roclimb = 0
        rot = 0
        sensitivity = 0
        gps = fix['GPS']		    # model ID
        uniqueid = str(fix["UnitID"])       # identifier of the owner
        dist = fix['dist']		    # distance to BASE
        extpos = fix['extpos']		    # battery state
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

        aprsmsg = id+">OGSPOT,qAS,SPOT:/"+hora+'h'+lat+"/"+lon+"'000/000/"
        if altitude > 0:
            aprsmsg += "A=%06d" % int(altitude*3.28084)
        else:
            aprsmsg += "A=000000"
        aprsmsg += " id"+uniqueid+" "+gps+" "+extpos+" \n"
        config.SOCK_FILE.write(aprsmsg)
        config.SOCK_FILE.flush()
        print("APRSMSG : ", aprsmsg)
    return(True)


def spotgetdata(spotID, spotpasswd, prt):
    # build the URL to call to the SPOT server
    if spotpasswd == '' or spotpasswd == None:
        url = "https://api.findmespot.com/spot-main-web/consumer/rest-api/2.0/public/feed/" + \
            spotID+"/message.json"
    else:
        url = "https://api.findmespot.com/spot-main-web/consumer/rest-api/2.0/public/feed/" + \
            spotID+"/message.json?feedPassword="+str(spotpasswd)
    if prt:
        print(url)
        # get the JSON data from the SPOT server
    jsondata = spotgetapidata(url)
    if prt:				    # if we require printing the raw data
        j = json.dumps(jsondata, indent=4)  # convert JSON to dictionary
        print(j)
    return(jsondata)

    # find all the fixes since TTIME


def spotfindpos(ttime, conn, prt=False, store=True, aprspush=False):
    foundone = False			    # asume no found
    if conn:
        curs = conn.cursor()                    # set the cursor for storing the fixes
        cursG = conn.cursor()                   # set the cursor for searching the devices
        # get all the devices with SPOT
        cursG.execute("select id, spotid, spotpasswd, active, flarmid, registration from TRKDEVICES where devicetype = 'SPOT'; ")
        for rowg in cursG.fetchall(): 	    # look for that registration on the OGN database

            reg = rowg[0]		            # registration to report
            spotID = rowg[1]		    # SPOTID
            spotpasswd = rowg[2]                # SPOTID password
            active = rowg[3]		    # if active or not
            flarmid = rowg[4]		    # Flamd id to be linked
            registration = rowg[5]              # registration id to be linked
            if active == 0:
                continue                        # if not active, just ignore it
            if flarmid == None or flarmid == '':  # if flarmid is not provided
                # get it from the registration
                flarmid = getflarmid(conn, registration)
            else:
                chkflarmid(flarmid)
            if flarmid == "NOREG":              # in case of no registration on the DDBa
                flarmid=getognflarmid(registration)
            if flarmid == "NOFlarm":              # in case of no registration on the DDB
                print(">>>> Reg", reg, "spotID", spotID, "FlarmID", flarmid, "Registration", registration, "<<<<<<\n")
                flarmid = registration          # just print warning and use the registration
            jsondata=spotgetdata(spotID, spotpasswd, prt)
            # find the gliders since TTIME
            spotpos = {"spotpos": []}    	    # init the dict
            found = spotgetaircraftpos(jsondata, spotpos, ttime, reg, flarmid, prt=False)
            if found:
                foundone = True
            if prt:
                print(spotpos)
            if store:
                spotstoreitindb(spotpos, curs, conn)  # and store it on the DDBB
            if aprspush:
                spotaprspush(spotpos, prt)	    # and push the data into the APRS
    else:
        devdvt=[]
        n=get_by_dvt(devdvt, "S")
        if n > 0:
            for dev in devdvt:
                if (dev['tracked'] == 'N' or dev['identified'] == 'N' or dev['device_active'] == 'N' or dev['aircraft_active'] == 'N'):
                    continue		# nothing to do
                spotID = dev['device_id']
                if 'device_password' in dev:
                    spotpasswd = dev['device_password']
                else:
                    spotpasswd = ''		# no password support yet
                registration=dev['registration']
                aprsid=dev['device_aprsid']  # APRS ID assigned
                reg=aprsid
                flarmid=getognflarmid(registration)   # get the flarmid for ogn ddb in case of device match
                if flarmid == "NOFlarm":              # in case of no registration on the DDB
                    print(">>>> Reg", aprsid, "spotID", spotID, "FlarmID", flarmid, "Registration", registration, "<<<<<<\n")
                    flarmid = aprsid                # just print warning and use the registration

                jsondata=spotgetdata(spotID, spotpasswd, prt)
                spotpos = {"spotpos": []}    	    # init the dict
                found = spotgetaircraftpos(jsondata, spotpos, ttime, reg, flarmid, prt=False)
                if found:
                    foundone = True
                if prt:
                    print(spotpos)
                if aprspush:
                    spotaprspush(spotpos, prt)	    # and push the data into the APRS
    if foundone:
        now = naive_utcnow()
        # number of second until beginning of the day of 1-1-1970
        td = now-datetime(1970, 1, 1)
        ts = int(td.total_seconds())        # as an integer
        return (ts)			    # return TTIME for next call
    else:
        return (ttime)			    # keep old value

#-------------------------------------------------------------------------------------------------------------------#
