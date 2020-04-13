#!/usr/bin/python3
#
# Python code to show access to OGN Beacons
#
# Version for gathering all the records for the world
#

from   datetime import datetime
from   ctypes import *
import socket
import time
import string
import pytz
import sys
import os
import os.path
import signal
import atexit
from parserfuncs import *               # the ogn/ham parser functions
#from geopy.distance import vincenty     # use the Vincenty algorithm^M
from geopy.distance import geodesic     # use the Vincenty algorithm^M
from time import sleep                  # use the sleep function
# from   geopy.geocoders import GeoNames # use the Nominatim as the geolocator^M
import MySQLdb                          # the SQL data base routines^M
from flarmfuncs import *                # import the functions relating with the Flarm ID

#########################################################################


def shutdown(sock, datafile):           # shutdown routine, close files and report on activity
                                        # shutdown before exit
    try:
        sock.shutdown(0)                # shutdown the connection
        sock.close()                    # close the connection file
    except:
        print("Ignore SOCK errors at this time -- shutdown")
    if datafile:
       datafile.close()                    # close the data file
    print("Sources: ", fsour)           # print the data about the different sources
                                        # report number of records read and IDs discovered
    print('Records read:', cin, ' DB records created: ', cout)
    try:
        conn.commit()                   # commit the DB updates
        conn.close()                    # close the database
    except:
        print("Ignore MySql errors at this time -- shutdown")

    local_time = datetime.now()         # report date and time now
    print("Time now:", local_time, " Local time.")
    print("=====================================")
    if os.path.exists(config.APP+".alive"):
        os.remove(config.APP+".alive")  # delete the mark of being alive
    return                              # job done

#######################################################################


def signal_term_handler(signal, frame):
    print('got SIGTERM ... shutdown orderly')
    shutdown(sock, datafile)            # shutdown orderly
    sys.exit(0)


# .....................................................................#
signal.signal(signal.SIGTERM, signal_term_handler)
# .....................................................................#

#
########################################################################
programver = 'V2.00'			# manually set the program version !!!

print("\n\nStart APRS, SPIDER, SPOT, CAPTURS, and LT24 logging "+programver)
print("====================================================================")
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
import config				# import the configuration details
if os.path.exists(config.PIDfile):	# check if this program is aleady running !!!
    raise RuntimeError("APRSlog already running !!!")
    exit(-1)
#
APP = "APRS"				# the application name
cin = 0                                 # input record counter
cout = 0                                # output file counter
i = 0                                   # loop counter
err = 0				        # number of read errors
day = 0				        # day of running
maxnerrs = 50                           # max number of error before quiting

fsllo = {'NONE  ': 0.0}                 # station location longitude
fslla = {'NONE  ': 0.0}                 # station location latitude
fslal = {'NONE  ': 0.0}                 # station location altitude
fslod = {'NONE  ': (0.0, 0.0)}          # station location - tuple
fsmax = {'NONE  ': 0.0}                 # maximun coverage
fsalt = {'NONE  ': 0}                   # maximun altitude
fsour = {}			 	# sources

# --------------------------------------#
DATA = True				# use the configuration values
DBpath      = config.DBpath
DBhost      = config.DBhost
DBuser      = config.DBuser
DBpasswd    = config.DBpasswd
DBname      = config.DBname
OGNT        = config.OGNT
# --------------------------------------#

if OGNT:
    from ogntfuncs import *

# --------------------------------------#
					# open the DataBase
conn = MySQLdb.connect(host=DBhost, user=DBuser, passwd=DBpasswd, db=DBname)
curs = conn.cursor()                    # set the cursor

print("MySQL: Database:", DBname, " at Host:", DBhost)

#----------------------aprslog.py start-----------------------#

prtreq = sys.argv[1:]			# check the arguments
if prtreq and prtreq[0] == 'prt':
    prt = True
else:
    prt = False

if prtreq and prtreq[0] == 'DATA':
    DATA = True
if prtreq and prtreq[0] == 'NODATA':
    DATA = False
    datafile=False

with open(config.PIDfile, "w") as f:    # create the lock file
    f.write(str(os.getpid()))		# to avoid running the same program twice 
    f.close()
atexit.register(lambda: os.remove(config.PIDfile)) # remove it at exit


if OGNT:                        	# if we need aggregation of FLARM and OGN trackers data
    ognttable = {}            	        # init the instance of the table
    # build the table from the TRKDEVICES DB table
    ogntbuildtable(conn, ognttable, prt)

# create socket & connect to server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.connect((config.APRS_SERVER_HOST, config.APRS_SERVER_PORT))
print("Socket sock connected")

# logon to OGN APRS network

compfile = config.cucFileLocation + "competitiongliders.lst"

if os.path.isfile(compfile):		# if we are in competition mode
    print("Competition file:", compfile)# we restrict only to the flamrs of the competition gliders
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

    login = 'user %s pass %s vers APRSLOG %s filter d/TCPIP* %s' % (config.APRS_USER, config.APRS_PASSCODE, programver, filter)
else:

    login = 'user %s pass %s vers APRSLOG %s filter d/TCPIP* %s' % (config.APRS_USER, config.APRS_PASSCODE, programver, config.APRS_FILTER_DETAILS)

login=login.encode(encoding='utf-8', errors='strict') 	# encode on UTF-8 

sock.send(login)			# send the login to the APRS server

# Make the connection to the server
sock_file = sock.makefile(mode='rw')    # make read/write as we need to send the keep_alive


print("APRS Version:", sock_file.readline())	# report the APRS version
sleep(2)
# for control print the login sent and get the response
print("APRS Login request:", login)
print("APRS Login reply:  ", sock_file.readline())	# report the APRS reply


start_time = time.time()
local_time = datetime.now()
fl_date_time = local_time.strftime("%y%m%d")
OGN_DATA = config.DBpath + "APRS" + fl_date_time+'.log'
print("APRS data file is: ", OGN_DATA, DATA)
if DATA:
   datafile = open(OGN_DATA, 'a')		# data file for loggin if requested
keepalive_count = 1
keepalive_time = time.time()
alive(config.APP, first='yes')		# create the ALIVE file/lock
#
#-----------------------------------------------------------------
#-----------------------------------------------------------------
#
now = datetime.utcnow()			# get the UTC time
min5 = timedelta(seconds=300)		# 5 minutes ago
now = now-min5				# now less 5 minutes
# number of seconds until beginning of the day 1-1-1970
td = now-datetime(1970, 1, 1)
ts = int(td.total_seconds())		# Unix time - seconds from the epoch
tc = ts					# init the variables
ty = ts
lt24ts = ts
ttime = now.strftime("%Y-%m-%dT%H:%M:%SZ")  # format required by SPIDER
day = now.day				# day of the month

date = datetime.now()

try:

    while True:
        current_time = time.time()
        local_time = datetime.now()
        now = datetime.utcnow()		# get the UTC time
        if now.day != day:	        # check if day has changed
            print("End of Day...\n\n\n", day)	# end of UTC day
            shutdown(sock, datafile)	# recycle
            print("Bye ...\n\n\n", day)	# end of UTC day
            exit(0)

                                        # get the time since last keep-alive
        elapsed_time = current_time - keepalive_time
        if (current_time - keepalive_time) > 180:        	# keepalives every 3 mins
                                        # and mark that we are still alive
            alive(config.APP)
            try:
                rtn = sock_file.write("#Python ognES App\n\n")
                                        # Make sure keepalive gets sent. If not flushed then buffered
                sock_file.flush()
                datafile.flush()
                run_time = time.time() - start_time
                if prt:
                    print("Send keepalive number: ", keepalive_count, " After elapsed_time: ", int(
                        (current_time - keepalive_time)), " After runtime: ", int(run_time), " secs")
                keepalive_time = current_time
                keepalive_count = keepalive_count + 1
                now = datetime.utcnow()	# get the UTC time
            except Exception as e:
                print(( '>>>>: something\'s wrong with socket write. Exception type is %s' % (repr(e))))
                now = datetime.utcnow()	# get the UTC time
                print("UTC time is now: ", now)
                err += 1
                if err > maxnerrs:
                    print(">>>>: Write returns an error code. Failure.  Orderly closeout")
                    date = datetime.now()
                    break
                else:
                    sleep(5) 		# wait 5 seconds
                    continue
            if OGNT:                   	# if we need aggregation of FLARM and OGN trackers data
                                        # rebuild the table from the TRKDEVICES DB table
                ogntbuildtable(conn, ognttable, prt)

            sys.stdout.flush()		# flush the print messages

        if prt:
            print("In main loop. Count= ", i)
            i += 1
        try:
            packet_str = sock_file.readline() 		# Read packet string from socket

            if len(packet_str) > 0 and packet_str[0] != "#" and config.LogData:
                datafile.write(packet_str)		# log the data if requested
            if prt:
                print(packet_str)
        except socket.error:
            print(">>>>: Socket error on readline")
            continue
        except KeyboardInterrupt:
                print("Keyboard input received, ignore")
                print("End of Day...\n\n\n", day)	# end of UTC day
                shutdown(sock, datafile)	# recycle
                print("Bye ...\n\n\n", day)	# end of UTC day
                exit(0)
    		
        except :
            print("Error on readline")
            print(">>>>: ", packet_str)
            continue
        if prt:
            print(packet_str)
        # A zero length line should not be return if keepalives are being sent
        # A zero length line will only be returned after ~30m if keepalives are not sent
        if len(packet_str) == 0:
            err += 1
            if err > maxnerrs:
                print(">>>>: Read returns zero length string. Failure.  Orderly closeout")
                date = datetime.now()
                print("UTC now is: ", date)
                break
            else:
                sleep(5) 		# wait 5 seconds
                continue

        ix = packet_str.find('>')
        cc = packet_str[0:ix]
        packet_str = cc.upper()+packet_str[ix:]		# conver the ID to uppercase
        msg = {}
        # if not a heartbeat from the server
        if len(packet_str) > 0 and packet_str[0] != "#":

            msg = parseraprs(packet_str, msg)		# parse the APRS message
            if msg == -1:
                continue
            data = packet_str
            if prt:

                print ("MSG:  ", msg)
            if 'id' in msg:
                ident = msg['id']                      	# id
            else:
                print(">>>>: Missing ID:>>>", data)
                continue
            aprstype    = msg['aprstype']		# APRS msg type
            longitude   = msg['longitude']
            latitude    = msg['latitude']
            altitude    = msg['altitude']
            path        = msg['path']
            relay       = msg['relay']
            otime       = msg['otime']
            source      = msg['source']
            station     = msg['station']
            if prt:
                print('Packet returned is: ', packet_str)
                print('Callsign is: ', ident, path, otime, aprstype)
            cin += 1                            # one more file to create
            if not source in fsour:	    	# did we see this source
                fsour[source] = 1	    	# init the counter
            else:
                fsour[source] += 1	    	# increase the counter

            # handle the TCPIP only for position or status reports
            if source == 'FANE':
                continue
            if source == 'ODLY':
                print ("ODLY>>>>:", msg, "<<<<")
                path = "tracker"
            if (path == 'aprs_receiver' or relay == 'TCPIP*' or path == 'receiver') and (aprstype == 'position' or aprstype == 'status'):
                status = msg['status']		# get the full status message
                if len(status) > 254:
                    status = status[0:254]
                if 'temp' in msg:
                        temp = msg['temp']	# station temperature
                        if temp == None or type(temp) == None:
                            temp = -1.0
                else:
                        temp=-1.0
                if 'version' in msg:
                        version = msg['version']# station SW version
                        if type(version) == None:
                            version= ' '
                else:
                        version = ' '
                if 'cpu' in msg:                # station CPU load
                        cpu = msg['cpu']	# CPU load
                        if type(cpu) == None:
                            cpu = 0
                else:
                        cpu = 0
                if 'rf' in msg:                 #
                        rf = msg['rf']	        # RF sensitibity load
                        if type(rf) == None:
                            rf= '0'
                else:
                        rf = '0'

                if longitude == -1 and latitude == -1:  # if the status report
                    if not ident in fslla:  # in the rare case that we got the status report but not the position report
                        continue  # in that case just continue
                    # we get tle lon/lat/alt from the table
                    latitude = fslla[ident]
                    longitude = fsllo[ident]
                    altitude = fslal[ident]
                    otime = datetime.utcnow()
                    #print "TTT:", ident, latitude, longitude, altitude, otime, version, cpu, temp, rf, status
                if not ident in fslod:		# if we not have it yeat on the table
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
                ccchk=cc[0:4]                   # just the first 4 chars
                if ccchk =="BSKY" or ccchk == "FNB1" or ccchk == "AIRS":    # useless sta
                    continue

                try:
                    inscmd = "insert into RECEIVERS values ('%s', %f,  %f,  %f, '%s', '%s', %f, %f, '%s', '%s')" %\
                    (cc, latitude, longitude, altitude, otime, version, cpu, temp, rf, status)
                except:
                    print ("InsCmd: >>>>", cc, latitude, longitude, altitude, otime, "V:", version, "C:", cpu,"T:",  temp, "R:", rf, status, "\nMGS:", msg)
                try:
                    curs.execute(inscmd)
                except MySQLdb.Error as e:
                    try:
                        print(">>>>: MySQL1 Error [%d]: %s" % (e.args[0], e.args[1]))
                    except IndexError:
                        print(">>>>: MySQL2 Error: %s" % str(e))
                    print(">>>>: MySQL3 error:",  cout, inscmd)
                    print(">>>>: MySQL4 data :",  data)
                cout += 1			# number of records saved
                conn.commit()			# commit to the DB
                continue
            if aprstype == 'status':		# if status report
                status = msg['status']		# get the status message
                                                # and the station receiving that status report
                station = msg['station']
                otime = datetime.utcnow()	# get the time from the system
                if len(status) > 254:
                    status = status[0:254]
                #print ("Status report:", ident, station, otime, status)
                inscmd = "insert into OGNTRKSTATUS values ('%s', '%s', '%s', '%s' ,'%s' )" %\
                    (ident, station, otime, status, 'APRS')
                try:
                    curs.execute(inscmd)
                except MySQLdb.Error as e:
                    try:
                        print(">>>>: MySQL1 Error [%d]: %s" % (
                            e.args[0], e.args[1]))
                    except IndexError:
                        print(">>>>: MySQL2 Error: %s" % str(e))
                    print(">>>>: MySQL3 error:",  cout, inscmd)
                    print(">>>>: MySQL4 data :",  data)
                cout += 1			# number of records saved
            if path == 'qAC':			# the case of a qAC message that is not a TCPIP*
                print(">>>qAC>>>:", data)
                continue                        # the case of the TCP IP as well
            if longitude == -1 or latitude == -1:  # if no position like in the status report
                continue			# that is the case of the ogn trackers status reports
            # if std records FLARM or OGN
            #
            if 'speed' in msg:
                speed       = msg['speed']
            else:
                print ("MMMMM>>>>", msg)
            course      = msg['course']
            uniqueid    = msg['uniqueid']
            if len(uniqueid) > 16:
                uniqueid = uniqueid[0:16]	# limit to 16 chars
            extpos      = msg['extpos']
            roclimb     = msg['roclimb']
            rot         = msg['rot']
            sensitivity = msg['sensitivity']
            gps         = msg['gps']
            hora        = msg['time']		# timestamp
            altim = altitude                    # the altitude in meters
            if altim > 15000 or altim < 0:
                altim = 0
                alti = '%05d' % altim           # convert it to an string
            dist = -1				# the case of when did not receive the station YET
            if station in fslod and source == 'OGN':  # if we have the station yet
                                                # distance to the station
                distance = geodesic((latitude, longitude), fslod[station]).km
                dist = distance
                if distance > 300.0:
                    print("distcheck: ", distance, data)
            if source != 'OGN':			# in the case of a NON OGN we use the base as reference point
                vitlat = config.location_latitude
                vitlon = config.location_longitude
                                                # distance to the BASE
                dist = geodesic((latitude, longitude), (vitlat, vitlon)).km

            if prt:
                print('Parsed data: POS: ', longitude, latitude, altitude, ' Speed:', speed, ' Course: ', course, ' Path: ', path, ' Type:', type)
                print("RoC", roclimb, "RoT", rot, "Sens", sensitivity, gps, uniqueid, dist, extpos, source, ":::")

                                                # write the DB record

            if (DATA):                          # if we need to store on the database
                                                # if we have OGN tracker aggregation and is an OGN tracker
                if OGNT and ident[0:3] == 'OGN':

                    if ident in ognttable:	# if the device is on the list
                                                # substitude the OGN tracker ID for the related FLARMID
                        ident = ognttable[ident]

                                                # get the date from the system as the APRS packet does not contain the date
                date = datetime.utcnow()
                dte = date.strftime("%y%m%d")  	# today's date
                if len(source) > 4:
                    source = source[0:3]	# restrict the length to 4 chars
                addcmd = "insert into OGNDATA values ('" + ident + "','" + dte + "','" + hora + "','" + station + "'," + str(latitude) + "," + str(longitude) + "," + str(altim) + "," + str(speed) + "," + \
                    str(course) + "," + str(roclimb) + "," + str(rot) + "," + str(sensitivity) + \
                    ",'" + gps + "','" + uniqueid + "'," + \
                    str(dist) + ",'" + extpos + "', '"+source + \
                    "' ) ON DUPLICATE KEY UPDATE extpos = '!ZZZ!' "
                if prt:
                    print(addcmd)
                try:
                    curs.execute(addcmd)
                except MySQLdb.Error as e:
                    try:
                        print(">>>>: MySQL Error [%d]: %s" % (e.args[0], e.args[1]))
                    except IndexError:
                        print(">>>>: MySQL Error: %s" % str(e))
                    print(">>>>: MySQL error:", cout, addcmd)
                    print(">>>>: MySQL data :",  data)
                
                cout += 1			# number of records saved
                conn.commit()                   # commit the DB updates


except KeyboardInterrupt:
    print("Keyboard input received, ignore")
    pass
print (">>>>: end of loop ... error detected or SIGTERM \n\n")
shutdown(sock, datafile)
print("Exit now ...", err)
exit(1)
