#!/usr/bin/python
from datetime import datetime, timedelta
import MySQLdb
import socket
import signal

#########################################################################
def alive(first='no'):				# routine to indicate that we are alive

        if (first == 'yes'):
                alivefile = open (config.DBpath+"SPISPOT.alive", 'w') # create a file just to mark that we are alive
        else:
                alivefile = open (config.DBpath+"SPISPOT.alive", 'a') # append a file just to mark that we are alive
        local_time = datetime.now()
        alivetime = local_time.strftime("%y-%m-%d %H:%M:%S")
        alivefile.write(alivetime+"\n") # write the time as control
        alivefile.close()               # close the alive file
#########################################################################
#########################################################################
def shutdown():               			# shutdown routine, close files and report on activity
                                                                                # shutdown before exit
        print 'SHUTDOWN: Records read:',count
        conn.commit()                   	# commit the DB updates
        conn.close()                    	# close the database
        local_time = datetime.now() 		# report date and time now
        print "Time now:", local_time, " Local time."
	if os.path.exists("./SPISPOT.alive"):
        	os.remove(  "SPISPOT.alive")   	# delete the mark of being alive
        return                          	# job done

#########################################################################

#########################################################################
#########################################################################

def signal_term_handler(signal, frame):		# signal handler
    print 'got SIGTERM ... shutdown orderly'
    shutdown()					# invoke shutdown 
    sys.exit(0)

# ......................................................................#
signal.signal(signal.SIGTERM, signal_term_handler)
# ......................................................................#



print "Start SPIDER, SPOT & LT24 logging  V1.3"
print "======================================="

import config

# --------------------------------------#
#
# get the SPIDER TRACK SPOT and TL24 information
#
# --------------------------------------#
DBpath   =config.DBpath
DBhost   =config.DBhost
DBuser   =config.DBuser
DBpasswd =config.DBpasswd
DBname   =config.DBname
SPIDER   =config.SPIDER
SPOT     =config.SPOT  
LT24     =config.LT24  
SKYLINE  =config.SKYLINE
SKYLINE=True
if SPIDER:
	from spifuncs import *
	spiusername =config.SPIuser  
	spipassword =config.SPIpassword  

if SPOT:
	from spotfuncs import *

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

if SKYLINE:
	from skylfuncs import *
# --------------------------------------#

conn=MySQLdb.connect(host=DBhost, user=DBuser, passwd=DBpasswd, db=DBname)
curs=conn.cursor()                      # set the cursor
date=datetime.utcnow()         		# get the date

print "MySQL: Database:", DBname, " at Host:", DBhost, "SPIDER:", SPIDER, "SPOT:", SPOT, "LT24", LT24, "SKYLINE", SKYLINE
print "Date: ", date, "UTC on:", socket.gethostname()
date = datetime.now()
print "Time now is: ", date, " Local time"

alive("yes")

now=datetime.utcnow()			# get the UTC time
min5=timedelta(seconds=300)		# 5 minutes ago
now=now-min5
ttime=now.strftime("%Y-%m-%dT%H:%M:%SZ")# format required by SPIDER
count=1					# loop counter
td=now-datetime(1970,1,1)         	# number of seconds until beginning of the day 1-1-1970
ts=int(td.total_seconds())		# Unix time - seconds from the epoch
skylts=ts
if LT24:
	lt24login(LT24path, lt24username, lt24password)	# login into the LiveTrack24 server
	lt24ts=ts
	LT24firsttime=True

print count, "---> TTime:", ttime, "Unix time:", ts, "UTC:", datetime.utcnow().isoformat()
while True:				# until 22:00 h
	now=datetime.utcnow()	# get the UTC time
	if SPIDER:			# if we have SPIDER according with the config
		print ">>>>>>>>>>>>>>>>>>>> SPIDER <<<<<<<<<<<<<<<<<"
		ttime=spifindspiderpos(ttime, conn, spiusername, spipassword, prt=True)
	else: 
		ttime=now.strftime("%Y-%m-%dT%H:%M:%SZ")# format required by SPIDER

	if SPOT:			# if we have the SPOT according with the configuration
		print ">>>>>>>>>>>>>>>>>>>> SPOT <<<<<<<<<<<<<<<<<"
		ts   =spotfindpos(ts, conn, prt=True)
	else:
		td=now-datetime(1970,1,1)      	# number of second until beginning of the day
		ts=int(td.total_seconds())	# Unix time - seconds from the epoch

	if LT24:			# if we have the LT24 according with the configuration
		
		print ">>>>>>>>>>>>>>>>>>>> LT24 <<<<<<<<<<<<<<<<<"
		lt24ts   =lt24findpos(lt24ts, conn, LT24firsttime, prt=True)
		LT24firsttime=False	# only once the addpos
	else:
		td=now-datetime(1970,1,1)      	# number of second until beginning of the day
		lt24ts=int(td.total_seconds())	# Unix time - seconds from the epoch

	if SKYLINE:			# if we have the SPOT according with the configuration
		print ">>>>>>>>>>>>>>>>>>>> SKYLINES <<<<<<<<<<<<<<<<<"
		ts   =skylfindpos(skylts, conn, prt=True)
	else:
		td=now-datetime(1970,1,1)      	# number of second until beginning of the day
		skylts=int(td.total_seconds())	# Unix time - seconds from the epoch
	time.sleep(300)  		# sleep for 5 minutes
	count += 1
	print count, "---> TTime:", ttime, "SPOT Unix time:", ts, "Z: LT24 Unix time", lt24ts, datetime.utcnow().isoformat()

	alive()				# indicate that we are still alive
	local_time = datetime.now()	# check the local time
        if local_time.hour >= 21:	# at 21:00 finish
		break
print "End of day ... Time is now:", local_time
shutdown()

sys.exit(1)
