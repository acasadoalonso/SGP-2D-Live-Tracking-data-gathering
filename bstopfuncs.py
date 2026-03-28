#!/bin/python3
#-------------------------------------------------------------------------------------------------------------------#
# this functions deals with the data received by the birdstop detectors    api.birdstop.io 
#-------------------------------------------------------------------------------------------------------------------#
 
import json
from   datetime import datetime
from   geopy.distance import geodesic       	# use the Vincenty algorithm^M
from   parserfuncs import deg2dmslat, deg2dmslon, dao
import urllib.request
import urllib.error
import psutil
import config
from   dtfuncs import naive_utcnow, naive_utcfromtimestamp

#-------------------------------------------------------------------------------------------------------------------#
#-------------------------------------------------------------------------------------------------------------------#
# example: curl -G "http://3.22.63.131/v1/detections"   -H "X-API-Key: bsdk_live_ogn_xk9mPqR2vTwL4nYsJ7hB"   --data-urlencode "type=bird"   --data-urlencode "from=2026-03-15T00:00:00"   --data-urlencode "min_confidence=0.8"   --data-urlencode "limit=25" | jq
#
example= {
  "count": 25,
  "data": [
    {
      "altitude_m": 50.0,
      "confidence": 0.8,
      "id": "bird_LCG2_4063986",
      "latitude": 41.999973992671606,
      "longitude": 2.9999794882946733,
      "metadata": {
        "category": "Bird",
        "distance_from_mic": 3.205619471300825,
        "gs_knts": None,
        "track_deg": 0.0,
        "vertical_rate": 0
      },
      "sensor": "LCG2",
      "site_id": "LCG2",
      "site_name": "LCG2",
      "timestamp": "2026-03-27T16:06:03Z",
      "track_id": "1",
      "type": "bird"
    },
    {
      "altitude_m": 53.0,
      "confidence": 0.8,
      "id": "bird_LCG2_4063958",
      "latitude": 43.30594743609879,
      "longitude": -8.371980763198955,
      "metadata": {
        "category": "Bird",
        "distance_from_mic": 50.0,
        "gs_knts": None,
        "track_deg": 0.0,
        "vertical_rate": 0
      }
   }
   ]
}
#-------------------------------------------------------------------------------------------------------------------#

def bstopgetapidata(url, prt=False):		# get the data from the aero-network using the API

    if prt:
       print("URL:", url)   
    req = urllib.request.Request(url)	    	# build the request

    req.add_header("Content-Type", "application/json")
    req.add_header("X-API-Key", config.BSTOPapikey) # add the API key to the header
    try:
       r = urllib.request.urlopen(req,timeout=30) # open the url resource
       rc=r.getcode()				# get the return code
    except Exception as e:
       print ("Error on urlopen: ", e)
       return []				# if we have an error, we return an empty list
    if rc != 200:				# if we have an error, we return an empty JSON object	
       print ("BSTOP RC = ", rc)
       j_obj = []
       return j_obj                            	# return the JSON object
    js=r.read().decode('UTF-8')
    if len(js) > 0:				# if we have data, we convert it to JSON
       j_obj = json.loads(js)                  	# convert to JSONa
    else:
       j_obj = []				# if we have no data, we return an empty list
    if 'data' not in j_obj:
       print ("BSTOP No data field in the JSON object")
       j_obj['data'] = []			# if we have no data, we return an empty list

    j_obj["data"].sort(key=lambda x: x["timestamp"]) # sort the data by timestamp, so we can process it in order
    if prt:
        print(json.dumps(j_obj, indent=4))
    return j_obj['data']                       	# return the JSON object

#-------------------------------------------------------------------------------------------------------------------#

# extract the data of the last know position from the JSON object

#-------------------------------------------------------------------------------------------------------------------#

def bstopaddpos(tracks, bstoppos, ttime, bstopnow, prt=False):	# build the bstoppos from the tracks received

    foundone = False				# assuming nothing found
    for msg in tracks:				# for each track received
        #print ("TRKS:", msg)
        src='BSTOP'				# BSTOP is the default
        if "id" in msg:
            ID = msg['id']
        else:
            print ("BSTOP No id")
            continue
        ID = msg['id'].upper()			# aircraft/bird/drone ID
        ID = ID[-6:]				# get the last 6 characters of the ID
        if ID.isnumeric():			# in case of number, convert to hex
           ID="%05X"%int(ID)			# convert to hex
        aid="OGNF"+ID[-5:]			# build the ICAO ID for OGN
        unitid="37F"+ID[-5:]			# build the uniqueID for OGN
						# we use 37F as prefix to avoid conflicts with real airplanes
        if "timestamp" in msg:			# check if we have the timestamp        
            t=msg['timestamp']	    		# when the aircraft was seen
        					# ISO 8601 format: 2026-03-24T05:59:44
        else:
            print ("BSTOP No timestamp")	#
            continue				# ignore the traffic with no timestamp
						# if we have timestamp, we assume that we have GPS
        if "longitude" in msg:			# check if we have longitude and latitude
            lon = msg['longitude']
        else:
            print ("BSTOP No lon")
            continue				# ignore the traffic with no position
        if "latitude" in msg:			# check if we have longitude and latitude
            lat = msg['latitude'] 		# extract the longitude and latitude
        else:
            print ("BSTOP No lat")
            continue				# ignore the traffic with no position
						# if we have position, we assume that we have GPS

        gps = "NO"				# set all the defaults
        extpos = "NO"
        roc=0
        rot=0
        tdir=0
        spd=0
        FL=0
        cat=''
        alt=0
        ts=0
        flg=''
        otype=''
        

        if "type" in msg:			# check if drone or bird
           otype = msg['type']			# get the type of the target
           cat = otype.upper()			# get the category	

        if "altitude_m" in msg:			# alt QFE in metters
                alt = msg["altitude_m"]*3.28084 # convert to feet and set it as altitude 
                FL = alt/100			# and FL	

        date = t[2:4]+t[5:7]+t[8:10]		# date and time in the format YYMMDD and HHMMSS
        tme =  t[11:13]+t[14:16]+t[17:19]	# we use the timestamp as time of the fix, and we ignore the time when we receive the message, because it can be delayed
        if 'metadata' in msg:			# if we have metadata, we can extract more information
           #print ("METADATA:", msg['metadata'])
           if "track_deg" in msg['metadata'] and msg['metadata']['track_deg'] != None:
              tdir = msg['metadata']['track_deg']	# get the track direction
           if "gs_knts" in msg['metadata'] and msg['metadata']['gs_knts'] != None:
              spd = msg['metadata']['gs_knts']*1.852 # get the speed in knots and convert to km/h
           if "vertical_rate" in msg['metadata'] and msg['metadata']['vertical_rate'] != None:
              roc = msg['metadata']['vertical_rate'] # get the vertical rate in ft/min 
           if "category" in msg['metadata']:
              cat = msg['metadata']['category'] # get the category from the metadata, because it can be more specific than the type
        # print ("TTT:", t, ts, bstopnow, date, tme, msg)
        vitlat = config.FLOGGER_LATITUDE	# get the distance to the dummy station 
        vitlon = config.FLOGGER_LONGITUDE
        distance = geodesic((lat, lon), (vitlat, vitlon)).km            # distance to the station

        pos = {"ICAOID": aid, "date": date, "time": tme, "Lat": lat, "Long": lon, "altitude": alt, "UnitID": unitid,
               "dist": distance, "course": tdir, "speed": spd, "roc": roc, "rot": rot, "GPS": gps, "extpos": extpos, 
               "flight": flg, "FL" : FL, "source": src, "cat": cat}

        #print ("SSSpos:", ttime, pos, "\n\n")
        if alt < int(config.BSTOPfl) :		# filter by FL
           bstoppos['bstoppos'].append(pos)     # and store it on the dict
        if prt:					# print the data
            print("bstopPOS :", round(lat, 4), round(lon, 4), alt, aid, round(distance, 4), ts, date, tme, flg)
        foundone = True				# mark that we found one

    return(foundone) 			    	# indicate that we added an entry to the dict


#-------------------------------------------------------------------------------------------------------------------#
# Store the data into the DDBB
#-------------------------------------------------------------------------------------------------------------------#

def bstopstoreitindb(datafix, curs, conn):   	# store the fix into the database

    import MySQLdb                          	# the SQL data base routines^M
    for fix in datafix['bstoppos']:	    	# for each fix on the dict
        iid       = fix['ICAOID']	    	# extract the information
        dte       = fix['date']
        hora      = fix['time']
        station   = config.location_name
        latitude  = fix['Lat']
        longitude = fix['Long']
        altitude  = fix['altitude']
        speed     = fix['speed']
        course    = fix['course']
        roclimb   = fix['roc']
        rot       = fix['rot']
        sensitivity = 0
        gps       = fix['GPS']
        uniqueid  = str(fix["UnitID"])
        dist      = fix['dist']
        extpos    = fix['extpos']

        if altitude == None or altitude == 0:
            print ("STOREITINDB No altitude:", altitude, speed, roclimb)
            continue								# ignore the traffic with no altitude

        addcmd = "insert into OGNDATA values ('" + iid + "','" + dte + "','" + hora + "','" + station + "'," + \
            str(latitude) + "," + str(longitude) + "," + str(altitude) + "," + str(speed) + "," + \
            str(course) + "," + str(roclimb) + "," + str(rot) + "," + str(sensitivity) + \
            ",'" + gps + "','" + uniqueid + "'," + \
            str(dist) + ",'" + extpos + "', 'bstop' ) "
        try:				    	# store it on the DDBB
            #print addcmd
            curs.execute(addcmd)
        except MySQLdb.Error as e:		# if we have an error, we print it and we return False
            try:
                print(">>>MySQL Error [%d]: %s" % (e.args[0], e.args[1]))
            except IndexError:
                print(">>>MySQL Error: %s" % str(e))
                print(">>>MySQL error:", addcmd)
            return (False)                  	# indicate that we have errors
    conn.commit()                           	# commit the DB updates
    return(True)			    	# indicate that we have success

#-------------------------------------------------------------------------------------------------------------------#
# Push the data received into the OGN APRS
#-------------------------------------------------------------------------------------------------------------------#
#APRSMSG:  OGNF0D3F7>OGBSTOP,qAS,SpaiBSTOP:/235811h4318.13N\00822.61W^000/000/A=000173 id37F0D3F7  !W05!  Bird
#APRSMSG:  OGNF0D3F9>OGBSTOP,qAS,SpaiBSTOP:/000000h4318.27N\00822.45W^000/000/A=000173 id37F0D3F9  !W10!  Bird
#-------------------------------------------------------------------------------------------------------------------#


def bstopaprspush(datafix, prt=False):
    print ("APRSpush start: ", len(datafix))
    cnt=0					# counter of messgages
    for fix in datafix['bstoppos']:	    	# for each fix on the dict
        if prt:
           print ("FIX: ", fix)
        id       = fix['ICAOID']		# extract the information
        dte      = fix['date']
        hora     = fix['time']
        station  = config.location_name
        latitude = fix['Lat']
        longitude= fix['Long']
        daotxt="!W"+dao(latitude)+dao(longitude)+"!"  # the extended precision
        altitude = fix['altitude']
        speed    = fix['speed']
        course   = fix['course']
        roclimb  = fix['roc']
        rot      = fix['rot']
        sensitivity = 0
        gps      = fix['GPS']
        uniqueid = fix["UnitID"]
        src      = fix['source']
        if src == 'BSTOP':
           uniqueid = '37'+uniqueid[3:]
        dist     = fix['dist']
        extpos   = fix['extpos']
        flight   = fix['flight']
        FL       = fix['FL']
        cat      = fix['cat']
        # build the APRS message
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
        if roclimb == None:
            roclimb = 0
        aprsmsg = id+">OGBSTOP,qAS,"+config.BSTOPname+":/" + \
            hora+'h'+lat+"\\"+lon+"^"+ccc+"/"+sss+"/"
        if altitude != None and altitude > 0:
            aprsmsg += "A=%06d" % int(altitude)
        else:
            print ("APRSPUSH No altitude:", altitude, speed, roclimb)
            continue								# ignore the traffic with no altitude
        aprsmsg += " id"+uniqueid+" %+04dfpm " % (int(roclimb))+" "+str(rot)+"rot "+daotxt+" "
        if cat != None and cat != '':
           aprsmsg += " "+cat
        aprsmsg += " \n" 
        if True:
           print("APRSMSG: ", aprsmsg[0:-1])
        rtn = config.SOCK_FILE.write(aprsmsg)
        if rtn == 0:
	    print("Error writing msg:", aprsmsg)
            return(0)
        try:
           config.SOCK_FILE.flush()
        except Exception as e:
           print ("error on flush: ", e)
        cnt += 1
        if rtn == 0:
            print("Error writing msg:", aprsmsg)

    return (cnt)

#-------------------------------------------------------------------------------------------------------------------#
#LEMD>OGNSDR,TCPIP*,qAC,GLIDERN2:/141436h4030.49NI00338.59W&/A=002280
#LEMD>OGNSDR,TCPIP*,qAC,GLIDERN2:>141436h v0.2.8.RPI-GPU CPU:0.6 RAM:710.8/972.2MB NTP:0.3ms/-5.5ppm +56.9C 2/2Acfts[1h] RF:+50-3.2ppm/+0.76dB/+47.4dB@10km[3859]
#-------------------------------------------------------------------------------------------------------------------#


#-------------------------------------------------------------------------------------------------------------------#
# Build a dummy receiver
#-------------------------------------------------------------------------------------------------------------------#

def bstopsetrec(sock, prt=False, store=False, aprspush=False):			# define on APRS the dummy OGN station
    t = naive_utcnow()       		# get the date
    tme = t.strftime("%H%M%S")
    aprsmsg=config.BSTOPname+">OGNSDR,TCPIP*:/"+tme+"h"+config.BSTOPloc+" BSTOP dummy station \n"
    if prt:
       print("APRSMSG: ", aprsmsg)
    rtn = sock.write(aprsmsg)
    sock.flush()
    if rtn == 0:
       print("Error writing msg:", aprsmsg)
    tempcpu = 0.0
    cpuload =psutil.cpu_percent()/100
    memavail=psutil.virtual_memory().available/(1024*1024)
    memtot=psutil.virtual_memory().total/(1024*1024)
    aprsmsg=config.BSTOPname+">OGNSDR,TCPIP*:>"+tme+"h v0.3.0.BSTOP CPU:"+str(cpuload)+" RAM:"+str(memavail)+"/"+str(memtot)+"MB NTP:0.4ms/-5.4ppm +"+str(tempcpu)+"C\n"
    if prt:
       print("APRSMSG: ", aprsmsg)
    rtn = sock.write(aprsmsg)
    try:
       sock.flush()
    except Exception as e:       
       print ("error on flush: ", e)
    return

#-------------------------------------------------------------------------------------------------------------------#
# find all the fixes since TTIME . Scan all the BSTOP devices for new data
#-------------------------------------------------------------------------------------------------------------------#


def bstopfindpos(ttime, conn, prt=False, store=False, aprspush=True):		# this is the function called by push2ogn.py module

    utime=naive_utcfromtimestamp(ttime)		# convert TTIME to a datetime object
    ttimeformat=utime.strftime("%Y-%m-%dT%H:%M:%SZ")	# and format it in the way that the BSTOP API expects
    #print ("TTT time:", ttime, ttimeformat)
    bstoppos = {"bstoppos": []}			# init the dict
    vitlat = config.FLOGGER_LATITUDE		# get location of the station to calculate the distance to the targets
    vitlon = config.FLOGGER_LONGITUDE
    url    = config.BSTOPhost			# the URL
    url   += "?type=bird&min_confidence=0.8&limit=500"
    url   +='&from='+ttimeformat
    url   +='&geo_lat='+str(vitlat)+'&geo_lon='+str(vitlon)+'&geo_radius='+str(config.BSTOPradius) # add the geofencing parameters
    #print ("URL:", url)
    bstopcnt=0
    now = naive_utcnow()          		# get the UTC time # number of seconds until beginning of the day 1-1-1970
    td = now-datetime(1970, 1, 1)
    bstopnow = int(td.total_seconds()) 		# Unix time - seconds from the epoch
    # print ("BSTOPnow:", bstopnow)
    tracks = bstopgetapidata(url, prt=prt)	# get the JSON data from the BSTOP server
    if len(tracks) <= 0:			# if no data ...
        print("BSTOPfindpos: Empty msg",  bstopnow, now)	# print the data
        return (int(bstopnow), bstopcnt)	# return TTIME for next call

    if prt:
        print("BSTOPfindpos:", len(tracks), bstopnow)
    if prt:
        print("TRACKS len:", len(tracks), json.dumps(tracks, indent=4), "time:", now)  	# convert JSON to string

    						# get all the devices with BSTOP
    bstopaddpos(tracks, bstoppos, ttime, bstopnow, prt=prt)  # find the airplanes since TTIME

    if prt:
        print("BSTOPpos:\n", len (bstoppos), bstoppos, "\n\n")		# print the data
    if store:
        curs = conn.cursor()            	# set the cursor for storing the fixes
        bstopstoreitindb(bstoppos, curs, conn) 	# and store it on the DDBB
    if aprspush:
        #print("Calling aprspush ...\n")
        bstopcnt=bstopaprspush(bstoppos, prt=prt)  	# and push it into the OGN APRS
        					# number of second until beginning of the day of 1-1-1970
    return (int(bstopnow), bstopcnt)		# return TTIME for next call

#-------------------------------------------------------------------------------------------------------------------#

def bstopini(prt=False, aprspush=False):
    print ("BSTOP interface initialized...")
    return
def bstopfinish(count, prt=False, aprspush=False):
    print ("BSTOP interface terminated... Count:", count)
    return
