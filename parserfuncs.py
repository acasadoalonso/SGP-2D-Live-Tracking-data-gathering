import datetime
from libfap import *
from ctypes import *
from datetime import datetime
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
#######---------------------------------------------------------------------------------------------------------

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
def gdatal (data, typer):               # get data on the left
        p=data.find(typer)              # scan for the type requested
        if p == -1:
                return (" ")
        pb=p
        while (data[pb] != ' '):
                   pb -= 1
        ret=data[pb:p]                  # return the data requested
        return(ret)
########################################################################
def gdatar (data, typer):               # get data on the  right
        p=data.find(typer)              # scan for the type requested
        if p == -1:
                return (" ")
        p=p+len(typer)
        pb=p
        max=len(data)-1
        while (pb < max):
                if data[pb] == ' ' or data[pb] == '\n' or data[pb] == '\r':
                        break
                pb += 1
        ret=data[p:pb]                  # return the data requested
        return(ret)
########################################################################

def parseraprs(packet_str, msg):
        # Parse packet using libfap.py into fields to process, eg:
        packet = libfap.fap_parseaprs(packet_str, len(packet_str), 0)
        if  len(packet_str) > 0 and packet_str[0] <> "#":
                callsign=packet[0].src_callsign     # get the call sign FLARM ID
                id=callsign                         # id
                longitude = get_longitude(packet)
                latitude  = get_latitude(packet)
                altitude  = get_altitude(packet)
                speed     = get_speed(packet)
                course    = get_course(packet)
                path      = get_path(packet)
                type      = get_type(packet)
                dst_callsign = get_dst_callsign(packet)
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
                        status=data[p+1:p+80].rstrip()  # status information
                        tempC=gdatal(data, "C ")        # temperature
                        if tempC == ' ':
                                temp = -99.9
                        else:
                                temp=float(tempC)
                        version=gdatar(data, " v0.")    # version
                        cpus=gdatar(data,"CPU:")        # CPU usagea

                        #print "CPU:", cpus, id
                        cpu=0.0
                        if (cpus != "" and cpus != " " and cpus[0] != "-" and cpus[0:3] != "0.-"):
                                cpu=float(cpus)         # CPU usage
                        rf=gdatar(data, "RF:").rstrip() # RF noise
                        if len(rf)>20:
                                rf=rf[0:20]             # sanity check
                        msg['id']=id
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
                        return (msg)
                if path == 'qAS' or path == 'RELAY*':                       # if std records
                        station=get_station(packet_str)
                #
                p1=data.find(':/')+2                    # scan for the body of the APRS message
                hora=data[p1:p1+6]                      # get the GPS time in UTC
                p2=data.find('/A=')+3                   # scan for the altitude on the body of the message
                if  data[p2+7] == '!':                  # get the unique id
                        uniqueid     = data[p2+13:p2+23] # get the unique id
                        extpos       = data[p2+7:p2+12] # get extended position indicator
                else:
                        uniqueid     = data[p2+7:p2+17] # get the unique id
                        extpos=' '
                roclimb      = gdatal(data,"fpm ")      # get the rate of climb
                rot          = gdatal(data,"rot")       # get the rate of turn
                if rot == ' ':
                        rot=0
                sensitivity  = gdatal(data,"dB ")       # get the sensitivity
                if sensitivity == ' ':
                        sensitivity = 0
                p6=data.find('gps')                     # scan for gps info
                if p6 != -1:
                        gps      = data[p6+3:p6+6]      # get the gps
                else:
                        gps      = "NO"
                date=datetime.utcnow()         # get the date
                dte=date.strftime("%y%m%d")

                msg['path']=path
                msg['idflarm']=id
                msg['id']=id
                msg['date']=dte
                msg['time']=hora
                msg['station']=station
                msg['latitude']=latitude
                msg['longitude']=longitude
                msg['altitude']=altitude
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
                return(msg)
        else:
                return -1
#
########################################################################


