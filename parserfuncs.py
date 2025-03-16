#!/usr/bin/python3
#
# Parser functions for the OGN APRS applications
#

import urllib.request
import urllib.error
import urllib.parse
import json
import os
import sys
import atexit
import socket
import airportsdata

from ogn.parser import parse
from datetime import datetime, timezone
from dtfuncs  import naive_utcnow, naive_utcfromtimestamp

# --------------------------------------------------------------------------
aprssources = {			# sources based on the APRS TOCALL
    "APRS"  : "OGN",		# old tocall
    "OGNSDR": "OGN",		# station Sofware defined radio
    "OGFLR" : "OGN",		# Flarm
    "OGNFLR": "OGN",		# Flarm
    "OGFLR6": "OGN",		# Flarm
    "OGFLR7": "OGN",		# Flarm
    "OGNTRK": "OGN",		# OGN Tracker
    "OGNDSX": "OGN",		# old DSX
    "OGNDVS": "WTX",		# Weather stations
    "OGNTTN": "TTN",		# the things LoRaWan network
    "OGTTN2": "TTN",		# the things LoRaWan network V2 - deprecated
    "OGTTN3": "TTN",		# the things LoRaWan network V3 - cumunity edition
    "OGNHEL": "HELI",		# helium LoRaWan
    "OGOBS" : "OBS",		# OBS LoRaWan
    "OGADSB": "ADSB",		# ADSB
    "ONADSB": "ADSB",		# ADSB
    "OGADSL": "ADSL",		# ADS-L
    "OGNFNT": "FANE",		# FANET
    "OGFNT" : "FANE",		# FANET
    "OGNPAW": "PAW",		# PilotAware
    "OGPAW" : "PAW",		# PilotAware
    "OGSPOT": "SPOT",		# SPOT
    "OGINRE": "INREACH",        # Garmin InReach
    "OGFLYM": "FLYM",		# FlyMaster
    "OGSPID": "SPID",		# spider
    "OGSKYL": "SKYL",		# Sky lines (XCsoar)
    "OGLT24": "LT24",		# LiveTrack 24
    "OGCAPT": "CAPT",		# capture
    "OGNAVI": "NAVI",		# NAVITER
    "OGNSKY": "SKYS",		# Sky Safe
    "OGNAVZ": "AVIA",		# AVIAZE
    "OGNMTK": "MTRK",		# Microtrack
    "OGNXCG": "XCG",		# Cross Country Guide
    "OGNMAV": "NMAV",		# MAV link
    "OGNEMO": "NEMO",		# Canadian NEMO
    "OGNFNO": "NEURONE",	# Neurone
    "OGNSXR": "OGNB",	   	# OGNbase
    "OGAIRM": "AIRM",	   	# Airmate
    "OGNMYC": "MYC",	   	# My cloud base
    "FXCAPP": "FXC",	   	# FXC 
    "OGMSHT": "MSHT",	   	# Metashtic
    "OGNDLY": "DLYM"		# Delayed fixes (IGC mandated)
}
# --------------------------------------------------------------------------
aprssymtypes=[
    "/z",                   # 0 = ?
    "/'",                   # 1 = (moto-)glider (most frequent)
    "/'",                   # 2 = tow plane (often)
    "/X",                   # 3 = helicopter (often)
    "/g",                   # 4 = parachute (rare but seen - often mixed with drop plane)
    "\\^",                  # 5 = drop plane (seen)
    "/_",                   # 6 = MicroLight (FANET) (rare but seen)
    "/g",                   # 7 = para-glider (rare but seen)
    "\\^",                  # 8 = powered aircraft (often)
    "/^",                   # 9 = jet aircraft (rare but seen)
    "/z",                   # A = UFO (people set for fun)
    "/O",                   # B = balloon (seen once)
    "/O",                   # C = airship (seen once)
    "/'",                   # D = UAV (drones, can become very common)
    "/z",                   # E = ground support (ground vehicles at airfields)
    "\\n"                   # F = static object (ground relay ?)
]
# --------------------------------------------------------------------------
aprstypes=[
    "Unknown",              # 0 = ?
    "Glider",               # 1 = (moto-)glider (most frequent)
    "Plane",                # 2 = tow plane (often)
    "Helicopter",           # 3 = helicopter (often)
    "ParaGlider",           # 7 = para-glider (rare but seen)
    "DropPlane",            # 5 = drop plane (seen)
    "MicroLight",           # 6 = MicroLight / hang-glider (rare but seen)
    "Parachute",            # 4 = parachute (rare but seen - often mixed with drop plane)
    "PowerAircraft",        # 8 = powered aircraft (often)
    "Jet",                  # 9 = jet aircraft (rare but seen)
    "UFO",                  # A = UFO (people set for fun)
    "Balloon",              # B = balloon (seen once)
    "Airship",              # C = airship (seen once)
    "Drone",                # D = UAV (drones, can become very common)
    "GroundVehicle",        # E = ground support (ground vehicles at airfields)
    "GroundStation"         # F = static object (ground relay ?)
]
# --------------------------------------------------------------------------
def isfloat(s):
    return (s.replace('.','',1).isdigit())

def get_aircraft_type(sym1, sym2):      # return the aircraft type based on the symbol table

    sym=sym1 +sym2
    idx=0
    while idx < len(aprssymtypes):
        if sym == aprssymtypes[idx]:
            return (aprstypes[idx])
        idx += 1
    # deal with the NEMO for the time being
    if sym1 == 'I' and sym2 == '&':
        return ("Station")
    print (">>> Unknown or Wrong Acft Type", sym1, sym2, "<<<", file=sys.stderr)
    return ("UNKNOWN")


def isFloat(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

#
# low lever parser functions
#


def get_longitude(packet):
    if 'longitude' in packet:
        longitude = packet['longitude']
    else:
        longitude = -1
    return longitude


def get_latitude(packet):
    if 'latitude' in packet:
        latitude = packet['latitude']
    else:
        latitude = -1
    return latitude


def get_altitude(packet):
    if 'altitude' in packet and packet['altitude'] is not None:
        altitude = packet['altitude']
    else:
        altitude = -1
    return altitude

def getinfoairport(icao):
    airports = airportsdata.load()  # key is the ICAO identifier (the default)
    if icao in airports:
       return(airports[icao])
    else:
       return (None)

# def get_daodatum(packet):
    # try:
    # daodatum = packet[0].dao_datum_byte
    # except ValueError:
    # daodatum = ' '
    # return daodatum


# def get_resolution(packet):
    # try:
    # resolution = packet[0].pos_resolution[0]
    # except ValueError:
    # resolution = -1
    # return resolution


def get_speed(packet):
    if 'ground_speed' in packet:
        speed = packet['ground_speed']
    else:
        speed = -1
    return speed


def get_course(packet):
    if 'track' in packet:
        course = packet['track']
    else:
        course = -1
    return course


def get_relay(packet):
    if 'relay' in packet:
        relay = packet['relay']
        if relay is None:
            relay="NORELAY"
    else:
        relay = "NORELAY"
    return relay


def get_path(packet):
    if 'beacon_type' in packet:
        path = packet['beacon_type']
    else:
        path = "NOPATH"
    return path


def get_beacontype(packet):
    if 'beacon_type' in packet:
        path = packet['beacon_type']
    else:
        path = "NOPATH"
    return path


def get_aprstype(packet):
    if 'aprs_type' in packet:
        aprstype = packet['aprs_type']
    else:
        aprstype = ''
    return aprstype


def get_dst_callsign(packet):
    if 'dstcall' in packet:
        dst_callsign = packet['dstcall']
    else:
        dst_callsign = ''
    return dst_callsign


def get_destination(packet):
    if 'receiver_name' in packet:
        destination = packet['receiver_name']
    else:
        destination = ''
    return destination


def get_header(packet):
    if 'aprs_type' in packet:
        header = packet['aprs_type']
    else:
        header = ''
    return header


def get_otime(packet):
    if 'timestamp' in packet:
        otime = packet['timestamp']
    else:
        otime = datetime.naive_utcfromtimestamp(0)
    return otime


def get_station(packet):
    if 'receiver_name' in packet:
        station = packet['receiver_name']
        station = station.upper()                 # translate to uppercase
    else:
        station=''
    return (station)
# #######################################################################


def get_source(dstcallsign):
    src = str(dstcallsign)
    if src in aprssources:
        return (aprssources[src])
    print(">>> Unknown SOURCE:", src, "<<<", file=sys.stderr)
    return ("UNKW")
# ########################################################################


def gdatal(data, typer):               	        # get data on the left
    p = data.find(typer)              	        # scan for the type requested
    if p == -1:
        return (" ")
    pb = p
    while (data[pb] != ' ' and data[pb] != '/' and pb >= 0):
        pb -= 1
    ret = data[pb +1:p]                  	# return the data requested
    return(ret)
# #######################################################################
def gdatall(data, typer):              	        # get data on the left
    p = data.find(typer)              	        # scan for the type requested
    if p == -1:
        return (" ")
    pb = p
    while (data[pb] != ' ' and pb >= 0):
        pb -= 1
    ret = data[pb +1:p]                  	# return the data requested
    return(ret)
# #######################################################################


def gdatar(data, typer):               	# get data on the  right
    p = data.find(typer)              	# scan for the type requested
    if p == -1:
        return (" ")
    p = p +len(typer)
    pb = p
    maxd = len(data) -1
    while (pb < maxd):
        if data[pb] == ' ' or data[pb] == '\n' or data[pb] == '\r':
            pb += 1
            break
        pb += 1
    ret = data[p:pb]                 	# return the data requested
    return(ret)
# #######################################################################
#
# geo specifics validations
#


def spanishsta(station):                # return true if is an Spanish station
    
    import ksta				# list of know stations
    if (station) is None:
        return False
    if station[0:2] == 'LE' or station[0:2] == "LP" or	\
            station[0:5] == 'CREAL'     or 	\
            station[0:5] == 'CReal'     or 	\
            station[0:4] == 'MORA'      or 	\
            station[0:4] == 'LUGO'      or 	\
            station[0:6] == 'MADRID'    or 	\
            station[0:8] == 'LEMDadsb'  or 	\
            station[0:7] == 'TTN2OGN'   or 	\
            station[0:6] == 'VIADOS'    or	\
            station[0:6] == 'Viados'    or	\
            station[0:9] == 'ALCAZAREN' or	\
            station[0:7] == 'ANDORRA'   or	\
            station[0:9] == 'STOROE'    or	\
            station[0:9] == 'STOROW'    or	\
            station[0:5] == 'PALOE'     or	\
            station[0:5] == 'PALOW'     or	\
            station[0:8] == 'BOITAULL'  or  	\
            station[0:6] == 'TAULL2'    or  	\
            station[0:6] == 'Taull2'    or  	\
            station[0:8] == 'LAMOLINA'  or	\
            station[0:6] == 'MATARO'    or	\
            station[0:6] == 'CEREJA'    or	\
            station[0:9] == 'FLYMASTER' or	\
            station[0:4] == 'SPOT'      or	\
            station[0:6] == 'PWLERM'    or	\
            station[0:9] == 'CASTEJONS' or	\
            station[0:9] == 'BELAVISTA' or	\
            station[0:9] == 'ALDEASEST' or	\
            station[0:9] == 'AldeaSEst' or	\
            station[0:9] == 'MADRUEDAN' or	\
            station[0:9] == 'Madruedan' or	\
            station[0:9] == 'PCARRASCO' or	\
            station[0:9] == 'PCarrasco' or	\
            station[0:8] == 'SMUERDO'   or	\
            station[0:8] == 'SMuerdo'   or	\
            station[0:9] == 'SSALVADOR' or	\
            station[0:9] == 'SSalvador' or	\
            station[0:9] == 'RinconCie' or	\
            station[0:8] == 'PORTAINE'  or      \
            station[0:8] == 'ALJARAFE'  or      \
            station[0:9] == 'Pagalajar' or      \
            station[0:6] == 'Aguila'    or      \
            station[0:6] == 'LaRaca'    or      \
            station[0:6] == 'Fiscal'    or      \
            station[0:4] == 'LUGA'      or      \
            station[0:5] == 'Avila'     or      \
            station[0:5] == 'AVILA'     or      \
            station[0:7] == 'Montsec'   or      \
            station[0:7] == 'MONTSEC'   or      \
            station[0:9] == 'TordlOrri' or      \
            station[0:9] == 'TORDLORRI' or      \
            station[0:8] == 'Baqueira'  or      \
            station[0:8] == 'BAQUEIRA'  or      \
            station in ksta.ksta and station[0:2] != 'LF' and station != 'Roquefort' :
        return True
    return False


def frenchsta(station):                # return true if is an French station
    if (station) is None:
        return False
    if station[0:2] == 'LF' or \
       station[0:4] == 'BRAM' or \
       station[0:7] == 'POUBEAU' or \
       station[0:7] == 'CANOHES' or \
       station[0:7] == 'FONTROMEU' or \
       station[0:7] == 'ROCAUDE':
        return True
    return False
# ########################################################################



def dao(dd):                           	# return the 3 digit of the decimal minutes
    dd1 = abs(float(dd))
    cdeg = int(dd1)
    mmss = dd1 - float(cdeg)
    minsec = round(mmss *60.0,4)
    decmin= "%06.3f" % (minsec)
    return decmin[5]			# just return the last digit


def deg2dmslat(dd):                     # convert degrees float in degrees and decimal minutes (to two decimal places)
    dd1 = abs(float(dd))
    cdeg = int(dd1)
    mmss = dd1 - float(cdeg)
    minsec = round(mmss *60.0,4)
    decmin= "%2.2d%06.3f" % (cdeg, minsec)
    return decmin[0:7]


def deg2dmslon(dd):                     # convert degrees float in degrees and decimal minutes (to two decimal places)
    dd1 = abs(float(dd))
    cdeg = int(dd1)
    mmss = dd1 - float(cdeg)
    minsec = round(mmss *60.0,4)
    decmin= "%3.3d%06.3f" % (cdeg, minsec)
    return decmin[0:8]

def decdeg2dms(dd):			# convert degress float into DDMMSS
    is_positive = dd >= 0
    dd = abs(dd)
    minutes, seconds = divmod(dd *3600, 60)
    degrees, minutes = divmod(minutes, 60)
    degrees = degrees if is_positive else -degrees
    return (degrees, minutes, seconds)

# ########################################################################
#
# High level APRS parser function
#


def parseraprs(packet_str, msg):
    # args: packet_str the packet stream with the data, msg the dict where to return the parsed data
    # patch #######
    try:
        packet = parse(packet_str)
    except:
        return -1
    # print (">>>Packet:", packet, file=sys.stderr)
    # ignore if do data or just the keep alive message
    if len(packet_str) > 0 and packet_str[0] != "#":
        date = naive_utcnow() 			# get the date
        if 'name' in packet:
            callsign = packet['name']               	# get the call sign FLARM ID or station name
            gid = callsign                  	        # id
        else:
            return -1
        longitude = get_longitude(packet)
        latitude  = get_latitude(packet)
        altitude  = get_altitude(packet)
        # resolution = get_resolution(packet)
        # daodatum = get_daodatum(packet)
        speed     = get_speed(packet)                   # ground_speed
        course    = get_course(packet)                  # track
        path      = get_path(packet)                    # aprs_receiver, tracker, aprs_aircraft
        relay     = get_relay(packet)                   # relay TCPIP, OGN123456*, RELAY* , OGNDLY*
        aprstype  = get_aprstype(packet)                # aprs type: status or position
        dst_callsign = get_dst_callsign(packet)         # APRS, OGNTRK,
        source    = get_source(dst_callsign)            # convert to SOURCE
        destination = get_destination(packet)           # receiver name
        # header = get_header(packet)                   # aprs type
        otime     = get_otime(packet)                   # msg time
        data      = packet_str
        ix = packet_str.find('>')
        cc = packet_str[0:ix]
        ix = packet_str.find(':')     # look for the message type
        # check if it is position report or status report
        msgtype = packet_str[ix +1:ix +2]
        if msgtype != '>' and msgtype != '/':   	# only status or location messages
            print("MMM>>>", aprstype, data, file=sys.stderr)
# ===================================================================================================== #
        # if TCPIP records            			The the WX
        if dst_callsign == 'OGNDVS':			# if it is a wether station ??
           windspeed = gdatall(data, 'kt ')
           temp      = gdatal (data, 'F ')
           humidity  = gdatal (data, '% ')
           rain      = gdatal (data, 'mm/h')
           msg['id']       = gid	        	# return the parsed data into the dict
           msg['path']     = path
           msg['relay']    = relay
           msg['station']  = gid
           msg['aprstype'] = aprstype
           msg['otime']    = otime
           msg['windspeed']= windspeed
           msg['temp']     = temp
           msg['humidity'] = humidity
           msg['rain']     = rain
           msg['source']   = 'WTX'
           return (msg)
               
# ===================================================================================================== #
        # if TCPIP records            			The station records
        if (path == 'aprs_receiver' or path == 'receiver') and (msgtype == '>' or msgtype == '/'):  # handle the TCPIP
            if cc.isupper():
                gid = callsign
            else:
                gid = cc
            station = gid
	
            # scan for the body of the APRS message
            p = data.find(' v0.')                       # the comment side
            if aprstype == 'status':
                status = packet['comment'].rstrip()     # status informationa
            else:
                status = " "
            if 'cpu_temp' in packet:
                temp=packet['cpu_temp']
            else:
                tempC = gdatal(data, "C ")              # temperature
                if tempC == ' ':
                    temp = -99.9		        # -99 means no temp declared
                else:
                    if isFloat(tempC):                  # check for numeric, just in case
                        temp = float(tempC)              # temperature
                    else:
                        temp = -99.9
            if 'version' in packet:
                version=packet['version']               # firmware version
            else:
                version=''
            if 'cpu_load' in packet:
                cpu=packet['cpu_load']
            else:
                cpus = gdatar(data, "CPU:")             # CPU usage
                cpu = 0.0
                if (cpus != "" and cpus != " " and cpus[0] != "-" and cpus[0:3] != "0.-"):
                    cpu = float(cpus)                   # CPU usage
            if 'rec_input_noise' in packet:
                rf=packet['rec_input_noise']
            else:
                rft = gdatar(data, "RF:").rstrip()      # look for the RF data
                if len(rft) > 64:
                    rft = rft[0:64]                     # sanity check
                rf = gdatal(rft, "dB").rstrip()         # RF noise
                irf = rft.find('dB')
                rft = rf[0:irf]			        # delete the extra inforomation
            if 'platform' in packet:
                msg['platform'] = packet['platform']
            else:
                msg['platform'] = ''
            if 'free_ram' in packet:
                msg['free_ram'] = packet['free_ram']
            else:
                msg['free_ram'] = ''
            if 'total_ram' in packet:
                msg['total_ram'] = packet['total_ram']
            else:
                msg['total_ram'] = ''
            if 'ntp_error' in packet:
                msg['ntp_error'] = packet['ntp_error']
            else:
                msg['ntp_error'] = ''
            msg['id'] = gid	        # return the parsed data into the dict
            msg['path'] = path
            msg['relay'] = relay
            msg['station'] = station
            msg['aprstype'] = aprstype
            msg['otime'] = otime
            msg['latitude'] = latitude
            msg['longitude'] = longitude
            msg['altitude'] = altitude
            msg['version'] = version
            msg['cpu'] = cpu
            msg['temp'] = temp
            msg['rf'] = rf
            msg['status'] = status
            msg['source'] = source
            return (msg)
# ===================================================================================================== #
        # if std records            aprs_aircraft or tracker
        station = destination

        if packet['aprs_type'] != 'status':     # if not status report
            if otime != 0:			# if time is provided ???
                # the aprs msgs has the time in this case
                hora = otime.strftime("%H%M%S")
            else:
                # scan for the body of the APRS message
                p1 = data.find(':/') +2
                if data[p1 +6] == 'h':  # case of HHMMSS
                    hora = data[p1:p1 +6]      # get the GPS time in UTC
                elif data[p1 +6] == 'z':  # case of DDHHMM
                    # get the GPS time in UTC, ignore date
                    hora = data[p1 +2:p1 +6] +'00'
                else:
                    # the aprs msgs has not time in this case
                    hora = date.strftime("%H%M%S")
        else:					# the case of aprs status report
            if otime == 0:			# if not time from the packet
                # the aprs msgs has not time in this case
                hora = date.strftime("%H%M%S")
            else:
                # the aprs msgs has the time in this case
                hora = otime.strftime("%H%M%S")

        # scan for the altitude on the body of the message
        p2 = data.find('/A=') +3
        if len(data) > (p2 + 7) and data[p2 +7] == '!':                  # get the unique id
            extpos = data[p2 +7:p2 +12]           # get extended position indicator
        else:
            extpos = ' '

        p3 = data.find(' id')                   # scan for uniqueid info
        if p3 != -1:
            uniqueid = "id" +gdatar(data, "id")  # get the unique id
        else:
            uniqueid = ' '		        # no unique ID
        if len(uniqueid) > 15:
            uniqueid = ' '		        # no unique ID

        roclimb = gdatal(data, "fpm ")          # get the rate of climb
        if roclimb == ' ' or not isfloat(roclimb):	# if no rot provided
            roclimb = 0
        rot = gdatal(data, "rot")               # get the rate of turn
        if rot == ' ' or not isfloat(rot):	# if no rot provided
            rot = 0
        sensitivity = gdatal(data, "dB ")       # get the sensitivity
        if sensitivity == ' ' or not isfloat(sensitivity):	# if no sensitivity provided
            sensitivity = 0
        p6 = data.find('gps')                   # scan for gps info
        if p6 != -1:
            gps = gdatar(data, "gps")  		# get the gpsdata
        else:
            p6 = data.find(' GPS')            	# scan for gps info
            if p6 != -1:
                gps = "GPS"  			# generic GPS mark
            else:
                gps = "NO"			# no GPS data
        if len(gps) > 6:
            gps=gps[0:6]			# max 6 chars
        if len(station) > 9:
            station=station[0:9]		# max 9 chars
        if len(source) > 8:
            source=source[0:8]		# max 8 chars

        dte = date.strftime("%y%m%d")		# the aprs msgs has not date

        msg['path'] = path			# return the data parsed in the dict
        msg['relay'] = relay			# return the data parsed in the dict
        msg['idflarm'] = gid
        msg['id'] = gid
        msg['date'] = dte
        msg['time'] = hora
        msg['station'] = station
        msg['latitude'] = latitude
        msg['longitude'] = longitude
        msg['altitude'] = altitude
        # msg['resolution'] = resolution
        # msg['daodatum'] = daodatum
        msg['speed'] = speed
        msg['course'] = course
        msg['roclimb'] = roclimb
        msg['rot'] = rot
        msg['sensitivity'] = sensitivity
        msg['gps'] = gps
        msg['uniqueid'] = uniqueid
        msg['extpos'] = extpos
        msg['aprstype'] = aprstype
        msg['otime'] = otime
        msg['source'] = source
        if aprstype == 'status':
            # scan for the body of the APRS message
            p = data.find(':>')
            status = data[p +2:p +254].rstrip()  # status information
            msg['status'] = status
        else:
            msg['status'] = "NOSTATUS"
        if station == "DLY2APRS":
            ix = data.find('>')
            if data[ix +1:ix +7] == "OGNTRK":
                idx=data[ix +8:].find(',')
                nsta=data[ix +8:ix +idx +8]
                # print("SSS:", nsta, ix, idx, data, file=sys.stderr)
                msg['station']=nsta
                msg['source']="DLYM"
                msg['relay']="OGNDLY*"

        if 'symboltable' in packet and 'symbolcode' in packet:
            msg['acfttype']=get_aircraft_type(packet['symboltable'], packet['symbolcode'])
        if source == "ADSB":
            fn =gdatar(data, " fn")
            reg =gdatar(data, " reg")
            model=gdatar(data, " model")
            if fn != ' ':
                msg['fn']=fn
            if reg != ' ':
                msg['reg']=reg
            if model != ' ':
                msg['model']=model

        return(msg)
    else:
        return -1				# if length ZERO or just the keep alive
#
# #######################################################################


def SRSSgetapidata(url):                    # get the data from the API server

    req = urllib.request.Request(url)       # buil the request
    req.add_header("Content-Type", "application/json")
    req.add_header("Content-type", "application/x-www-form-urlencoded")
    r = urllib.request.urlopen(req)         # open the url resource
    js=r.read().decode('UTF-8')
    j_obj = json.loads(js)                  # convert to JSON
    return j_obj                            # return the JSON object


def SRSSgetjsondata(lat, lon, obj='sunset', prt=False):

    ts = 0                                  # init the return time since epoch
    url = "http://api.sunrise-sunset.org/json?lat=" +lat +"&lng=" +lon +"&formatted=0"
    jsondata = SRSSgetapidata(url)          # get the data from the web
    # print jsondata
    if prt:                                 # if print requested
        print(json.dumps(jsondata, indent=4))
    if jsondata['status'] == "OK":          # only if results are OK
        results = jsondata["results"]       # get the reults part
        timeref = results[obj]         	    # get the object that we need
        print(jsondata['status'], obj, timeref)
        # convert to time format
        ttt = datetime.strptime(timeref, "%Y-%m-%dT%H:%M:%S+00:00")
        # number of second until beginning of the day
        td = ttt -datetime(1970, 1, 1)
        ts = int(td.total_seconds())      # Unix time - seconds from the epoch
    return (ts)                             # return it

# ########################################################################


def alive(app, keepalive=0, first='no', register=False):

    alivename = app +".alive"
    hostname = socket.gethostname()
    if (first == 'yes'):
        # create a file just to mark that we are alive
        alivefile = open(alivename, 'w')
        if register:
            atexit.register(lambda: os.remove(alivename))

    else:
        # append a file just to mark that we are alive
        alivefile = open(alivename, 'a')
    local_time = datetime.now()
    alivetime = local_time.strftime("%y-%m-%d %H:%M:%S")
    alivefile.write(alivetime +":" +hostname +" "+str(keepalive)+" \n")  # write the time as control
    alivefile.close()               # close the alive file
    return()
# ########################################################################
# import datetime
