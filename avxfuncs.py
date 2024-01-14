#!/bin/python3
#-------------------------------------------------------------------------------------------------------------------#
# this functions deals with the data received by the Avionix (AVX) aero-network.com
#-------------------------------------------------------------------------------------------------------------------#
 
import json
import os
import io
from   datetime import datetime
from   geopy.distance import geodesic       	# use the Vincenty algorithm^M
from   parserfuncs import deg2dmslat, deg2dmslon
import urllib.request
import urllib.error
import urllib.parse
import psutil
import ICAO_ranges
import config

#-------------------------------------------------------------------------------------------------------------------#
sample= {					# sample of data received from aero-network
        "uti": 1704480518,
        "dat": "2024-01-05 18:48:38.339",
        "hex": "4ca9d2",
        "fli": "RYR1294",
        "lat": 37.261714612023304,
        "lon": -5.615088421365499,
        "gda": "A",
        "src": "A",
        "alt": 6175,
        "altg": 6450,
        "spd": 249,
        "cat": "A3",
        "squ": "6214",
        "vrt": -1472,
        "trk": 2.0700307,
        "mop": 2,
        "lla": 1,
        "tru": 5662,
        "dbm": -77
    }

#-------------------------------------------------------------------------------------------------------------------#


global _adsbregcache_				# Global ADSB registration information	
_adsbregcache_ = {}
_adsbreg_ = {}


def getadsbreg(icao):			    	# get the registration and model from the ICAO ID
    global _adsbregcache_
    global _adsbreg_
    if not config.ADSBreg:		    	# check if we want to import the huge file ADSBreg
        return(False)
    if len(_adsbreg_) == 0:	    	    	# only import the table if need it
        import ADSBreg			    	# this file is huge
        _adsbreg_ = ADSBreg.ADSBreg	    	# update the global pointer
    if icao in _adsbregcache_:		    	# if ID on the table ???
        return (_adsbregcache_[icao])       	# return model and registration
    else:				    	# if not found, look into the whole registration DB
        if icao in _adsbreg_:
            _adsbregcache_[icao]=_adsbreg_[icao]  # and update the cache for next time
            return (_adsbregcache_[icao])     	# return model and registration
    return False			    	# return FALSE


def getsizeadsbcache():			    	# just return the size of the cache
    return (len(_adsbregcache_))

#-------------------------------------------------------------------------------------------------------------------#

def avxgetapidata(url, prt=False):		# get the data from the aero-network using the API

    req = urllib.request.Request(url)	    	# build the request
    req.add_header("Content-Type", "application/json")
    req.add_header("Content-type", "application/x-www-form-urlencoded")
    r = urllib.request.urlopen(req)         	# open the url resource
    js=r.read().decode('UTF-8')
    j_obj = json.loads(js)                  	# convert to JSON

    if prt:
        print(json.dumps(j_obj, indent=4))
    return j_obj                            	# return the JSON object

#-------------------------------------------------------------------------------------------------------------------#

# extract the data of the last know position from the JSON object

#-------------------------------------------------------------------------------------------------------------------#

def avxaddpos(tracks, avxpos, ttime, avxnow, prt=False):	# build the avxpos from the tracks received

    foundone = False				# assuming nothing found
    for msg in tracks:
        #print ("TRKS:", msg)
        if "fli" in msg:
            flg = msg['fli']
        else:
            print ("AVX No fli")
            continue
        aid = "ICA"+msg['hex'].upper()	    	# aircraft ID
        ttt=msg['uti']		    		# when the aircraft was seen
        					# number of second until beginning of the day
        ts = int(ttt)       		    	# Unix time - seconds from the epoch
        t=datetime.utcfromtimestamp(ts)		# convert to time object the number os seconds from epoc

        if "lon" in msg:
            lon = msg['lon']
        else:
            print ("AVX No lon")
            continue
        if "lat" in msg:
            lat = msg['lat'] 		    	# extract the longitude and latitude
        else:
            print ("AVX No lat")
            continue
        gps = "NO"				# set all the defaults
        extpos = "NO"
        roc=0
        rot=0
        dir=0
        spd=0
        FL=0
        cat=''
        src='ADSB'				# ADSB is the default
        if "vrt" in msg:
                roc = msg['vrt']
        if "spd" in msg:
                spd = msg['spd']
        if "alt" in msg:
                alt = msg["alt"] 		# and the altitude
        else:
                print ("AVX No alt")
                continue
        if "hgt" in msg:			# barometric altitude
                FL = msg['hgt']+alt
                print("FL", FL)
        if "trk" in msg:
            dir = msg['trk']
        if "cat" in msg:
            cat = msg['cat']
        if "src" in msg:			# check the source ADS-B or ADS-L
            if msg['src'] == 'O':
               src='OGN'
            else:
               src='ADSB'

        date = t.strftime("%y%m%d")		# date and time
        tme = t.strftime("%H%M%S")
        # print ("TTT:", t, ts, avxnow, date, tme, msg)
        foundone = True				# mark that we found one

        vitlat = config.FLOGGER_LATITUDE	# get the distance to the dummy station 
        vitlon = config.FLOGGER_LONGITUDE
        distance = geodesic((lat, lon), (vitlat, vitlon)).km            # distance to the station

        pos = {"ICAOID": aid, "date": date, "time": tme, "Lat": lat, "Long": lon, "altitude": alt, "UnitID": aid,
               "dist": distance, "course": dir, "speed": spd, "roc": roc, "rot": rot, "GPS": gps, "extpos": extpos, 
               "flight": flg, "FL" : FL, "source": src, "cat": cat}

        #print "SSS:", ts, ttime, pos
        if alt < int(config.AVXfl) or src == 'OGN':	# filter by source or FL
           avxpos['avxpos'].append(pos)      	# and store it on the dict
        if prt:
            print("avxPOS :", round(lat, 4), round(lon, 4), alt, aid, round(distance, 4), ts, date, tme, flg)

    return(foundone) 			    	# indicate that we added an entry to the dict


#-------------------------------------------------------------------------------------------------------------------#
# Store the data into the DDBB
#-------------------------------------------------------------------------------------------------------------------#

def avxstoreitindb(datafix, curs, conn):   	# store the fix into the database

    import MySQLdb                          	# the SQL data base routines^M
    for fix in datafix['avxpos']:	    	# for each fix on the dict
        id = fix['ICAOID']		    	# extract the information
        dte = fix['date']
        hora = fix['time']
        station = config.location_name
        latitude = fix['Lat']
        longitude = fix['Long']
        altitude = fix['altitude']
        speed = fix['speed']
        course = fix['course']
        roclimb = fix['roc']
        rot = fix['rot']
        sensitivity = 0
        gps = fix['GPS']
        uniqueid = str(fix["UnitID"])
        dist = fix['dist']
        extpos = fix['extpos']
        addcmd = "insert into OGNDATA values ('" + id + "','" + dte + "','" + hora + "','" + station + "'," + \
            str(latitude) + "," + str(longitude) + "," + str(altitude) + "," + str(speed) + "," + \
            str(course) + "," + str(roclimb) + "," + str(rot) + "," + str(sensitivity) + \
            ",'" + gps + "','" + uniqueid + "'," + \
            str(dist) + ",'" + extpos + "', 'avx' ) "
        try:				    # store it on the DDBB
            #print addcmd
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

#-------------------------------------------------------------------------------------------------------------------#
# Push the data received into the OGN APRS
#-------------------------------------------------------------------------------------------------------------------#

def avxaprspush(datafix, conn, prt=False):

    for fix in datafix['avxpos']:	    # for each fix on the dict
        id       = fix['ICAOID']		    # extract the information
        dte      = fix['date']
        hora     = fix['time']
        station  = config.location_name
        latitude = fix['Lat']
        longitude= fix['Long']
        altitude = fix['altitude']
        speed    = fix['speed']
        course   = fix['course']
        roclimb  = fix['roc']
        rot      = fix['rot']
        sensitivity = 0
        gps      = fix['GPS']
        uniqueid = fix["UnitID"]
        uniqueid = '25'+uniqueid[3:]
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
        aprsmsg = id+">OGADSB,qAS,"+config.AVXname+":/" + \
            hora+'h'+lat+"\\"+lon+"^"+ccc+"/"+sss+"/"
        if altitude != None and altitude > 0:
            aprsmsg += "A=%06d" % int(altitude)
        else:
            continue								# ignore the traffic with no altitude
        aprsmsg += " id"+uniqueid+" %+04dfpm " % (int(roclimb))+" "+str(rot)+"rot " 
        if flight != '':
           aprsmsg += "fn"+cat+":"+flight+" "
        regmodel = getadsbreg(id[3:9])
        if FL > 0 :
           aprsmsg += " FL%03d " % int(FL)
        if regmodel:
            reg =regmodel['Reg']
            model=regmodel['Model']
            aprsmsg += "reg"+reg+" model"+model+" \n"
        else:
            aprsmsg += " \n"
        print("APRSMSG: ", aprsmsg[0:-1], "Country:", ICAO_ranges.getcountry(int(id[3:9],16)))
        rtn = config.SOCK_FILE.write(aprsmsg)
        config.SOCK_FILE.flush()
        if rtn == 0:
            print("Error writing msg:", aprsmsg)

    return (True)

#-------------------------------------------------------------------------------------------------------------------#
#LEMD>OGNSDR,TCPIP*,qAC,GLIDERN2:/141436h4030.49NI00338.59W&/A=002280
#LEMD>OGNSDR,TCPIP*,qAC,GLIDERN2:>141436h v0.2.8.RPI-GPU CPU:0.6 RAM:710.8/972.2MB NTP:0.3ms/-5.5ppm +56.9C 2/2Acfts[1h] RF:+50-3.2ppm/+0.76dB/+47.4dB@10km[3859]
#-------------------------------------------------------------------------------------------------------------------#


#-------------------------------------------------------------------------------------------------------------------#
# Build a dummy receiver
#-------------------------------------------------------------------------------------------------------------------#

def avxsetrec(sock, prt=False, store=False, aprspush=False):			# define on APRS the dummy OGN station
    t = datetime.utcnow()       		# get the date
    tme = t.strftime("%H%M%S")
    aprsmsg=config.AVXname+">OGNSDR,TCPIP*:/"+tme+"h"+config.AVXloc+" \n"
    print("APRSMSG: ", aprsmsg)
    rtn = sock.write(aprsmsg)
    sock.flush()
    if rtn == 0:
        print("Error writing msg:", aprsmsg)
    tempcpu = 0.0
    cpuload =psutil.cpu_percent()/100
    memavail=psutil.virtual_memory().available/(1024*1024)
    memtot =psutil.virtual_memory().total/(1024*1024)
    aprsmsg =config.AVXname+">OGNSDR,TCPIP*:>"+tme+"h v0.2.8.AVX CPU:"+str(cpuload)+" RAM:"+str(memavail)+"/"+str(memtot)+"MB NTP:0.4ms/-5.4ppm +"+str(tempcpu)+"C\n"
    print("APRSMSG: ", aprsmsg)
    rtn = sock.write(aprsmsg)
    sock.flush()
    return

#-------------------------------------------------------------------------------------------------------------------#
# find all the fixes since TTIME . Scan all the AVX devices for new data
#-------------------------------------------------------------------------------------------------------------------#


def avxfindpos(ttime, conn, prt=False, store=False, aprspush=False):		# this is the function called by push2ogn.py module

    avxpos = {"avxpos": []}			# init the dict
    url    = config.AVXhost
    tracks = avxgetapidata(url)   		# get the JSON data from the AVX server
    if prt:
        print("TRACKS len:", len(tracks), json.dumps(tracks, indent=4))  	# convert JSON to dictionary
    
    now = datetime.utcnow()          		# get the UTC time # number of seconds until beginning of the day 1-1-1970
    td = now-datetime(1970, 1, 1)
    avxnow = int(td.total_seconds())  		# Unix time - seconds from the epoch
    # print ("AVXnow:", avxnow)
    						# get all the devices with AVX
    avxaddpos(tracks, avxpos, ttime, avxnow, prt=prt)  # find the gliders since TTIME

    if prt:
        print("AVXpos:\n", avxpos)		# print the data
    if store:
        curs = conn.cursor()            	# set the cursor for storing the fixes
        avxstoreitindb(avxpos, curs, conn)  	# and store it on the DDBB
    if aprspush:
        avxaprspush(avxpos, conn, prt=prt)  	# and push it into the OGN APRS
        					# number of second until beginning of the day of 1-1-1970
    return (int(avxnow))			# return TTIME for next call

#-------------------------------------------------------------------------------------------------------------------#
