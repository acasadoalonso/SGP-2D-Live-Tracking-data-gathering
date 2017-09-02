#!/usr/bin/python
#
# Python code to push into the OGN APRS the data from SPOT/SPIDER/CAPTURS/LT24/SKYLINES
#

from datetime import datetime
from libfap import *
from ctypes import *
import socket
import time
import string
import pytz
import sys
import os
import os.path
import signal
import atexit
import kglid
from   parserfuncs import *             # the ogn/ham parser functions
from   geopy.distance import vincenty   # use the Vincenty algorithm^M
from   time import sleep                # use the sleep function
import MySQLdb                          # the SQL data base routines^M
from flarmfuncs import *		# import the functions delaing with the Flarm ID
#########################################################################
def shutdown(sock):		        # shutdown routine, close files and report on activity
                                        # shutdown before exit
        libfap.fap_cleanup()            # close lifap in order to avoid memory leaks
	try:
        	sock.shutdown(0)        # shutdown the connection
        	sock.close()            # close the connection file
        except Exception, e:
		print "Socket error..."
        conn.commit()                   # commit the DB updates
        conn.close()                    # close the database
        local_time = datetime.now() # report date and time now
        print "Shutdown now, Time now:", local_time, " Local time."
 	if os.path.exists(config.DBpath+"APRSPUSH.alive"):
		os.remove(config.DBpath+"APRSPUSH.alive")	# delete the mark of being alive
        return                          # job done

#########################################################################

#########################################################################
#########################################################################

def signal_term_handler(signal, frame):
    print 'got SIGTERM ... shutdown orderly'
    shutdown(sock) 			# shutdown orderly
    sys.exit(0)

# ......................................................................#
signal.signal(signal.SIGTERM, signal_term_handler)
# ......................................................................#
def prttime(unixtime):
	tme	=datetime.utcfromtimestamp(unixtime)	# get the time from the timestamp
	return(tme.strftime("%H%M%S"))			# the time

#
########################################################################
programver='V1.0'
print "\n\nStart APRSPUSH "+programver
print "=============================="

print "Program Version:", time.ctime(os.path.getmtime(__file__))
date=datetime.utcnow()         		# get the date
dte=date.strftime("%y%m%d")             # today's date
print "\nDate: ", date, "UTC on SERVER:", socket.gethostname(), "Process ID:", os.getpid()
date = datetime.now()
print "Time now is: ", date, " Local time"

#
# get the SPIDER TRACK  & SPOT information
#
# --------------------------------------#
import config
if os.path.exists(config.PIDfile+"PUSH"):
	raise RuntimeError("APRSlog/push already running !!!")
	exit(-1)
#
APP="APRSPUSH"				# the application name
SLEEP=10				# sleep 10 seconds in between calls to the APRS
cin   = 0                               # input record counter
cout  = 0                               # output file counter
i     = 0                               # loop counter
err   = 0				# number of read errors

fsllo={'NONE  ' : 0.0}                  # station location longitude
fslla={'NONE  ' : 0.0}                  # station location latitude
fslal={'NONE  ' : 0.0}                  # station location altitude
fslod={'NONE  ' : (0.0, 0.0)}           # station location - tuple
fsmax={'NONE  ' : 0.0}                  # maximun coverage
fsalt={'NONE  ' : 0}                    # maximun altitude

# --------------------------------------#
DBpath   =config.DBpath
DBhost   =config.DBhost
DBuser   =config.DBuser
DBpasswd =config.DBpasswd
DBname   =config.DBname
SPIDER   =config.SPIDER
SPOT     =config.SPOT
CAPTURS  =config.CAPTURS
SKYLINE  =config.SKYLINE
LT24     =config.LT24
OGNT     =config.OGNT
# --------------------------------------#


if SPIDER:
	from spifuncs import *
	spiusername =config.SPIuser
	spipassword =config.SPIpassword
	spisysid =config.SPISYSid

if SPOT:
	from spotfuncs import *

if CAPTURS:
	from captfuncs import *

if SKYLINE:
	from skylfuncs import *

if LT24:
	from lt24funcs import *
	lt24username =config.LT24username
	lt24password =config.LT24password
	LT24qwe=" "
	LT24_appSecret= " "
	LT24_appKey= " "
	LT24path=DBpath+"LT24/"
	LT24login=False
	LT24firsttime=True

# --------------------------------------#


# --------------------------------------#
conn=MySQLdb.connect(host=DBhost, user=DBuser, passwd=DBpasswd, db=DBname)
curs=conn.cursor()                      # set the cursor

print "MySQL: Database:", DBname, " at Host:", DBhost

#----------------------ogn_aprspush.py start-----------------------

prtreq =  sys.argv[1:]
if prtreq and prtreq[0] == 'prt':
    prt = True
else:
    prt = False

with open(config.PIDfile+"PUSH","w") as f:
	f.write (str(os.getpid()))
	f.close()
atexit.register(lambda: os.remove(config.PIDfile+"PUSH"))

# create socket & connect to server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((config.APRS_SERVER_HOST, config.APRS_SERVER_PORT))
print "Socket sock connected"

# logon to OGN APRS network

login = 'user %s pass %s vers APRSPUSH %s %s'  % ("APRSPUSH", "25596" , programver, "\n")
print "APRS login:", login

sock.send(login)

# Make the connection to the server
sock_file = sock.makefile()
config.SOCK=sock
config.SOCK_FILE=sock_file
print "APRS Version:", sock_file.readline()
sleep (2)
print "APRS Login reply:", sock_file.readline()


# Initialise libfap.py for parsing returned lines
print "libfap_init"
libfap.fap_init()
start_time = time.time()
local_time = datetime.now()
keepalive_count = 1
keepalive_time = time.time()
alive(config.DBpath+APP, first='yes')
#
#-----------------------------------------------------------------
# Initialise API for SPIDER & SPOT & LT24
#-----------------------------------------------------------------
#
now=datetime.utcnow()			# get the UTC time
min5=timedelta(seconds=300)		# 5 minutes ago
now=now-min5				# now less 5 minutes
td=now-datetime(1970,1,1)         	# number of seconds until beginning of the day 1-1-1970
ts=int(td.total_seconds())		# Unix time - seconds from the epoch
tc=ts					# init the variables
ty=ts
lt24ts=ts
spispotcount=0				# loop counter
ttime=now.strftime("%Y-%m-%dT%H:%M:%SZ")# format required by SPIDER

if LT24:
	lt24login(LT24path, lt24username, lt24password)	# login into the LiveTrack24 server
	lt24ts=ts
	LT24firsttime=True


if SPIDER or SPOT or CAPTURS or LT24:
	print spispotcount, "---> Initial TTime:", ttime, "Unix time:", ts, "UTC:", datetime.utcnow().isoformat()

date = datetime.now()

try:

    while True:
        current_time = time.time()
        local_time = datetime.now()
        elapsed_time = current_time - keepalive_time	# time since last keep_alive
        if (current_time - keepalive_time) > 180:      	# keepalives every 3 mins
		alive(config.DBpath+APP)               	# and mark that we are still alive
                run_time = time.time() - start_time
                keepalive_time = current_time
                keepalive_count = keepalive_count + 1	# just a control
	now=datetime.utcnow()				# get the UTC time
	try:
                rtn = sock_file.write("#Python ogn aprspush App\n\n")
                # Make sure keepalive gets sent. If not flushed then buffered
                sock_file.flush()
        except Exception, e:
                print ('Something\'s wrong with socket write. Exception type is %s' % (`e`))
		now=datetime.utcnow()			# get the UTC time
		print "UTC time is now: ", now
        try:						# lets see if we have data from the interface functionns: SPIDER, SPOT, LT24 or SKYLINES
		if  (spispotcount % 30) == 0:		# every 5 minutes
			if SPIDER:			# if we have SPIDER according with the config
				ttime=spifindspiderpos(ttime, conn, spiusername, spipassword, spisysid, prt=prt, store=False, aprspush=True)
			else:
				ttime=now.strftime("%Y-%m-%dT%H:%M:%SZ")# format required by SPIDER

			if SPOT:			# if we have the SPOT according with the configuration
				ts   =spotfindpos(ts, conn, prt=prt, store=False, aprspush=True)
			else:
				td=now-datetime(1970,1,1)      	# number of second until beginning of the day
				ts=int(td.total_seconds())	# Unix time - seconds from the epoch

		if CAPTURS:				# if we have the CAPTURS according with the configuration
			tc   =captfindpos(tc, conn, prt=prt, store=False)
		else:
			td=now-datetime(1970,1,1)      	# number of second until beginning of the day
			tc=int(td.total_seconds())	# Unix time - seconds from the epoch

		if SKYLINE:				# if we have the SPOT according with the configuration
			ty   =skylfindpos(ty, conn, prt=prt, store=False)
		else:
			td=now-datetime(1970,1,1)      	# number of second until beginning of the day
			ty=int(td.total_seconds())	# Unix time - seconds from the epoch
		if LT24:				# if we have the LT24 according with the configuration
			lt24ts   =lt24findpos(lt24ts, conn, LT24firsttime, prt=prt, store=False, aprspush=True) # find the position and add it to the DDBB
			LT24firsttime=False		# only once the addpos
		else:
			td=now-datetime(1970,1,1)      	# number of second until beginning of the day
			lt24ts=int(td.total_seconds())	# Unix time - seconds from the epoch

		spispotcount += 1			# we report a counter of calls to the interfaces

		if SPIDER or SPOT or LT24 or SKYLINE or CAPTURS:

			print spispotcount, "---> SPIDER TTime:", ttime, "SPOT Unix time:", ts, prttime(ts), "Tcapt", prttime(tc), "Tskyl", prttime(ty), "LT24 Unix time", prttime(lt24ts), "UTC Now:", datetime.utcnow().isoformat()


	except Exception, e:
                        print ('Something\'s wrong with interface functions Exception type is %s' % (`e`))
			if SPIDER or SPOT or LT24 or SKYLINE or CAPTURS:

				print spispotcount, "ERROR ---> TTime:", ttime, "SPOT Unix time:", ts, "LT24 Unix time", lt24ts, "UTC Now:", datetime.utcnow().isoformat()
	sleep (SLEEP)					# sleep n seconds


except KeyboardInterrupt:
    print "Keyboard input received, ignore"
    pass

shutdown(sock)
print "Exit now ...", err
exit(1)
