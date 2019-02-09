#!/usr/bin/python
from inreachfuncs import *
from datetime import *
import time
import MySQLdb
import socket
import config

programver="1.0"
print "Start InReach logging", programver
print "==========================="

#
# get the SPIDER TRACK information
#
DBhost   =config.DBhost
DBuser   =config.DBuser
DBpasswd =config.DBpasswd
DBname   =config.DBname
SPIDER   =config.SPIDER
SPOT     =config.SPOT
INREACH  =config.INREACH
# --------------------------------------#
# create socket & connect to server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((config.APRS_SERVER_HOST, config.APRS_SERVER_PORT))
print "Socket sock connected to: ", config.APRS_SERVER_HOST, ":", config.APRS_SERVER_PORT

# logon to OGN APRS network

login = 'user %s pass %s vers TestInReach %s %s'  % ("TINREACH", "28656" , programver, "\n")
sock.send(login)

# Make the connection to the server
sock_file = sock.makefile()

config.SOCK=sock
config.SOCK_FILE=sock_file
print "APRS Version:", sock_file.readline()
time.sleep (2)
print "APRS Login request:", login
print "APRS Login reply:  ", sock_file.readline()


# --------------------------------------#
conn=MySQLdb.connect(host=DBhost, user=DBuser, passwd=DBpasswd, db=DBname)
curs=conn.cursor()             # set the cursor
date=datetime.utcnow()         # get the date

print "MySQL: Database:", DBname, " at Host:", DBhost
print "Date: ", date, "UTC on:", socket.gethostname()
date = datetime.now()
print "Time now is: ", date, " as local time"

now=datetime.utcnow()           # UTC time now
min5=timedelta(seconds=300)     # less 5 minutes
now=now-min5                    # this is the START time now - 5 minutes
ttime=now.strftime("%Y-%m-%dT%H:%M:%SZ") # convert it to ISO format
count=1
td=now-datetime(1970,1,1)       # number of second until beginning of the epoch
ts=int(td.total_seconds())      # UNIX time
print "Count=", count, "---> Now=", ttime, "TS=", ts # print it as control
ts=0
while True:
	ts=inreachfindpos(ts, conn, prt=False, aprspush=True)
	time.sleep(300)  
	now=datetime.utcnow()
	count += 1
        ttime=now.isoformat()
        print "Count=", count, "---> Now=", ttime, "TS=", ts 

