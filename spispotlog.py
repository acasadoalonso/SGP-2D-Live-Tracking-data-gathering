#!/usr/bin/python
from datetime import datetime, timedelta
from spifuncs import *
from spotfuncs import *
import MySQLdb
import socket
import config
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
        print 'Records read:',count
        conn.commit()                   	# commit the DB updates
        conn.close()                    	# close the database
        local_time = datetime.now() 		# report date and time now
        print "Time now:", local_time, " Local time."
        os.remove("SPISPOT.alive")         	# delete the mark of being alive
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



print "Start SPIDER & SPOT logging  V1.1"
print "================================="

#
# get the SPIDER TRACK information
#
# --------------------------------------#
DBhost   =config.DBhost
DBuser   =config.DBuser
DBpasswd =config.DBpasswd
DBname   =config.DBname
SPIDER   =config.SPIDER
SPOT     =config.SPOT  
# --------------------------------------#
conn=MySQLdb.connect(host=DBhost, user=DBuser, passwd=DBpasswd, db=DBname)
curs=conn.cursor()                      # set the cursor
date=datetime.utcnow()         		# get the date

print "MySQL: Database:", DBname, " at Host:", DBhost, "SPIDER:", SPIDER, "SPOT:", SPOT
print "Date: ", date, "UTC on:", socket.gethostname()
date = datetime.now()
print "Time now is: ", date, " Local time"

alive("yes")

now=datetime.utcnow()			# get the UTC time
min5=timedelta(seconds=300)		# 5 minutes ago
now=now-min5
ttime=now.strftime("%Y-%m-%dT%H:%M:%SZ")# format required by SPIDER
count=1					# loop counter
td=now-datetime(1970,1,1)         	# number of second until beginning of the day
ts=int(td.total_seconds())		# Unix time - seconds from the epoch
print count, "---> TTime:", ttime, "Unix time:", ts, "UTC:", datetime.utcnow().isoformat()
while True:				# until 22:00 h
	if SPIDER:			# if we have SPIDER according with the config

		ttime=spifindspiderpos(ttime, conn)
	if SPOT:			# if we have the SPOT according with the configuration

		ts   =spotfindpos(ts, conn)

	time.sleep(300)  		# sleep for 5 minutes
	count += 1
	print count, "---> TTime:", ttime, "Unix time:", ts, "UTC:", datetime.utcnow().isoformat()

	alive()				# indicate that we are still alive
	local_time = datetime.now()	# check the local time
        if local_time.hour == 21:	# at 22:00 finish
		break
print "Time is now:", local_time
shutdown()

sys.exit(1)
