#!/usr/bin/python3
#
# Python code to show access to OGN Beacons
#
# Version for gathering all the records for the world
#

import config				# import the configuration details
from datetime import datetime, timedelta
import socket
import time
import json
import sys
import os
import os.path
import signal
import atexit
from parserfuncs import alive, parseraprs  # the ogn/ham parser functions
from geopy.distance import geodesic     # use the Vincenty algorithm^M
from time import sleep                  # use the sleep function
# from   geopy.geocoders import GeoNames # use the Nominatim as the geolocator^M
import MySQLdb                          # the SQL data base routines^M
# from flarmfuncs import *                # import the functions relating with the Flarm ID
import argparse

#########################################################################


def aprsconnect(sock, login, firsttime=False, prt=False):  # connect to the APRS server
    if not firsttime:
        try:				# reconnect
            sock.shutdown(0)                # shutdown the connection
            sock.close()                    # close the connection file
        except:
            print("Ignore SOCK errors at this time -- reconnect")
            # create socket & connect to server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if prt or firsttime:
        print("Default RCVBUF:", sock.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF))  # get the size of the receiving buffer
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 2097152)		  # set the receiving buffer to be 2Mb
    if prt or firsttime:
        print("New     RCVBUF:", sock.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF))
    if LASTFIX:				# if LASTFIX use the non filtered port
        print("Connecting with APRS HOST:", config.APRS_SERVER_HOST, ":", 10152)
        sock.connect((config.APRS_SERVER_HOST, 10152))  # use the non filtered port
        #sock.connect(("aprs.glidernet.org", 10152))
    else:				# if not use the use from the configuration file
        print("Connecting with APRS HOST:", config.APRS_SERVER_HOST, ":", config.APRS_SERVER_PORT)
        sock.connect((config.APRS_SERVER_HOST, config.APRS_SERVER_PORT))
    print("Socket sock connected")
    sock.send(login)			# send the login to the APRS server

    # Make the connection to the server
    sock_file = sock.makefile(mode='rw')  # make read/write as we need to send the keep_alive
    if prt or firsttime:
        print("APRS Version:", sock_file.readline())  # report the APRS version
        # for control print the login sent and get the response
        print("APRS Login request:", login)  # print the login command for control
        print("APRS Login reply:  ", sock_file.readline())  # report the APRS reply
    sleep(2)				# just wait to receive the login command
    return (sock, sock_file)		# return sock and sockfile

#########################################################################


def shutdown(sock, datafile):           # shutdown routine, close files and report on activity
    # shutdown before exit
    try:
        sock.shutdown(0)                # shutdown the connection
        sock.close()                    # close the connection file
    except:
        print("Ignore SOCK errors at this time -- shutdown")
    if datafile:
        datafile.close()                 # close the data file
        if (os.stat(OGN_DATA).st_size == 0):
            os.system("rm " + OGN_DATA)

    print("=====================================")
    print("Sources: ", fsour)           # print the data about the different sources
    print("Aircraft types: ", acfttype)  # print the aircraft types
    # report number of records read and IDs discovered
    print('Records read:', cin, ' DB records created: ', cout)
    print('Devices type:', fdtcnt, "Unique Ids:", len(flastfix))
    try:
        conn.commit()                   # commit the DB updates
        conn.close()                    # close the database
    except:
        print("Ignore MySql errors at this time -- shutdown")

    local_time = datetime.now()         # report date and time now
    print("Time now:", local_time, " Local time.")
    print("=====================================")
    if os.path.exists(config.APP + hostname + ".alive"):
        os.remove(config.APP + hostname + ".alive")  # delete the mark of being alive
    if os.path.exists(config.PIDfile):
        os.remove(config.PIDfile)  # remove it at exit
    atexit.unregister(lambda: os.remove(config.PIDfile))  # remove it at exit
    return                              # job done

#######################################################################


def signal_term_handler(signal, frame):
    print('got SIGTERM ... shutdown orderly')
    shutdown(sock, datafile)            # shutdown orderly
    print('Bye...')
    os._exit(0)


# .....................................................................#
signal.signal(signal.SIGTERM, signal_term_handler)
# .....................................................................#

#
########################################################################
programver = 'V2.08'			# manually set the program version !!!

print("\n\nStart APRS, SPIDER, SPOT, InReach, CAPTURS, Skylines, ADSB and LT24 logging: " + programver)
print("==================================================================================")
#					  report the program version based on file date
print("Program Version:", time.ctime(os.path.getmtime(__file__)))
date = datetime.utcnow()                # get the date
dte = date.strftime("%y%m%d")           # today's date
hostname = socket.gethostname()		# get the hostname
print("\nDate: ", date, "UTC on SERVER:", hostname, "Process ID:", os.getpid())
date = datetime.now()
print("Time now is: ", date, " Local time")

# --------------------------------------#
#
if os.path.exists(config.PIDfile):  # check if this program is aleady running !!!
    raise RuntimeError("APRSlog already running !!!")
    exit(-1)
#
APP = "APRS"				# the application name
cin = 0                                 # input record counter
cout = 0                                # output file counter
loopcnt = 0                             # loop counter
err = 0				        # number of read errors
day = 0				        # day of running
commentcnt = 0				# counter of comment lines
maxnerrs = 99                           # max number of error before quiting
SLEEPTIME = 2				# time to sleep in case of errors
comment = False			# comment line from APRS server
datafile = False			# use the datafile on|off
COMMIT = True				# commit every keep lives
prt = False			# use the configuration values
DATA = True				# use the configuration values
MEM = False			# built the lastfix flarmId table in memory
STATIONS = False			# get the stations info
STD = True				# Std case
OGN_DATA = ''

fsllo = {'NONE  ': 0.0}                 # station location longitude
fslla = {'NONE  ': 0.0}                 # station location latitude
fslal = {'NONE  ': 0.0}                 # station location altitude
fslod = {'NONE  ': (0.0, 0.0)}          # station location - tuple
fsmax = {'NONE  ': 0.0}                 # maximun coverage
fsalt = {'NONE  ': 0}                   # maximun altitude
fsour = {}			 	# sources
acfttype = []			 	# aircraft types
fdtcnt = {}			 	# device type counter
flastfix = {}				# table with the LAST FIXES
lastfix = []				# list of last fix from DB
fdistcheck = {}				# table with device with distance more than 400 kms
# --------------------------------------#
DBpath = config.DBpath
DBhost = config.DBhost
DBuser = config.DBuser
DBpasswd = config.DBpasswd
DBname = config.DBname
OGNT = config.OGNT
# --------------------------------------#

if OGNT:
    from ogntfuncs import ogntbuildtable

# --------------------------------------#
    # open the DataBase
conn = MySQLdb.connect(host=DBhost, user=DBuser, passwd=DBpasswd, db=DBname)
curs = conn.cursor()                    # set the cursor

print("MySQL: Database:", DBname, " at Host:", DBhost)

#----------------------aprslog.py start-----------------------#
parser = argparse.ArgumentParser(description="OGN receive the messages from the APRS network and store it on the MySQL database")
parser.add_argument('-p', '--print', required=False,
                    dest='prt', action='store', default=False)
parser.add_argument('-d', '--DATA', required=False,
                    dest='DATA', action='store', default=False)
parser.add_argument('-l', '--LASTFIX', required=False,
                    dest='LASTFIX', action='store', default=False)
parser.add_argument('-m', '--MEM', required=False,
                    dest='MEM', action='store', default=False)
parser.add_argument('-s', '--STATIONS', required=False,
                    dest='STATIONS', action='store', default=False)
args = parser.parse_args()
prt = args.prt			# print on|off
DATA = args.DATA			# data store on|off
LASTFIX = args.LASTFIX			# LASTFIX on|off
MEM = args.MEM			# MEM on|off
STATIONS = args.STATIONS		# stations on|off
if STATIONS:
    STD = False				# not need to record DATA
print("Options: prt:", prt, ",DATA:", DATA, ",MEM:", MEM, ",LASTFIX:", LASTFIX, ",STATIONS:", STATIONS, ",STD", STD)

if LASTFIX:
    if MEM:
        try:
            curs.execute("select flarmId from GLIDERS_POSITIONS;")
            gl = curs.fetchall()
            for fid in gl:
                lastfix.append(fid[0])
        except MySQLdb.Error as e:
            try:
                print(">>>>: MySQL Error1 [%d]: %s" % (e.args[0], e.args[1]))
            except IndexError:
                print(">>>>: MySQL Error2: [%s]" % str(e))
        print("Number of IDs on the DB: ", len(lastfix))
if DATA:
    config.LogData = True

with open(config.PIDfile, "w") as f:    # create the lock file
    f.write(str(os.getpid()))		# to avoid running the same program twice
    f.close()
atexit.register(lambda: os.remove(config.PIDfile))  # remove it at exit


if OGNT and not LASTFIX:                # if we need aggregation of FLARM and OGN trackers data
    ognttable = {}            	        # init the instance of the table
    # build the table from the TRKDEVICES DB table
    ogntbuildtable(conn, ognttable, prt)


compfile = config.cucFileLocation + "competitiongliders.lst"

if os.path.isfile(compfile) and not LASTFIX and not STATIONS:		# if we are in competition mode
    print("Competition file:", compfile)  # we restrict only to the flamrs of the competition gliders
    fd = open(compfile, 'r')
    j = fd.read()
    if len(j) > 0:
        clist = json.loads(j)		# load the list of flarms used on the competition
    else:
        clist = []
    fd.close()
    filter = "b/"			# filter to only those gliders in competition
    for f in clist:
        filter += f		        # add the flarmid
        filter += "/"

    if OGNT:			        # if we have OGN tracker paired
        for f in ognttable:             # for each ogntracker

            filter += f  # add the flarm id/tracker id associated
            filter += "/"  # separated by an slash
    filter += "\n"
    # in case of competition we filter to just the competition gliders and their OGNT pairs
    login = 'user %s pass %s vers APRSLOG %s filter d/TCPIP* %s' % (config.APRS_USER, config.APRS_PASSCODE, programver, filter)
else:
    # normal case either STD or STATIONS
    login = 'user %s pass %s vers APRSLOG %s filter d/TCPIP* %s' % (config.APRS_USER, config.APRS_PASSCODE, programver, config.APRS_FILTER_DETAILS)

if LASTFIX:				# if we want just status or receivers and glider LASTFIX, use not filtered PORT
    login = 'user %s pass %s vers APRSLOG %s  \n' % (config.APRS_USER, config.APRS_PASSCODE, programver)

login = login.encode(encoding='utf-8', errors='strict') 	# encode on UTF-8

# -----------------------------------------------------------------
# logon to OGN APRS network

sock = False
Ntries = 0
(sock, sock_file) = aprsconnect(sock, login, firsttime=True, prt=prt)
if sock == False:
    while Ntries < 10:
        (sock, sock_file) = aprsconnect(sock, login, firsttime=True, prt=prt)
        if sock != False:
            break
        Ntries += 1
        if Ntries == 10:
            print("Errors connecting with APRS ... leaving now \n\n\n")
            exit(-1)

# -----------------------------------------------------------------
start_time = time.time()
local_time = datetime.now()
fl_date_time = local_time.strftime("%y%m%d")
if DATA:				# if we want to record the data on a file
    OGN_DATA = config.DBpath + "APRS" + fl_date_time + '.log'
    print("APRS data file is: ", OGN_DATA, DATA)
    datafile = open(OGN_DATA, 'a')  # data file for loggin if requested
else:
    datafile = False
keepalive_count = 1			# init the counter
keepalive_time = time.time()
alive(config.APP + hostname, first='yes')  # create the ALIVE file/lock
#
# -----------------------------------------------------------------
#
now = datetime.utcnow()			# get the UTC time
day = now.day				# day of the month
min5 = timedelta(seconds=300)		# 5 minutes ago
now = now - min5				# now less 5 minutes
# number of seconds until beginning of the day 1-1-1970
td = now - datetime(1970, 1, 1)
ts = int(td.total_seconds())		# Unix time - seconds from the epoch
tc = ts					# init the variables
ty = ts
lt24ts = ts
ttime = now.strftime("%Y-%m-%dT%H:%M:%SZ")  # format required by SPIDER

date = datetime.now()

#
# -----------------------------------------------------------------
#
try:
    while True:				# forever
        current_time = time.time()
        local_time = datetime.now()
        now = datetime.utcnow()		# get the UTC time
        if now.day != day:	        # check if day has changed
            print("End of Day...Day: ", day, "\n\n")  # end of UTC day
            shutdown(sock, datafile)  # recycle
            print("Bye ... day:", day, "\n\n\n")  # end of UTC day
            exit(0)

            # get the time since last keep-alive
        elapsed_time = current_time - keepalive_time
        if (current_time - keepalive_time) > 5 * 60:  # keepalives every 5 mins
            # and mark that we are still alive
            alive(config.APP + hostname)  # set the mark on the aliave file
            try:			# send a comment to the APRS server
                rtn = sock_file.write("# Python APRSLOG App \n")
                sock_file.flush() 	# Make sure keepalive gets sent. If not flushed then buffered
                run_time = time.time() - start_time
                if prt:
                    print("Send keepalive number: ", keepalive_count, loopcnt, " After elapsed_time: ",
                          int((current_time - keepalive_time)), " After runtime: ", int(run_time), " secs", now)
                if DATA:		# if we need to record on a file. flush it as well
                    datafile.flush()
                keepalive_time = current_time
                keepalive_count = keepalive_count + 1
                now = datetime.utcnow()  # get the UTC time
            except Exception as e:
                print(('>>>>: something\'s wrong with socket write. Exception type is %s' % (repr(e))))
                now = datetime.utcnow()  # get the UTC time
                print("UTC time is now: ", now)
                err += 1
                if err > maxnerrs:
                    print(">>>>: Write returns an error code. Failure.  Orderly closeout")
                    date = datetime.now()
                    break
                else:
                    sleep(SLEEPTIME) 	# wait X seconds
                    continue
            if OGNT and not LASTFIX:    # if we need aggregation of FLARM and OGN trackers data
                # rebuild the table from the TRKDEVICES DB table
                ogntbuildtable(conn, ognttable, prt)

            sys.stdout.flush()		# flush the print messages
            if COMMIT:
                conn.commit()		# commit to the DB every 5 minutes
            continue			# next APRSMSG

        if prt:
            print("In main loop. Count= ", loopcnt)
        loopcnt += 1			# just keep a count of number of request to the APRS server
        try:
            packet_str = ''
            packet_str = sock_file.readline() 		# Read packet string from socket

            if DATA and len(packet_str) > 0 and packet_str[0] != "#" and config.LogData:
                datafile.write(packet_str)		# log the data if requested
            if prt:
                print(packet_str)
        except socket.error as e:
            err += 1
            print(">>>>: Socket error on readline: ", loopcnt, packet_str, current_time)
            print(('>>>>: something\'s wrong with socket readline Exception type is %s' % (repr(e))))
            (sock, sock_file) = aprsconnect(sock, login, prt=prt)
            continue
        except KeyboardInterrupt:
            print("Keyboard input received, Bye Bye")
            shutdown(sock, datafile)
            print("Bye ...\n\n\n")
            os._exit(0)
        except:
            print(">>>>: Error on readline", now)
            print(">>>>: ", packet_str)
            rtn = sock_file.write("# Python APRSLOG App\n")
            continue

        if len(packet_str) > 0 and packet_str[0] == '#':
            comment = True
            commentcnt += 1
            continue
        else:
            comment = False
        if prt:
            print(packet_str)

        # A zero length line should not be return if keepalives are being sent
        # A zero length line will only be returned after ~30m if keepalives are not sent
        if len(packet_str) == 0:  # socket error ?
            err += 1
            print("packet_str empty, loop count:", loopcnt, keepalive_count, now, "Num errs:", err)
            (sock, sock_file) = aprsconnect(sock, login, prt=prt)
            if err > maxnerrs:
                print(">>>>: Too many errors reading APRS messages.  Orderly closeout")
                date = datetime.now()
                print("UTC now is: ", date)
                break
            else:
                sleep(SLEEPTIME) 		# wait 5 seconds
                continue

        ix = packet_str.find('>')
        cc = packet_str[0:ix]
        packet_str = cc.upper() + packet_str[ix:]		# conver the ID to uppercase
        msg = {}
        # if not a heartbeat from the server
        if len(packet_str) > 0 and packet_str[0] != "#":

            msg = parseraprs(packet_str, msg)		# parse the APRS message
            if msg == -1:
                continue
            data = packet_str
            if prt:

                print("MSG:  ", msg)
            if 'id' in msg:
                ident = msg['id']                      	# id
            else:
                print(">>>>: Missing ID:>>>", data)
                continue
            aprstype = msg['aprstype']		# APRS msg type
            longitude = msg['longitude']
            latitude = msg['latitude']
            altitude = msg['altitude']
            path = msg['path']
            relay = msg['relay']
            otime = msg['otime']
            source = msg['source']
            station = msg['station']
            if prt:
                print('Packet returned is: ', packet_str)
                print('Callsign is: ', ident, path, otime, aprstype)
            cin += 1                            # one more file to create
            if source not in fsour:	    	# did we see this source
                fsour[source] = 1	    	# init the counter
            else:
                fsour[source] += 1	    	# increase the counter

            if source == 'FANE' or source == 'UNKW':  # ignore those messages
                continue
            if source == 'ODLY':
                print("ODLY>>>>:", msg, "<<<<")
                path = "tracker"
            if 'acfttype' in msg:
                acftt = msg['acfttype']
                if acftt not in acfttype:
                    acfttype.append(acftt)

            # handle the TCPIP only for position or status reports
            if (path == 'aprs_receiver' or relay == 'TCPIP*' or path == 'receiver') and (aprstype == 'position' or aprstype == 'status'):
                #           RECEIVER CASE ------------------------------------------------------#
                status = msg['status']		# get the full status message
                if len(status) > 254:
                    status = status[0:254]
                if 'temp' in msg:
                    temp = msg['temp']  # station temperature
                    if temp == None or type(temp) == None:
                        temp = -1.0
                else:
                    temp = -1.0
                if 'version' in msg:
                    version = msg['version']  # station SW version
                    if type(version) == None:
                        version = ' '
                else:
                    version = ' '
                if 'cpu' in msg:                # station CPU load
                    cpu = msg['cpu']  # CPU load
                    if type(cpu) == None:
                        cpu = 0
                else:
                    cpu = 0
                if 'rf' in msg:                 #
                    rf = msg['rf']	        # RF sensitibity load
                    if type(rf) == None:
                        rf = '0'
                else:
                    rf = '0'

                if longitude == -1 and latitude == -1:  # if the status report
                    if ident not in fslla:  # in the rare case that we got the status report but not the position report
                        continue  # in that case just continue
                    # we get tle lon/lat/alt from the table
                    latitude = fslla[ident]
                    longitude = fsllo[ident]
                    altitude = fslal[ident]
                    otime = datetime.utcnow()
                    # print "TTT:", ident, latitude, longitude, altitude, otime, version, cpu, temp, rf, status
                if ident not in fslod:		# if we not have it yeat on the table
                    # save the location of the station
                    fslla[ident] = latitude
                    # save the location of the station
                    fsllo[ident] = longitude
                    # save the location of the station
                    fslal[ident] = altitude
                    # save the location of the station
                    fslod[ident] = (latitude, longitude)
                    fsmax[ident] = 0.0             # initial coverage zero
                    fsalt[ident] = 0               # initial coverage zero
                if data.find(":/") != -1:       # it is the position report ??
                    # we do not want that message ... we want the status report ...
                    continue
                if data.find(":)") != -1:       # it is the message report ??
                    print(">>> :)>>>", data)
                    # we do not want that message ... we want the status report ...
                    continue
                ccchk = cc[0:4]                   # just the first 4 chars
                if ccchk == "BSKY" or ccchk == "FNB1" or ccchk == "AIRS":    # useless sta
                    continue

                try:
                    inscmd = "insert into RECEIVERS values ('%s', %f,  %f,  %f, '%s', '%s', %f, %f, '%s', '%s')" %\
                        (cc, latitude, longitude, altitude, otime, version, cpu, temp, rf, status)
                except:
                    print("InsCmd: >>>>", cc, latitude, longitude, altitude, otime, "V:", version, "C:", cpu, "T:", temp, "R:", rf, status, "\nMGS:", msg)

                try:
                    curs.execute(inscmd)  # insert data into RECEIVERS table
                except MySQLdb.Error as e:
                    try:
                        print(">>>>: MySQL1 Error [%d]: %s" % (e.args[0], e.args[1]))
                    except IndexError:
                        print(">>>>: MySQL2 Error: [%s]" % str(e))
                    print(">>>>: MySQL3 error:", cout, inscmd)
                    print(">>>>: MySQL4 data :", data)
                cout += 1			# number of records saved
                continue

            if aprstype == 'status':		# if status report
                #           TRACKER STATUS CASE ------------------------------------------------------#
                status = msg['status']		# get the status message
                # and the station receiving that status report
                station = msg['station']
                otime = datetime.utcnow()  # get the time from the system
                if len(status) > 254:
                    status = status[0:254]
                #print ("Status report:", ident, station, otime, status)
                inscmd = "insert into OGNTRKSTATUS values ('%s', '%s', '%s', '%s' ,'%s' )" %\
                    (ident, station, otime, status, 'APRS')
                try:
                    curs.execute(inscmd)  # insert data into trackstatus table
                except MySQLdb.Error as e:
                    try:
                        print(">>>>: MySQL1 Error [%d]: %s" % (
                            e.args[0], e.args[1]))
                    except IndexError:
                        print(">>>>: MySQL2 Error: %s" % str(e))
                    print(">>>>: MySQL3 error:", cout, inscmd)
                    print(">>>>: MySQL4 data :", data)

                cout += 1			# number of records saved

            if path == 'qAC':			# the case of a qAC message that is not a TCPIP*
                print(">>>qAC>>>:", data)
                continue                        # the case of the TCP IP as well
            if longitude == -1 or latitude == -1:  # if no position like in the status report
                continue			# that is the case of the ogn trackers status reports

#           FLARM OR OGN FIXES  CASE ------------------------------------------------------#
            # if std records FLARM or OGN
            #
            if 'speed' in msg:
                speed = msg['speed']
            else:
                print("MMMMM>>>>", msg)
            course = msg['course']
            uniqueid = msg['uniqueid']
            if len(uniqueid) > 16:
                uniqueid = uniqueid[0:16]  # limit to 16 chars
            extpos = msg['extpos']
            roclimb = msg['roclimb']
            rot = msg['rot']
            sensitivity = msg['sensitivity']
            gps = msg['gps']
            if len(gps) > 6:
                gps = gps[0:6]
            hora = msg['time']		# timestamp
            altim = altitude                    # the altitude in meters
            if altim > 15000 or altim < 0:
                altim = 0
                alti = '%05d' % altim           # convert it to an string
            dist = -1				# the case of when did not receive the station YET
            if station in fslod and source == 'OGN':  # if we have the station coordinates yet
                # distance to the station
                distance = geodesic((latitude, longitude), fslod[station]).km
                dist = distance
                if distance > 400.0 and not LASTFIX:  # if nore than 400 kms
                    if ident not in fdistcheck:
                        print("distcheck: ", distance, data)  # report it only once
                    fdistcheck[ident] = distance
            if source != 'OGN':			# in the case of a NON OGN we use the base as reference point
                vitlat = config.location_latitude
                vitlon = config.location_longitude
                # distance to the BASE
                dist = geodesic((latitude, longitude), (vitlat, vitlon)).km
#           -----------------------------------------------------------------
            if prt:
                print('Parsed data: :::', ident, ' POS: ', longitude, latitude, altitude, ' Speed:', speed, ' Course: ', course, ' Path: ', path, ' Type:', type)
                print("RoC", roclimb, "RoT", rot, "Sens", sensitivity, gps, uniqueid, dist, extpos, source, ":::")

#           -----------------------------------------------------------------
                # write the DB record

            if (DATA or LASTFIX or STD):        # if we need to store on the database
                # if we have OGN tracker aggregation and is an OGN tracker
                if OGNT and ident[0:3] == 'OGN' and not LASTFIX:

                    if ident in ognttable:  # if the device is on the list
                        # substitude the OGN tracker ID for the related FLARMID
                        ident = ognttable[ident]

                        # get the date from the system as the APRS packet does not contain the date
                        # get the date from the system as the APRS packet does not contain the date
                dateutc = datetime.utcnow()
                dte = dateutc.strftime("%y%m%d")  # today's date
                if len(source) > 4:
                    source = source[0:4]  # restrict the length to 4 chars
                dtype = ident[0:3]		# device type: ICAO, FLARM, OGNT
                if dtype in fdtcnt:		# set the counters by device type
                    fdtcnt[dtype] += 1		# increase the counter
                else:
                    fdtcnt[dtype] = 1 		# init the counter

                if LASTFIX:			# we we need just to store LASTFIX of the glider
                    #                   LASTFIX   CASE ------------------------------------------------------#
                    flastfix[ident] = msg		# save it in memory for the time being

                    if MEM:			# if we use the memory option
                        if ident in lastfix:
                            recfound = True		# mark as found
                        else:
                            recfound = False
                            if prt:
                                print("New ID: ", ident)
                            lastfix.append(ident)  # add it to the list

                    else:			# if we use the DB option
                        try:			# first try to see if we have that device on the GLIDER_POSITION table
                            cmd1 = "SELECT count(flarmId) FROM GLIDERS_POSITIONS WHERE flarmId='" + ident + "'; "
                            curs.execute(cmd1)
                        except MySQLdb.Error as e:
                            try:
                                print(">>>>: MySQL Error1 [%d]: %s" % (e.args[0], e.args[1]))
                            except IndexError:
                                print(">>>>: MySQL Error2: [%s]" % str(e))
                            print(">>>>: MySQL error3 [count & cmd] :", cout, cmd1)
                            print(">>>>: MySQL data :", data)

                        row = curs.fetchone()		# get the counter 0 or 1 ???
                        if row[0] == 0 and source != "UNKW":  # if not add the entry to the tablea
                            recfound = False		# ark it as not found
                        else:
                            recfound = True

                    if not recfound:		# if we never saw this ID ... insert it on the DB
                        try:
                            cmd2 = "INSERT INTO GLIDERS_POSITIONS  VALUES ('%s', %f, %f, %f, %f, '%s', '%s', %f, %f, %f, %f, '%s', %f, '%s', '%s', -1, '%s');" % \
                                (ident, latitude, longitude, altim, course, dte, hora, float(rot), speed, dist, float(roclimb), station, float(sensitivity), gps, otime, source)
                        except TypeError:
                            print(">>>>cmd2:", ident, latitude, longitude, altim, course, dte, hora, float(rot), speed, dist, float(roclimb), station, float(sensitivity), gps, otime, source)
                        if prt:
                            print("CMD2>>>", cmd2)
                        try:
                            curs.execute(cmd2)  # insert the data on the DB
                        except MySQLdb.Error as e:
                            try:
                                print(">>>>: MySQL Error1 [%d]: %s" % (e.args[0], e.args[1]))
                            except IndexError:
                                print(">>>>: MySQL Error2: %s" % str(e))
                            print(">>>>: MySQL error3:", cout, cmd2)
                            print(">>>>: MySQL data :", data)

                    else:			# if found just update the entry on the table
                        try:
                            cmd3 = "UPDATE GLIDERS_POSITIONS SET lat='%f', lon='%f', altitude='%f', course='%f', date='%s', time='%s', rot='%f', speed='%f', distance='%f', climb='%f', station='%s', gps='%s', sensitivity='%f', lastFixTx=NOW(), source='%s' where flarmId='%s';" % \
                                (latitude, longitude, altim, course, dte, hora, float(rot), speed, dist, float(roclimb), station, gps, float(sensitivity), source, ident)
                        except TypeError:
                            print(">>>>cmd3:", ident, latitude, longitude, altim, course, dte, hora, float(rot), speed, dist, float(roclimb), station, float(sensitivity), gps, otime, source)
                        if prt:
                            print("CMD3>>>", cmd3)
                        try:
                            curs.execute(cmd3)  # update the data on the DB
                        except MySQLdb.Error as e:
                            try:
                                print(">>>>: MySQL Error1 [%d]: %s" % (e.args[0], e.args[1]))
                            except IndexError:
                                print(">>>>: MySQL Error2: %s" % str(e))
                            print(">>>>: MySQL error3:", cout, cmd3)
                            print(">>>>: MySQL data :", data)

#               STD  CASE NOT LASTFIX ------------------------------------------------------#
                else:				# if we just is normal option, just add the data to the OGNDATA table
                    addcmd = "insert into OGNDATA values ('" + ident + "','" + dte + "','" + hora + "','" + station + "'," + \
                        str(latitude) + "," + str(longitude) + "," + str(altim) + "," + str(speed) + "," + \
                        str(course) + "," + str(roclimb) + "," + str(rot) + "," + str(sensitivity) + \
                        ",'" + gps + "','" + uniqueid + "'," + \
                        str(dist) + ",'" + extpos + "', '" + source + \
                        "' ) ON DUPLICATE KEY UPDATE extpos = '!ZZZ!' "
                    if prt:
                        print(addcmd)
                    try:
                        curs.execute(addcmd)
                    except MySQLdb.Error as e:
                        try:
                            print(">>>>: MySQL Error1 [%d]: %s" % (e.args[0], e.args[1]))
                        except IndexError:
                            print(">>>>: MySQL Error2: %s" % str(e))
                        print(">>>>: MySQL error3:", cout, addcmd)
                        print(">>>>: MySQL data :", data)
                    conn.commit()		# commit to the DB  right away

                cout += 1  # number of records saved

#
# end of infinity while
# --------------------------------------------------------------------------------------
except SystemExit:
    print(">>>>: System Exit <<<<<<\n\n")
    os._exit(1)
except KeyboardInterrupt:
    print(">>>>: Keyboard Interupt <<<<<<\n\n")

print(">>>>: end of loop ... error detected or SIGTERM <<<<<<\n\n")
shutdown(sock, datafile)  # close down everything
print("Exit now ... Number of errors: ", err)

if err > maxnerrs:
    now = datetime.utcnow()			# get the UTC time
    print("Restarting python program ...", now, sys.executable, "\n\n")
    sys.stdout.flush()		# flush the print messages
    os.execv(__file__, sys.argv)  # restart the program
    # we should not reach here !!!!
    # python = sys.executable
    #os.execl(python, python, * sys.argv)
os._exit(0)
