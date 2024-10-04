#!/bin/python3
import urllib.request
import urllib.error
import urllib.parse
import json
from datetime import datetime
from geopy.distance import geodesic       # use the Vincenty algorithm^M
import MySQLdb                            # the SQL data base routines^M
import urllib.request
import urllib.parse
import urllib.error
import config
from flarmfuncs import getflarmid
from parserfuncs import deg2dmslat, deg2dmslon
from dtfuncs import naive_utcnow
#-------------------------------------------------------------------------------------------------------------------#


def skylgetapidata(url): 	            # get the data from the API server
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/json")
    req.add_header("Content-Type", "application/json")
    r = urllib.request.urlopen(req)         # open the url resource
    js=r.read().decode('UTF-8')
    j_obj = json.loads(js)                  # convert to JSON

    return j_obj                            # return the JSON object
#-------------------------------------------------------------------------------------------------------------------#

    # extract the data of the last know position from the JSON object


def skyladdpos(tracks, skylpos, ttime, pilotname, gliderreg):

    foundone = False
    for msg in tracks:
        pilot = msg['pilot']		    # get the pilot infor id/name
        name = pilot['name']		    # pilot name
        id = pilot['id']		    # pilot ID
        pilotname = pilotname.decode("utf-8")
        if pilotname.isnumeric():           # id numeric is pilot id
            # if is not this pilot id nothing to do
            if pilotname.strip(' ') != id.strip(' '):
                continue
        else:
            # if is not this pilot name nothing to do
            if pilotname.strip(' ') != name.strip(' '):
                continue
        foundone = True
        dte = msg['time']		    # get the time on ISO format
        dte = dte[0:19]			    # get the important part
        ttt = datetime.strptime(dte, "%Y-%m-%dT%H:%M:%S")  # parser the time
        # number of second until beginning of the day
        td = ttt-datetime(1970, 1, 1)
        ts = int(td.total_seconds())        # Unix time - seconds from the epoch
        location = msg['location']
        lon = location[0]
        lat = location[1] 		    # extract the longitude and latitude
        alt = msg["altitude"] 		    # and the altitude
        gps = "NO"
        extpos = "NO"
        roc = 0
        dir = 0
        spd = 0
        date = dte[2:4]+dte[5:7]+dte[8:10]
        time = dte[11:13]+dte[14:16]+dte[17:19]

        vitlat = config.FLOGGER_LATITUDE
        vitlon = config.FLOGGER_LONGITUDE
        distance = geodesic((lat, lon), (vitlat, vitlon)
                            ).km            # distance to the station
        pos = {"pilotname": pilotname, "date": date, "time": time, "Lat": lat, "Long": lon, "altitude": alt, "UnitID": id,
               "dist": distance, "course": dir, "speed": spd, "roc": roc, "GPS": gps, "extpos": extpos, "gliderreg": gliderreg}
        #print "SSS:", ts, ttime, pos
        if ts < ttime+30:		    # check if the data is from before
            continue		            # in that case nothing to do
        skylpos['skylpos'].append(pos)      # and store it on the dict
        print("SKYLPOS :", round(lat, 4), round(lon, 4), alt, id, round(
            distance, 4), ts, dte, date, time, pilotname)

    return(foundone) 			    # indicate that we added an entry to the dict


#-------------------------------------------------------------------------------------------------------------------#


def skylstoreitindb(datafix, curs, conn):   # store the fix into the database

    for fix in datafix['skylpos']:	    # for each fix on the dict
        idpn = fix['pilotname']		    # extract the information
        dte = fix['date']
        hora = fix['time']
        station = config.location_name
        latitude = fix['Lat']
        longitude = fix['Long']
        altitude = fix['altitude']
        speed = fix['speed']
        course = fix['course']
        roclimb = fix['roc']
        rot = 0
        sensitivity = 0
        gps = fix['GPS']
        uniqueid = str(fix["UnitID"])
        dist = fix['dist']
        extpos = fix['extpos']
        gliderreg = fix['gliderreg']
        flarmid = getflarmid(conn, gliderreg)
        addcmd = "insert into OGNDATA values ('" + flarmid + "','" + dte + "','" + hora + "','" + station + "'," + str(latitude) + "," + str(longitude) + "," + str(altitude) + "," + str(speed) + "," + \
            str(course) + "," + str(roclimb) + "," + str(rot) + "," + str(sensitivity) + \
            ",'" + gps + "','" + uniqueid + "'," + \
            str(dist) + ",'" + extpos + "', 'SKYL' ) "
        try:				    # store it on the DDBB
            #print addcmd
            curs.execute(addcmd)
        except MySQLdb.Error as e:
            try:
                print(">>>MySQL Error [%d]: %s" % (e.args[0], e.args[1]))
            except IndexError:
                print(">>>MySQL Error: %s" % str(e))
                print(">>>MySQL error:", addcmd, idpn)
            return (False)                  # indicate that we have errors
    conn.commit()                           # commit the DB updates
    return(True)			    # indicate that we have success

#-------------------------------------------------------------------------------------------------------------------#


def skylaprspush(datafix, conn, prt=False):

    for fix in datafix['skylpos']:	    # for each fix on the dict
        idpn 			= fix['pilotname']		    # extract the information
        dte 			= fix['date']
        hora 			= fix['time']
        station = config.location_name
        latitude 		= fix['Lat']
        longitude 		= fix['Long']
        altitude 		= fix['altitude']
        speed 			= fix['speed']
        course 			= fix['course']
        roclimb			 = fix['roc']
        rot = 0
        sensitivity = 0
        gps 			= fix['GPS']
        uniqueid 		= str(fix["UnitID"])
        dist 			= fix['dist']
        extpos 			= fix['extpos']
        gliderreg 		= fix['gliderreg']
        flarmid 		= getflarmid(conn, gliderreg)
        # build the APRS message
        lat 			= deg2dmslat(abs(latitude))
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
        aprsmsg = flarmid+">OGSKYL,qAS,SKYLINES:/" + \
            hora+'h'+lat+"/"+lon+"'"+ccc+"/"+sss+"/"
        if altitude > 0:
            aprsmsg += "A=%06d" % int(altitude*3.28084)
        aprsmsg += " id"+uniqueid+" %+04dfpm " % (int(roclimb))+" \n"
        print("APRSMSG: ", aprsmsg)
        config.SOCK_FILE.write(aprsmsg)
        config.SOCK_FILE.flush()

    return (True)

#-------------------------------------------------------------------------------------------------------------------#


# find all the fixes since TTIME . Scan all the SKYL devices for new data
def skylfindpos(ttime, conn, prt=False, store=True, aprspush=False):

    curs = conn.cursor()                # set the cursor for storing the fixes
    cursG = conn.cursor()               # set the cursor for searching the devices
    # get the counter of IDs
    cursG.execute(
        "select count(*) from TRKDEVICES where devicetype = 'SKYL' and active = '1'; ")
    cnt = cursG.fetchone()
    cnt = int(cnt[0])
    if cnt == 0:
        now = naive_utcnow()
        # number of second until beginning of the day of 1-1-1970
        td = now-datetime(1970, 1, 1)
        sync = int(td.total_seconds())  # as an integer
        return (sync+1)			# return TTIME for next call
    url = "https://skylines.aero/api/live"
    skylpos = {"skylpos": []}		# init the dicta
    pos = skylgetapidata(url)           # get the JSON data from the Skylines server
    if prt:
        print(json.dumps(pos, indent=4))  # convert JSON to dictionary
    tracks = pos['tracks']
    # get all the devices with SKYL
    cursG.execute(
        "select id, Registration, active from TRKDEVICES where devicetype = 'SKYL' ; ")
    for rowg in cursG.fetchall(): 	# look for that registration on the OGN database

        pilotname = rowg[0]             # pilotname to report
        gliderreg = rowg[1]             # Glider registration EC-???
        active = rowg[2]		# if active or not
        if active == 0:
            continue                    # if not active, just ignore it
            # build the userlist to call to the SKYL server
        skyladdpos(tracks, skylpos, ttime, pilotname, gliderreg)  # find the gliders since TTIME
    if prt:
        print(skylpos)
    if store:
        skylstoreitindb(skylpos, curs, conn)  # and store it on the DDBB
    if aprspush:
        skylaprspush(skylpos, conn, prt=prt)  # and push it into the OGN APRS
    now = naive_utcnow()
    # number of second until beginning of the day of 1-1-1970
    td = now-datetime(1970, 1, 1)
    sync = int(td.total_seconds())      # as an integer
    return (sync+1)			# return TTIME for next call

#-------------------------------------------------------------------------------------------------------------------#
