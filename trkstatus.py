import socket
import string
import time
import os.path
import psutil
import signal
import atexit
import MySQLdb                          # the SQL data base routines^M
import json
import argparse
from datetime import datetime, timedelta

#########################################################################


def signal_term_handler(signal, frame):
    print('got SIGTERM ... shutdown orderly')
    shutdown(sock) 			# shutdown orderly
    sys.exit(0)


# ......................................................................#
signal.signal(signal.SIGTERM, signal_term_handler)
# ......................................................................#


def prttime(unixtime):
    # get the time from the timestamp
    tme = datetime.utcfromtimestamp(unixtime)
    return(tme.strftime("%H%M%S"))			# the time


#
########################################################################
def shutdown(sock, prt=False):          # shutdown routine, close files and report on activity
                                        # shutdown before exit
	if os.path.exists("/tmp/TRKS.pid"):	# check if another process running
		os.remove("/tmp/TRKS.pid")	# remove it
	return
########################################################################
def storedb(curs, data, prt=False):
	if data[0:2] != 'M:':
		return
	otime = datetime.utcnow()
	sc1=data[2:].find(':')
	sc2=data[sc1+3:].find(':')
	station=data[2:sc1+2]
	ident="OGN"+data[sc1+3:sc1+sc2+3]
	status=otime.strftime("%H%M%S")+'h '+data[sc1+sc2+4:].rstrip('\n\r ')
	if len(status) > 254:
		status=staus[0:254]
	if prt:
		print ("S-->", ident, station, otime, status)
	inscmd = "insert into OGNTRKSTATUS values ('%s', '%s', '%s', '%s', '%s')" % (ident, station, otime, status, 'STAT')
	try:
		curs.execute(inscmd)
	except MySQLdb.Error as e:
		try:
			print(">>>MySQL1 Error [%d]: %s" % ( e.args[0], e.args[1]))
		except IndexError:
			print(">>>MySQL2 Error: %s" % str(e))
			print(">>>MySQL3 error:",  numtrksta, inscmd)
			print(">>>MySQL4 data :",  s)
	return
#
########################################################################
#
programver = 'V1.0'
print("\n\nStart TRKSTATUS  "+programver)
print("===================")

print("Program Version:", time.ctime(os.path.getmtime(__file__)))
print("==========================================")
date = datetime.utcnow()                # get the date
dte = date.strftime("%y%m%d")           # today's date
print("\nDate: ", date, "UTC on SERVER:", socket.gethostname(), "Process ID:", os.getpid())
date = datetime.now()			# local time
parser = argparse.ArgumentParser(description="OGN Push to the OGN APRS the delayed tracks")
parser.add_argument('-p',  '--print',     required=False,
                    dest='prt',   action='store', default=False)
args = parser.parse_args()
prt   = args.prt			# print on|off

# --------------------------------------#
#
# get the configuration data
#
# --------------------------------------#
import config                           # get the configuration data
if os.path.exists("/tmp/TRKS.pid"):	# check if another process running
    raise RuntimeError("TRKSTATUS already running !!!")
    exit(-1)
#
import locale
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
# --------------------------------------#
DBpath      = config.DBpath
DBhost      = config.DBhost
DBuser      = config.DBuser
DBpasswd    = config.DBpasswd
DBname      = config.DBname
# we force everything FALSE as we try to push to the APRS
OGNT        = False
# --------------------------------------#
cond = MySQLdb.connect(host=DBhost, user=DBuser, passwd=DBpasswd, db=DBname)
curs = cond.cursor()               	# set the cursor

print("Time now is: ", date, " Local time")
print("MySQL: Database:", DBname, " at Host:", DBhost)
# --------------------------------------#

count = 0
HOST=""
PORT = 50000              # Arbitrary non-privileged port
hostname = socket.gethostname()

try:
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(1)
    socket=s
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)
        while True:
            data = conn.recv(1024)
            count += 1
            dd=data.decode('utf-8')
            if prt:
               print("D:", dd)
            msg="OK "+str(count)+" "+hostname+' '+programver
            if not data: break
            conn.sendall(msg.encode('utf-8'))
            storedb(curs, dd, prt)
            cond.commit()
        print ("Counter:", count)
#########################################################################################
except KeyboardInterrupt:
    print("Keyboard input received, end of program, shutdown")
    pass

shutdown(socket)					# shotdown tasks
print ("Exit now ...          ", count)
exit(0)

