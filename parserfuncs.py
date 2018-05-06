#
# Parser functions for the OGN APRS applications
#

from libfap import *
from ctypes import *
import urllib2
import json

from datetime import datetime, timedelta
aprssources = {
	"APRS"   : "OGN",
	"OGNSDR" : "OGN",
	"OGFLR"  : "OGN",
	"OGNFLR" : "OGN",
	"OGNTRK" : "OGN",
	"OGNDSX" : "OGN", 
	"OGADSB" : "ADSB",
	"OGNFNT" : "FANE",
	"OGNPAW" : "PAW",
	"OGSPOT" : "SPOT",
	"OGSPID" : "SPID",
	"OGSKYL" : "SKYL",
	"OGLT24" : "LT24",
	"OGCAPT" : "CAPT",
	"OGNAVI" : "NAVI",
	"OGNMAV" : "NMAV"
	}
#
# low lever parser functions
#
def get_longitude(packet):
    try:
        longitude=packet[0].longitude[0]
    except ValueError:
        longitude = -1
    return longitude

def get_latitude(packet):
    try:
        latitude=packet[0].latitude[0]
    except ValueError:
        latitude = -1
    return latitude

def get_altitude(packet):
    try:
        altitude=packet[0].altitude[0]
    except ValueError:
        altitude = -1
    return altitude

def get_daodatum(packet):
    try:
        daodatum=packet[0].dao_datum_byte
    except ValueError:
        daodatum = ' '
    return daodatum

def get_resolution(packet):
    try:
        resolution=packet[0].pos_resolution[0]
    except ValueError:
        resolution = -1 
    return resolution

def get_speed(packet):
    try:
        speed=packet[0].speed[0]
    except ValueError:
        speed = -1
    return speed

def get_course(packet):
    try:
        course=packet[0].course[0]
    except ValueError:
        course = -1
    return course

def get_path(packet):
    try:
        path=packet[0].path[0]
    except ValueError:
        path = -1
    return path

def get_type(packet):
    try:
        type=packet[0].type[0]
    except ValueError:
        type = -1
    return type

def get_dst_callsign(packet):
    try:
        dst_callsign=packet[0].dst_callsign
    except ValueError:
        dst_callsign = ''
    return dst_callsign

def get_destination(packet):
    try:
        destination=packet[0].destination
    except ValueError:
        destination = ''
    return destination

def get_header(packet):
    try:
        header=packet[0].header
    except ValueError:
        header = ''
    return header

def get_otime(packet):
    try:
        itime=packet[0].timestamp[0]
        otime=datetime.utcfromtimestamp(itime)
    except ValueError:
        otime = 0
    return otime

def get_station(data):
        scolon=data.find(':')                   # find the colon
        station=data[data.find("qAS")+4:scolon] # get the station identifier
        station=station.upper()                 # translate to uppercase
        return (station)
########################################################################
def get_source(dstcallsign):
	src=str(dstcallsign)
	if src in aprssources:
		return (aprssources[src])
	else:
		return ("UNKW")
#########################################################################
def gdatal (data, typer):               	# get data on the left
        p=data.find(typer)              	# scan for the type requested
        if p == -1:
                return (" ")
        pb=p
        while (data[pb] != ' ' and data[pb] != '/' and pb >= 0):
                   pb -= 1
        ret=data[pb+1:p]                  	# return the data requested
        return(ret)
########################################################################
def gdatar (data, typer):               	# get data on the  right
        p=data.find(typer)              	# scan for the type requested
        if p == -1:
                return (" ")
        p=p+len(typer)
        pb=p
        max=len(data)-1
        while (pb < max):
                if data[pb] == ' ' or data[pb] == '\n' or data[pb] == '\r' :
                        break
                pb += 1
        ret=data[p:pb]                  	# return the data requested
        return(ret)
########################################################################
#
# geo specifics validations
#

def spanishsta(station):                # return true if is an Spanish station
    if (station) == None:
        return False
    if station[0:2] == 'LE' or 			\
		station[0:5] == 'CREAL'     or 	\
		station[0:4] == 'MORA'      or 	\
		station[0:6] == 'MADRID'    or 	\
		station[0:5] == 'AVILA'     or	\
		station[0:9] == 'ALCAZAREN' or	\
		station[0:7] == 'ANDORRA'   or	\
		station[0:8] == 'STOROSIA'  or	\
		station[0:9] == 'STOROSIAE' or	\
		station[0:9] == 'STOROSIAW' or	\
		station[0:4] == 'PALO'      or	\
		station[0:5] == 'PALOE'     or	\
		station[0:5] == 'PALOW'     or	\
		station[0:8] == 'BOITAULL'  or  \
		station[0:8] == 'LAMOLINA'  or	\
		station[0:8] == 'PORTAINE'  :
        return True
    else:
        return False


def frenchsta(station):                # return true if is an French station
    if (station) == None:
        return False
    if station[0:2] == 'LF'        or \
       station[0:4] == 'BRAM'      or \
       station[0:7] == 'POUBEAU'   or \
       station[0:7] == 'CANOHES'   or \
       station[0:7] == 'ROCAUDE' :
        return True
    else:
        return False
######################################################################### 

def deg2dmslat(dd):  			# convert degrees float in degrees and decimal minutes (to two decimal places)
        dd1 = round(abs(float(dd)), 4)  
        cdeg = int(dd1)  
        mmss = dd1 - float(cdeg)
        minsec = mmss*60.0
        if dd < 0: cdeg = cdeg * -1  
        return "%2.2d%05.2f"%(cdeg,minsec)

def deg2dmslon(dd):  			# convert degrees float in degrees and decimal minutes (to two decimal places)
        dd1 = round(abs(float(dd)), 4)  
        cdeg = int(dd1)  
        mmss = dd1 - float(cdeg)
        minsec = mmss*60.0
        if dd < 0: cdeg = cdeg * -1  
        return "%3.3d%05.2f"%(cdeg,minsec)

def decdeg2dms(dd):			# convert degress float into DDMMSS
	is_positive = dd >= 0
	dd = abs(dd)
	minutes,seconds = divmod(dd*3600,60)
	degrees,minutes = divmod(minutes,60)
	degrees = degrees if is_positive else -degrees
	return (degrees,minutes,seconds)

######################################################################### 
#
# High level APRS parser function
#

def parseraprs(packet_str, msg):
	# args: packet_str the packet stream with the data, msg the dict where to return the parsed data
        # Parse packet using libfap.py into fields to process
        packet = libfap.fap_parseaprs(packet_str, len(packet_str), 0)
        if  len(packet_str) > 0 and packet_str[0] <> "#": # ignore if do data or just the keep alive message
                date=datetime.utcnow() 			# get the date
                callsign=packet[0].src_callsign     	# get the call sign FLARM ID
                id=callsign                         	# id
                longitude    = get_longitude(packet)
                latitude     = get_latitude(packet)
                altitude     = get_altitude(packet)
                resolution   = get_resolution(packet)
                daodatum     = get_daodatum(packet)
                speed        = get_speed(packet)
                course       = get_course(packet)
                path         = get_path(packet)
                type         = get_type(packet)
                dst_callsign = get_dst_callsign(packet)
		source	     = get_source(dst_callsign)
                destination  = get_destination(packet)
                header       = get_header(packet)
                otime        = get_otime(packet)
                data=packet_str
                ix=packet_str.find('>')
                cc= packet_str[0:ix]
                if path == 'TCPIP*':                    # handle the TCPIP
                        if cc.isupper():
                                id=callsign
                        else:
                                id=cc
                        station=id
                        p=data.find(' v0.')             # scan for the body of the APRS message
                        status=data[p+1:p+254].rstrip() # status information
                        tempC=gdatal(data, "C ")        # temperature
                        if tempC == ' ':
                                temp = -99.9		# -99 means no temp declared
                        else:
                                temp=float(tempC)	# temperature
                        version=gdatar(data, " v0.")    # version
                        cpus=gdatar(data,"CPU:")        # CPU usagea
                        cpu=0.0
                        if (cpus != "" and cpus != " " and cpus[0] != "-" and cpus[0:3] != "0.-"):
                                cpu=float(cpus)         # CPU usage
			rft=gdatar(data,"RF:").rstrip()	# look for the RF data
                        if len(rft)>64:
                                rft=rft[0:64]           # sanity check
                        rf=gdatal(rft, "dB").rstrip()   # RF noise
                        irf=rft.find  ('dB')
			rft=rf[0:irf]			# delete the extra inforomation
                        msg['id']=id			# return the parsed data into the dict
                        msg['path']=path
                        msg['station']=station
                        msg['type']=type
                        msg['otime']=otime
                        msg['latitude']=latitude
                        msg['longitude']=longitude
                        msg['altitude']=altitude
                        msg['version']=version
                        msg['cpu']=cpu
                        msg['temp']=temp
                        msg['rf']=rf
                        msg['status']=status
                        msg['source']=source
                        return (msg)
		if path != 'qAS':			# we dealt already with the other paths !!!
			#print "Path:", path, packet_str
			if path == -1:
				return -1
                if path == 'qAS' or path == 'RELAY*' or path[0:3] == "OGN" or path[0:3] == "FLR" or path[0:3] == "RND":   # if std records
                        station=get_station(packet_str) # get the station ID
		else:
			station = "Unkown"		# always one station

		if type != 8:				# if not status report
			if otime != 0:			# if time is provided ???
                		hora=otime.strftime("%H%M%S")	# the aprs msgs has the time in this case
			else:	
                		p1=data.find(':/')+2    # scan for the body of the APRS message
				if data[p1+6] == 'h':	# case of HHMMSS
                			hora=data[p1:p1+6]      # get the GPS time in UTC
				elif data[p1+6] == 'z':	# case of DDHHMM
                			hora=data[p1+2:p1+6]+'00'  # get the GPS time in UTC, ignore date
				else:
                			hora=date.strftime("%H%M%S")	# the aprs msgs has not time in this case
		else:					# the case of aprs status report
			if otime == 0:			# if not time from the packet
                		hora=date.strftime("%H%M%S")	# the aprs msgs has not time in this case
			else:
                		hora=otime.strftime("%H%M%S")	# the aprs msgs has the time in this case

               	p2=data.find('/A=')+3                   # scan for the altitude on the body of the message
                if  data[p2+7] == '!':                  # get the unique id
                        extpos       = data[p2+7:p2+12] # get extended position indicator
                else:
                        extpos=' '

                p3=data.find(' id')                     # scan for uniqueid info
                if p3 != -1:
			uniqueid     = "id"+gdatar(data,"id") # get the unique id
		else:
			uniqueid     = ' '		# no unique ID
			
                roclimb      = gdatal(data,"fpm ")      # get the rate of climb
                if roclimb == ' ':				# if no rot provided
                        roclimb=0
                rot          = gdatal(data,"rot")       # get the rate of turn
                if rot == ' ':				# if no rot provided
                        rot=0
                sensitivity  = gdatal(data,"dB ")       # get the sensitivity
                if sensitivity == ' ':			# if no sensitivity provided
                        sensitivity = 0
                p6=data.find('gps')                     # scan for gps info
                if p6 != -1:
                        gps      = gdatar(data, "gps")  # get the gpsdata 
                else:
                	p6=data.find(' GPS')            # scan for gps info
                	if p6 != -1:
                        	gps      = "GPS"	# generic GPS mark
                	else:
                        	gps      = "NO"		# no GPS data
                dte=date.strftime("%y%m%d")		# the aprs msgs has not date

                msg['path']=path			# return the data parsed in the dict
                msg['idflarm']=id
                msg['id']=id
                msg['date']=dte
                msg['time']=hora
                msg['station']=station
                msg['latitude']=latitude
                msg['longitude']=longitude
                msg['altitude']=altitude
                msg['resolution']=resolution
                msg['daodatum']=daodatum
                msg['speed']=speed
                msg['course']=course
                msg['roclimb']=roclimb
                msg['rot']=rot
                msg['sensitivity']=sensitivity
                msg['gps']=gps
                msg['uniqueid']=uniqueid
                msg['extpos']=extpos
                msg['type']=type
                msg['otime']=otime
                msg['source']=source
		if type == 8:
                        p=data.find(':>')             	# scan for the body of the APRS message
                        status=data[p+2:p+254].rstrip() # status information
                        msg['status']=status
		libfap.fap_free(packet)			# just in case free memory, to avoid memory leaks.
                return(msg)
        else:
                return -1				# if length ZERO or just the keep alive
#
########################################################################

def SRSSgetapidata(url):                        # get the data from the API server

        req = urllib2.Request(url)              # buil the request
        req.add_header("Content-Type","application/json")
        req.add_header("Content-type", "application/x-www-form-urlencoded")
        r = urllib2.urlopen(req)                # open the url resource
        j_obj = json.load(r)                    # convert to JSON
        return j_obj                            # return the JSON object
def SRSSgetjsondata(lat, lon, object='sunset', prt=False):

        ts=0                                    # init the return time since epoch
        url="http://api.sunrise-sunset.org/json?lat="+lat+"&lng="+lon+"&formatted=0"
        jsondata=SRSSgetapidata(url)            # get the data from the web
        #print jsondata
        if prt:                                 # if print requested
                print json.dumps(jsondata, indent=4)
        if jsondata['status'] == "OK":          # only if results are OK
                results=jsondata["results"]     # get the reults part
                timeref=results[object]         # get the object that we need
                #print timeref
                ttt=datetime.strptime(timeref,"%Y-%m-%dT%H:%M:%S+00:00") # convert to time format
                td=ttt-datetime(1970,1,1)       # number of second until beginning of the day
                ts=int(td.total_seconds())      # Unix time - seconds from the epoch
        return (ts)                             # return it

#########################################################################
def alive(app, first='no'):

        alivename=app+".alive"
        if (first == 'yes'):
                alivefile = open (alivename, 'w') # create a file just to mark that we are alive
        else:
                alivefile = open (alivename, 'a') # append a file just to mark that we are alive
        local_time = datetime.now()
        alivetime = local_time.strftime("%y-%m-%d %H:%M:%S")
        alivefile.write(alivetime+"\n") # write the time as control
        alivefile.close()               # close the alive file
	return()
#########################################################################
#import datetime
