#!/usr/bin/python3

# --------------------------------------------------------------------------------------------- #
#
# Python code to push into the OGN APRS the data from SPOT/SPIDER/CAPTURS/LT24/SKYLINES/AvioniX
#
# --------------------------------------------------------------------------------------------- #

import config                           # get the configuration data
from datetime import datetime, timedelta
from ctypes import *
import socket
import time
import sys
import os
import os.path
import signal
import atexit
from parserfuncs import alive           			# the ogn/ham parser functions
from time import sleep                  			# use the sleep function
from flarmfuncs import *		        		# import the functions delaing with the Flarm ID
from dtfuncs import naive_utcnow, naive_utcfromtimestamp        # import the naive version of utcnow()
import argparse
import traceback

#########################################################################


def shutdown(sock, count=-1):		        # shutdown routine, close files and report on activity
    # shutdown before exit
    try:
        sock.shutdown(0)                # shutdown the connection
        sock.close()                    # close the connection file
    except Exception as e:
        print("Socket error...", e, "ignored \n")
    if conn and conn != None:
        try:
           conn.commit()                # commit the DB updates
           conn.close()                 # close the database
        except:
           print("Error closing database ... no problem at this shutdown time...")
    if AVX:
        avxfinish(avxcnt)
    local_time = datetime.now()         # report date and time now
    print("Shutdown now, Time now:", local_time, " Local time. Count:", count)
    if os.path.exists(config.DBpath+"PUSH2OGN.alive"):
        				# delete the mark of being alive
        os.remove(config.DBpath+"PUSH2OGN.alive")
    return                              # job done


#########################################################################


def signal_term_handler(signal, frame):
    print('got SIGTERM ... shutdown orderly')
    if ENA:
       enafinish(True, True)
    shutdown(sock) 			# shutdown orderly
    sys.exit(0)

#########################################################################

# ......................................................................#
signal.signal(signal.SIGTERM, signal_term_handler)
# ......................................................................#


def prttime(unixtime):
    # get the time from the timestamp
    tme = naive_utcfromtimestamp(unixtime)
    return(tme.strftime("%H%M%S"))			# the time


#
#########################################################################
#########################################################################
#


programver = 'V2.6'					# June 2024

print("\n\nStart PUSH2OGN: "+programver)
print(    "=====================")

print("Program Version:", time.ctime(os.path.getmtime(__file__)))
print("==========================================")
import platform
print("Python version:", platform.python_version())
date = naive_utcnow()         		# get the date
dte = date.strftime("%y%m%d")             # today's date
print("\nDate: ", date, "UTC on SERVER:", socket.gethostname(), "Process ID:", os.getpid())
date = datetime.now()                   # local time
print("Time now is: ", date, " Local time")

#
# --------------------------------------#
#
# get the SPIDER TRACK  & SPOT & InReach & ADSB ... information
#
# --------------------------------------#
#
APP = "PUSH2OGN"		# the application name
SLEEP = 10			# sleep 10 seconds in between calls to the APRS
nerrors = 0			# number of errors in *funcs found
day = 0				# day of running
TimeSPOTSPIDERINREACH = 300     # time in second from each run
TimeCAPTUR            = 150    	# time in second from each run
TimeLT24SKYL          = 60     	# time in second from each run
TimeADSB              = SLEEP	# time in second from each run
TimeAVX               = 5  	# time in second from each run
TimeENA		      = 0 	# the waiting is whitin the run

# --------------------------------------#
DBpath = config.DBpath
DBhost = config.DBhost
DBuser = config.DBuser
DBpasswd = config.DBpasswd
DBname = config.DBname
# we force everything TRUE as we try to push to the APRS
OGNT = True
parser = argparse.ArgumentParser(description="OGN push to the APRS network and store it on the MySQL database")
parser.add_argument('-p', '--print', required=False,
                    dest='prt', action='store', default=False)
parser.add_argument('-r', '--SPIDER', required=False,
                    dest='SPIDER', action='store', default=False)
parser.add_argument('-s', '--SPOT', required=False,
                    dest='SPOT', action='store', default=False)
parser.add_argument('-i', '--INREACH', required=False,
                    dest='INREACH', action='store', default=False)
parser.add_argument('-k', '--SKYLINE', required=False,
                    dest='SKYLINE', action='store', default=False)
parser.add_argument('-c', '--CAPTURS', required=False,
                    dest='CAPTURS', action='store', default=False)
parser.add_argument('-l', '--LT24', required=False,
                    dest='LT24', action='store', default=False)
parser.add_argument('-a', '--ADSB', required=False,
                    dest='ADSB', action='store', default=False)
parser.add_argument('-u', '--USEDDB', required=False,
                    dest='USEDDB', action='store', default=False)
parser.add_argument('-x', '--AVX', required=False,
                    dest='AVX', action='store', default=False)
parser.add_argument('-e', '--ENA', required=False,
                    dest='ENA', action='store', default=False)

args 	= parser.parse_args()
prt 	= args.prt			# print on|off
SPIDER 	= args.SPIDER
SPOT 	= args.SPOT
INREACH = args.INREACH
CAPTURS = args.CAPTURS
SKYLINE = args.SKYLINE
LT24 	= args.LT24
ADSB 	= args.ADSB
USEDDB  = args.USEDDB
AVX     = args.AVX
ENA     = args.ENA
# --------------------------------------#
if os.path.exists(config.PIDfile+".PUSH2OGN"):
    raise RuntimeError("APRSpush already running !!!")
    exit(-1)

print("Setup: \nPRINT:", prt, "\nSPIDER:", SPIDER, "\nSPOT:", SPOT, "\nINREACH:", INREACH, "\nCAPTURS:", CAPTURS, "\nSKLYLINE:", SKYLINE, "\nLT24:", LT24, "\nADSB:", ADSB, "\nAVX:", AVX, "\nENA:", ENA, "\n")
# --------------------------------------#

if SPIDER:
    from spifuncs import *
    spiusername = config.SPIuser
    spipassword = config.SPIpassword
    spisysid    = config.SPISYSid

if SPOT:
    from spotfuncs import *

if INREACH:
    from inreachfuncs import *

if CAPTURS:
    from captfuncs import *

if SKYLINE:
    from skylfuncs import *

if ADSB:
    from adsbfuncs import getsizeadsbcache, adsbsetrec
    from adsbfuncs import *
    SLEEP = 5
    
    adsbini(prt=prt, aprspush=True)			# init the process

if LT24:
    from lt24funcs import lt24login
    from lt24funcs import *
    lt24username = config.LT24username
    lt24password = config.LT24password
    LT24qwe = " "
    LT24_appSecret = " "
    LT24_appKey = " "
    LT24path = DBpath+"LT24/"
    LT24login = False
    LT24firsttime = True
if AVX:
    from avxfuncs import *
    avxini(prt=prt, aprspush=True)			# init the process
    avxcnt=0
    SLEEP=5
if ENA:
    from enafuncs import enasetrec
    from enafuncs import *
    enaini(prt=prt, aprspush=True)			# init the Mosquitto
    sleep(2)				# give a chance
    print ("MQTT initialized...\n")
    SLEEP = 0				# no sleep when MQTT


# --------------------------------------#


# -----------------------------------------------------------------#

if not USEDDB:
    import MySQLdb                          # the SQL data base routines^M
    conn = MySQLdb.connect(host=DBhost, user=DBuser, passwd=DBpasswd, db=DBname)
    print("MySQL: Database:", DBname, " at Host:", DBhost)
else:
    print("Using the OGN DDB.")
    conn = False

#----------------------pus2ogn.py start-----------------------#

prtreq = sys.argv[1:]              # check if the prt arg is there
if prtreq and prtreq[0] == 'prt':
    prt = True
else:
    prt = False

with open(config.PIDfile+".PUSH2OGN", "w") as f:  # set the lock file  as the pid
    f.write(str(os.getpid()))
    f.close()
atexit.register(lambda: os.remove(config.PIDfile+".PUSH2OGN"))

# create socket & connect to server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((config.APRS_SERVER_PUSH, config.APRS_SERVER_PORT))
print("Socket sock connected to: ", config.APRS_SERVER_PUSH, ":", config.APRS_SERVER_PORT)

# logon to OGN APRS network

login = 'user %s pass %s vers PUSH2OGN %s %s' % (config.APRS_USER_PUSH, config.APRS_PASSCODE_PUSH, programver, "\n")
login=login.encode(encoding='utf-8', errors='strict')
sock.send(login)

# Make the connection to the server
sock_file = sock.makefile(mode='rw')    # make read/write as we need to send the keep_alive

config.SOCK = sock
config.SOCK_FILE = sock_file
print("APRS Version:", sock_file.readline())
sleep(2)
print("APRS Login request:", login)
print("APRS Login reply:  ", sock_file.readline())


start_time = time.time()
local_time = datetime.now()
keepalive_count = 1
keepalive_time = time.time()
alive(config.DBpath+APP, first='yes')
#
#-----------------------------------------------------------------#
# Initialise API for SPIDER & SPOT & INREACH & LT24
#-----------------------------------------------------------------#
#
now  = naive_utcnow()		# get the UTC time
min5 = timedelta(seconds=300)		# 5 minutes ago
now  = now-min5				# now less 5 minutes
# number of seconds until beginning of the day 1-1-1970
td = now-datetime(1970, 1, 1)
ts = int(td.total_seconds())		# Unix time - seconds from the epoch
tc = ts					# for capturs
ty = ts					# for skylines
tr = ts					# for inReach
ttspid = 0				# time between spid request
ttcapt = 0				# time between capturs request
ttltsk = 0				# time between lt24/skyl request
lt24ts = ts                             # the same
adsbts = ts                             # the same
avxts  = ts                             # the same
spispotcount = 0			# loop counter
ttime = now.strftime("%Y-%m-%dT%H:%M:%SZ")  # format required by SPIDER

day = now.day				# day of the month
print("Time between calls for SPOT/SPIDER/INREACH:", TimeSPOTSPIDERINREACH, "for CAPTUR:", TimeCAPTUR, "for LT24/SKYLINES:", TimeLT24SKYL, "for ADSB:", SLEEP, "for AVX:", TimeAVX, "for ENA:", TimeENA, "\n\n")
if LT24:
    # login into the LiveTrack24 server
    lt24login(LT24path, lt24username, lt24password)
    lt24ts = ts
    LT24firsttime = True


if SPIDER or SPOT or INREACH or CAPTURS or LT24 or ADSB or AVX or ENA:
    print(spispotcount, "---> Initial TTime:", ttime, "Unix time:", ts, "UTC:", naive_utcnow().isoformat())


date = datetime.now()

try:

    while True:
        func='NONE'
        current_time = time.time()
        local_time = datetime.now()
        elapsed_time = current_time - keepalive_time    # time since last keep_alive
        if (current_time - keepalive_time) > 180:      	# keepalives every 3 mins
            # and mark that we are still alive
            alive(config.DBpath+APP)
            run_time = time.time() - start_time
            keepalive_time = current_time
            keepalive_count = keepalive_count + 1       # just a control

            try:					# lets send a message to the APRS for keep alive
                rtn = sock_file.write("#Python ogn aprspush App\n\n")
							# in addition if ADSB or AVX send the position of the dummy receiver
                if ADSB:
                    func='ADSB'
                    adsbsetrec(sock_file, prt=prt, store=False, aprspush=True)
                if AVX:
                    func='AVX'
                    avxsetrec(sock_file, prt=prt, store=False, aprspush=True)
                if ENA:
                    func='ENA'
                    enasetrec(sock_file, prt=prt, store=False, aprspush=True)
                sock_file.flush()		        # Make sure keepalive gets sent. If not flushed then buffered

            except Exception as e:
                print((
                    'Something\'s wrong with socket write. Exception type is %s' % (repr(e))))
                now = naive_utcnow()		        # get the UTC time
                print("UTC time is now: ", now, keepalive_count, run_time)

        now = naive_utcnow()				# get the UTC time
        # number of second until beginning of the epoch
        tt = int((now-datetime(1970, 1, 1)).total_seconds())
        if now.day != day:				# check if day has changed
            print("End of Day...")
            if ENA:
               enafinish(prt=prt, aprspush=True)  	# get the data from Mosquitto and process it         
                         				# recycle
            shutdown(sock, spispotcount)
            print(".............")
            exit(0)
        try:						# lets see if we have data from the interface functionns: SPIDER, SPOT, LT24 or SKYLINES
            if (tt - ttspid) >TimeSPOTSPIDERINREACH:    # every 5 minutes for SPIDER, SPOT, INREACH
                if SPIDER:			        # if we have SPIDER according with the config
                    func='SPIDER'
                    ttime = spifindspiderpos(ttime, conn, spiusername, spipassword, spisysid, prt=prt, store=False, aprspush=True)
                else:
                    					# format required by SPIDER
                    ttime = now.strftime("%Y-%m-%dT%H:%M:%SZ")

                if SPOT:			        # if we have the SPOT according with the configuration
                    func='SPOT'
                    ts = spotfindpos(ts, conn, prt=prt, store=False, aprspush=True)
                else:
                    					# number of second until beginning of the day
                    td = now-datetime(1970, 1, 1) 	# Unix time - seconds from the epoch
                    ts = int(td.total_seconds())
                if INREACH:			        # if we have the INREACH according with the configuration
                    func='INREACH'
                    tr = inreachfindpos(tr, conn, prt=prt, store=False, aprspush=True)
                else:
                    					# number of second until beginning of the day
                    td = now-datetime(1970, 1, 1) 	# Unix time - seconds from the epoch
                    tr = int(td.total_seconds())
                ttspid = tt

            if (tt - ttcapt) > TimeCAPTUR:		# every 2.5 minutes for CAPTUR
                if CAPTURS:			        # if we have the CAPTURS according with the configuration
                    func='CAPTUR'
                    tc = captfindpos(tc, conn, prt=prt, store=False, aprspush=True)
                else:
                    					# number of second until beginning of the day
                    td = now-datetime(1970, 1, 1) 	# Unix time - seconds from the epoch
                    tc = int(td.total_seconds())
                ttcapt = tt

            if (tt - ttltsk) > TimeLT24SKYL:		# every 1 minutes for LT24SKYL
                if SKYLINE:				# if we have the SKYLINE according with the configuration
                    func='SKYLINE'
                    ty = skylfindpos(ty, conn, prt=prt, store=False, aprspush=True)
                else:
                    					# number of second until beginning of the day
                    td = now-datetime(1970, 1, 1) 	# Unix time - seconds from the epoch
                    ty = int(td.total_seconds())
                if LT24:				# if we have the LT24 according with the configuration
                    					# find the position and add it to the DDBB
                    func='LT24'
                    lt24ts = lt24findpos(lt24ts, conn, LT24firsttime, prt=prt, store=False, aprspush=True)
                    LT24firsttime = False		# only once the addpos
                else:
                    					# number of second until beginning of the day
                    td = now-datetime(1970, 1, 1) 	# Unix time - seconds from the epoch
                    lt24ts = int(td.total_seconds())
                ttltsk = tt

            if ADSB:					# if we have the ADSB according with the configuration
                					# find the position and add it to the DDBB or APRS
                func='ADSB'
                adsbts = adsbfindpos(adsbts, conn, prt=prt, store=False, aprspush=True)
            else:
                					# number of second until beginning of the day
                td = now-datetime(1970, 1, 1) 		# Unix time - seconds from the epoch
                adsbts = int(td.total_seconds())

            if AVX:					# if we have the ADSB/AVX according with the configuration
                					# find the position and add it to the DDBB
                func='AVX'
                (avxts,cnt) = avxfindpos(avxts, conn, prt=prt, store=False, aprspush=True)
                avxcnt += cnt				# count the number of APRS messages
            else:
                					# number of second until beginning of the day
                td = now-datetime(1970, 1, 1) 		# Unix time - seconds from the epoch
                avxts = int(td.total_seconds())

            if ENA:					# enaire interface

                now = naive_utcnow()			# get the UTC time
                enarun(prt=prt, aprspush=True)  	# get the data from Mosquitto and process it         
                now = naive_utcnow()			# get the UTC time

            spispotcount += 1			        # we report a counter of calls to the interfaces

            if SPIDER or SPOT or INREACH or LT24 or SKYLINE or CAPTURS or ADSB or AVX or ENA:
                if prt:
                   print(spispotcount, "---> CONTROL: Spider TTime:", ttime, "SPOT Unix time:", ts, prttime(ts), "TinReach", tr, "Tcapt", prttime(
                    tc), "Tskyl", prttime(ty), "LT24 Unix time", prttime(lt24ts), "ADSB time", adsbts, "UTC Now:", naive_utcnow().isoformat())
            if (ADSB or AVX or ENA) and spispotcount % 10000 == 0:

                print("ADSB Cache size", getsizeadsbcache())
                if AVX:
                   print ("AVX PUSH messages:", avxcnt)

        except Exception as e:
            print(traceback.format_exc())
            print(('Something\'s wrong with interface function '+func+' Exception type is %s' % (repr(e))))

            if SPIDER or SPOT or INREACH or LT24 or SKYLINE or CAPTURS or ADSB or AVX:
                print(spispotcount, "ERROR ---> TTime:", ttime, "SPOT Unix time:", ts, "LT24 Unix time", lt24ts, "UTC Now:", naive_utcnow().isoformat())

            nerrors += 1
            if nerrors > 100:
                if ENA:
                   enafinish(prt=prt, aprspush=True)  	# get the data from Mosquitto and process it         
                shutdown(sock, spispotcount)            # way to many errors
                sys.exit(-1)		                # and bye ...
							# end of except
        sys.stdout.flush()				# flush the print messages
        sleep(SLEEP)					# sleep n seconds


except KeyboardInterrupt:
    print("Keyboard input received, ignore")
    pass

if ENA:
   enafinish(prt=prt, aprspush=True)  	# get the data from Mosquitto and process it         
shutdown(sock, spispotcount)

print("Exit now ...", nerrors)
exit(0)
