import sys
import os
import MySQLdb
import datetime
import urllib.parse
from  ognddbfuncs import *
import config

#
#   This script set the pairing between OGN trackers and flarms that are on the same glider, so it become a virtual single device
#

action='list'								# set the defaults
trk='ALL'
#print (sys.argv)
if len(sys.argv) >1:							# first arg is the action
	arg1 = sys.argv[1]
	action = arg1[0:]				
if len(sys.argv) >2:							# second is the trackid 
	arg2 = sys.argv[2]
	trk = arg2[0:9].upper()
#print (len(sys.argv), "Action=", action, "Tracker=", trk )

localtime = datetime.datetime.now()					# get today's date
today    = localtime.strftime("%y/%m/%d %H:%M:%S")			# in string format yymmdd
DBpath   = config.DBpath						# use the configuration DB path
DBname   = config.DBname						# use the configuration DB name
DBname   ='APRSLOG'							# database always APRSLOG
DBtable  ='TRKSTATUS'							# table name
if os.path.exists("./img/ogn-logo-150x150.png"):
   html1 = """<head><meta charset="UTF-8"><meta http-equiv="refresh" content="30" > </head><TITLE>TRACKERs Status</TITLE> <IMG src="./img/ogn-logo-150x150.png" border=1 alt=[image]><H1>WGC CAT I Trackers STATUS: </H1> <HR> <P>Today is:  %s and we have %d trackers on TRKDEVICES table.  <br /> <br /> <br /> </p> </HR> """
else:
   html1 = """<head><meta charset="UTF-8"><meta http-equiv="refresh" content="30" > </head><TITLE>TRACKERs Status</TITLE> <IMG src="./node/img/ogn-logo-150x150.png" border=1 alt=[image]><H1>WGC CAT I Trackers STATUS: </H1> <HR> <P>Today is:  %s and we have %d trackers on TRKDEVICES table.  <br /> <br /> <br /> </p> </HR> """

html2 = """<center><table><tr><td><pre>"""
html3 = """</pre></td></tr></table></center>"""

#
conn = MySQLdb.connect(host=config.DBhost, user=config.DBuser, passwd=config.DBpasswd, db=DBname, connect_timeout=1000)     # connect with the database
curs = conn.cursor()				# connect with the DB set the cursor

#
# get the counter of trackers pairs active
#
sql1 = "SELECT COUNT(*) FROM TRKDEVICES WHERE devicetype = 'OGNT' AND active = 1;"
try:
        curs.execute(sql1)
except MySQLdb.Error as e:
        print ("SQL error: ",e)
row = curs.fetchone()
nrecs=row[0]					# number of trackers pairs active

sql0="SELECT   COUNT(DISTINCT(id)) FROM OGNTRKSTATUS ;"
cmd0="SELECT   COUNT(*) FROM OGNTRKSTATUS ;"
cmd1="SELECT * FROM OGNTRKSTATUS where source = 'STAT' and id in (select id from TRKDEVICES where active = 1 and devicetype = 'OGNT') ORDER BY otime DESC;"
cmd2="SELECT * FROM OGNTRKSTATUS where source = 'STAT' and id = '"+trk+"' ORDER BY otime DESC;"
cmd3="SELECT * FROM OGNTRKSTATUS ORDER BY otime DESC;"
cmd4="SELECT DISTINCT (id) FROM `OGNTRKSTATUS`;" 
try:
        curs.execute(sql0)			# get the number of trackers seen
except MySQLdb.Error as e:
        print ("SQL error: ",e)
cnt=curs.fetchone()
try:
        curs.execute(cmd0)			# get the number of records on the TRK STAUS table
except MySQLdb.Error as e:
        print ("SQL error: ",e)
row=curs.fetchone()
print ("Number of records on TRKSTATUS table:", row[0], " as today: ", today , " from ", cnt[0], " trackers </br>")	# number of records on the table

if trk == 'ALL':
        if action == 'full':
           cmd = cmd3				# if all the trackers
        elif action == 'lastfix':
           cmd = cmd4				# if all the trackers
        else:
           cmd = cmd1				# if only the active trackers
else:
	cmd = cmd2 				# if looking for an specific TRACK ID
#print (cmd)
try:
        curs.execute(cmd)			# get the info from OGNTRKSTATUS table
except MySQLdb.Error as e:
        print ("SQL error: ",e)
trks={}						# the list of trackers and its counters
trkt={}						# the list of trackers and the last OTIME
print (html1% (today,nrecs))			# report data and number of pairs
print (html2)
print ("<b> <a>TRKDEV  IDTRK     REGTRK CID STATION       UTCTIME            STATUS     SOURCE </a> </b> <br />") 
for row in curs.fetchall():                     # search 
        # flarmid is the first field
        id1      = row[0]			# tracker ID
        if action == 'lastfix':
           cmd5="SELECT MAX(otime), id FROM OGNTRKSTATUS WHERE id = '"+id1+"' ;"
           try:					# find the last fix
              curs.execute(cmd5)		# get the info from OGNTRKSTATUS table
           except MySQLdb.Error as e:
              print ("SQL error: ",e)
           row=curs.fetchone()
           mtime=row[0]
           maxotime = mtime.strftime("%y-%m-%d %H:%M:%S")			# in string format yymmdd
           cmd6="SELECT * FROM OGNTRKSTATUS WHERE id = '"+id1+"' and otime = '"+maxotime+"' ;"
           curs.execute(cmd6)			# get the info from OGNTRKSTATUS table
           row=curs.fetchone()
        if row == None:
              continue
        station  = row[1]			# station receiving it
        otime    = row[2]			# timestamp
        status   = row[3]			# status
        source   = row[4]			# source OGN or STAT
        reg=getognreg(id1[3:])			# get the registration ID
        cid=getogncn(id1[3:])			# get the competition number
        sp=status[8:].find(' ')
        if sp == 20:				# if a encrypted status, nothing to do
           continue
        if id1 not in trks:			# if not seeing yet
           trks[id1] = 1			# add it now
        else:
           trks[id1] += 1			# increase the counter
        if status[6:8] == 'h ':			# check the version number
           qlf=id1+status[8:11]
        else:
           qlf=id1+status[0:3]
           if status[0] == 'h' and status[3:5] == ' v':
              status = "        "+status
        if qlf in trkt:				# do we have the timestamp
           continue
        else:
           trkt[qlf]=otime			# save the timestamp
        if action == 'list' and status[8] != 'h':
           continue 
        print ("<a> TRKDEV: %-9s %-7s %-3s %-9s %-20s %-30s %4s "% (id1, reg, cid, station, str(otime), status, source), "</a>")

print (html3)					# print the end of HTML table
conn.close()

exit(0)
