#!/usr/bin/python
from datetime import datetime, timedelta
from spifuncs import *
from spotfuncs import *
import MySQLdb
import socket
import config

print "Start SPIDER & SPOT logging  V1.0"
print "================================="

#
# get the SPIDER TRACK information
#
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

now=datetime.utcnow()			# get the UTC time
min5=timedelta(seconds=300)		# 5 minutes ago
now=now-min5
ttime=now.strftime("%Y-%m-%dT%H:%M:%SZ")# format required by SPIDER
count=1					# loop counter
td=now-datetime(1970,1,1)         	# number of second until beginning of the day
ts=int(td.total_seconds())		# Unix time - seconds from the epoch
print count, "---> Ttime:", ttime, "Unix time:", ts, "UTC:", datetime.utcnow().isoformat()
while True:				# until 22:00 h
	if SPIDER:			# if we have SPIDER according with the config

		ttime=spifindspiderpos(ttime, conn)
	if SPOT:			# if we have the SPOT according with the configuration

		ts   =spotfindpos(ts, conn)

	time.sleep(300)  		# sleep for 5 minutes
	count += 1
	print count, "---> Ttime:", ttime, "Unix time:", ts, "UTC:", datetime.utcnow().isoformat()
	local_time = datetime.now()	# check the local time

        if local_time.hour == 22:	# at 22:00 finish
		break
print local_time


