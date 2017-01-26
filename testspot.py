#!/usr/bin/python
from datetime import datetime, timedelta
from spotfuncs import *
import MySQLdb
import socket
import config

print "Start SPOT logging  V1.0"
print "========================"

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
date=datetime.utcnow()         # get the date

print "MySQL: Database:", DBname, " at Host:", DBhost
print "Date: ", date, "UTC on:", socket.gethostname()
date = datetime.now()
print "Time now is: ", date, " Local time"

now=datetime.utcnow()
min5=timedelta(seconds=300)
now=now-min5
ttime=now.strftime("%Y-%m-%dT%H:%M:%SZ")
count=1
td=now-datetime(1970,1,1)         # number of second until beginning of the day
ts=int(td.total_seconds())
print count, "--->", ttime, ts
while True:
	ts=spotfindpos(ts, conn)
	time.sleep(300)  
	now=datetime.utcnow()
	td=now-datetime(1970,1,1)         # number of second until beginning of the day
	count += 1
	ttime=now.strftime("%Y-%m-%dT%H:%M:%SZ")
	print count, "--->", ttime, ts

