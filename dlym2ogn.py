#!/usr/bin/python3
#
# Python code to push into the OGN APRS the delayed unencrypted PARS messages
#

import socket
import string
import sys
import os
import time
import os.path
import signal
import atexit
import MySQLdb                          # the SQL data base routines^M
import json
import ogndecode
from ctypes import *
from time import sleep                  # use the sleep function
from datetime import datetime, timedelta
from ogn.parser import parse
from parserfuncs import deg2dmslat, deg2dmslon, dao, alive

#########################################################################


def shutdown(sock):		        # shutdown routine, close files and report on activity
                                        # shutdown before exit
    try:
        sock.shutdown(0)                # shutdown the connection
        sock.close()                    # close the connection file
    except Exception as e:
        print("Socket error...")
    conn.commit()                       # commit the DB updates
    conn.close()                        # close the database
    local_time = datetime.now()         # report date and time now
    now = datetime.utcnow()    		# get the date
    print("\n\n=================================================\nQueue: ", len(queue), now, "\n\n")
    i=1
    for e in queue:
          etime=e['TIME']
          print (i, now-etime, "==>", etime, e['ID'], e['station'], e['hora'], e['rest'])
          print(json.dumps(e['DECODE'], skipkeys=True, indent=4))
          i +=1
    print("Shutdown now, Time now:", local_time, " Local time.")
    print("Number of records read: %d Trk status: %d Decodes: %d APRS msgs gen: %d \n" % (inputrec, numtrksta, numdecodes, numaprsmsg))
    if os.path.exists(config.DBpath+"DLYM2OGN.alive"):
                                        # delete the mark of being alive
        os.remove(config.DBpath+"DLYM2OGN.alive")
    return                              # job done

#########################################################################

#########################################################################
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
def genaprsmsg(entry):					# format the reconstructed APRS message
            decode             =entry["DECODE"]
            ID                 =entry["ID"]
            station            =entry["station"]
            hora               =entry["hora"]
            rest               =entry["rest"]
            latitude           =decode["Lat"]
            longitude          =decode["Lon"]
            altitude           =decode["Alt"]
            course             =decode["Heading"]
            speed              =decode["Speed"]
            roclimb            =decode["RoC"]*3.28084
            RoT                =decode["RoT"]
            DOP                =decode["DOP"]
                                                        # build the APRS message
            lat = deg2dmslat(abs(latitude))
            if latitude > 0:
                        lat += 'N'
            else:
                        lat += 'S'
            lon = deg2dmslon(abs(longitude))
            if longitude > 0:
                        lon += 'E'
            else:
                        lon += 'W'
            
            ccc = "%03d" % int(course)
            sss = "%03d" % int(speed)
            daotxt="!W"+dao(latitude)+dao(longitude)+"!"	# the extended precision

            DOP=10+DOP
            HorPrec=(DOP*2+5)/10 
            if(HorPrec>63):
                HorPrec=63
            VerPrec=(DOP*3+5)/10 
            if(VerPrec>63): 
                VerPrec=63
            gpstxt="gps"+str(HorPrec)+"x"+str(VerPrec)

            aprsmsg = ID+">OGNDELAY,RELAY*,qAS,"+station+":/" + hora+lat+"/"+lon+"'"+ccc+"/"+sss+"/"
            if altitude > 0:
                        aprsmsg += "A=%06d" % int(altitude)
            aprsmsg += daotxt+" id06"+ID[3:]+" %+04dfpm " % (int(roclimb))+" %+04.1frot " % (float(RoT)) +rest+" -7.4kHz "+gpstxt

            return(aprsmsg)
#
########################################################################
#
programver = 'V1.0'
print("\n\nStart DLYM2OGN "+programver)
print("===================")

print("Program Version:", time.ctime(os.path.getmtime(__file__)))
print("==========================================")
date = datetime.utcnow()         		# get the date
dte = date.strftime("%y%m%d")             # today's date
print("\nDate: ", date, "UTC on SERVER:", socket.gethostname(), "Process ID:", os.getpid())
date = datetime.now()                   # local time
print("Time now is: ", date, " Local time")

# --------------------------------------#
#
# get the configuration data
#
# --------------------------------------#
import config                           # get the configuration data
if os.path.exists(config.DLYPIDfile):
    raise RuntimeError("DLY2APRS already running !!!")
    exit(-1)
#
import locale
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
APP         = "DLYM2OGN"		# the application name
SLEEP       = 10			# sleep 10 seconds in between calls to the APRS
DELAY       = config.DELAY		# 20 minutes delay
nerrors     = 0				# number of errors in *funcs found
day         = 0				# day of running
loopcount   = 0				# counter of loops
inputrec    = 0				# number of input records
numerr      = 0				# number of errors
numtrksta   = 0 			# number of tracker status records
numdecodes  = 0				# number of records decoded
numaprsmsg  = 0				# number of APRS messages generated
maxnerrs    = 100
queue       = []			# queue of pending messages
# --------------------------------------#
DBpath      = config.DBpath
DBhost      = config.DBhost
DBuser      = config.DBuser
DBpasswd    = config.DBpasswd
DBname      = config.DBname
# we force everything FALSE as we try to push to the APRS
SPIDER      = False
SPOT        = False
INREACH     = False
CAPTURS     = False
SKYLINE     = False
LT24        = False
OGNT        = False
# --------------------------------------#

# -----------------------------------------------------------------#
conn = MySQLdb.connect(host=DBhost, user=DBuser, passwd=DBpasswd, db=DBname)
curs = conn.cursor()               # set the cursor

print("MySQL: Database:", DBname, " at Host:", DBhost)

#----------------------dlym2ogn.py start-----------------------#

prtreq = sys.argv[1:]              # check if the prt arg is there
if prtreq and prtreq[0] == 'prt':
    prt = True
else:
    prt = False

with open(config.DLYPIDfile, "w") as f:  # set the lock file  as the pid
    f.write(str(os.getpid()))
    f.close()
atexit.register(lambda: os.remove(config.DLYPIDfile))

# create socket & connect to server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((config.APRS_SERVER_HOST, config.APRS_SERVER_PORT))
print("Socket sock connected to: ", config.APRS_SERVER_HOST, ":", config.APRS_SERVER_PORT)

# logon to OGN APRS network
config.APRS_USER='DLY2APRS'
config.APRS_PASSCODE='32159'

login = 'user %s pass %s vers DLY2APRS %s filter d/TCPIP* %s' % (config.APRS_USER, config.APRS_PASSCODE, programver, config.APRS_FILTER_DETAILS)
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


# Initialise libfap.py for parsing returned lines
start_time = time.time()
local_time = datetime.now()
keepalive_count = 1
keepalive_time = time.time()
alive(config.DBpath+APP, first='yes')
#
#-----------------------------------------------------------------#
# Initialise API for DLYM2OGN
#-----------------------------------------------------------------#
#
now = datetime.utcnow()			# get the UTC timea
min5 = timedelta(seconds=300)		# 5 minutes ago
now = now-min5				# now less 5 minutes
# number of seconds until beginning of the day 1-1-1970
td = now-datetime(1970, 1, 1)
ts = int(td.total_seconds())		# Unix time - seconds from the epoch
ttime = now.strftime("%Y-%m-%dT%H:%M:%SZ")  # format required by 
import DecKey
#decKey=b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
day = now.day				# day of the month

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
                sock_file.flush()		        # Make sure keepalive gets sent. If not flushed then buffered

            except Exception as e:
                print(( 'Something\'s wrong with socket write. Exception type is %s' % (repr(e))))
                now = datetime.utcnow()		        # get the UTC time
                print("UTC time is now: ", now, keepalive_count, run_time)

        now = datetime.utcnow()				# get the UTC time
                                                        # number of second until beginning of the epoch
        tt = int((now-datetime(1970, 1, 1)).total_seconds())
        if now.day != day:				# check if day has changed
            print("End of Day...")
            shutdown(sock)				# recycle
            exit(0)

        try:						# lets see if we have data from the interface functionns: 

            loopcount += 1			        # we report a counter of calls to the interfaces

        except Exception as e:
            print(( 'Something\'s wrong with interface function  Exception type is %s' % (repr(e))))
            print(loopcount, "ERROR ---> TTime:UTC Now:", datetime.utcnow().isoformat())
            nerrors += 1
            if nerrors > maxnerrs:
                shutdown(sock)		                # way to many errors
                sys.exit(-1)		                # and bye ...

        sys.stdout.flush()				# flush the print messages
        if prt:
            print("In main loop. Count= ", inputrec)
        inputrec += 1
        try:
            packet_str = sock_file.readline() 		# Read packet string from socket

            if len(packet_str) > 0 and packet_str[0] != "#" and config.LogData:
                datafile.write(packet_str)		# log the data if requested
            if prt:
                print(packet_str)
        except socket.error:
            print("Socket error on readline")
            continue
        if prt:
            print(packet_str)
        # A zero length line should not be return if keepalives are being sent
        # A zero length line will only be returned after ~30m if keepalives are not sent
        if len(packet_str) == 0:
            numerr += 1					# increase error counter
            if numerr > maxnerrs:
                print("Read returns zero length string. Failure.  Orderly closeout", err)
                date = datetime.now()
                print("UTC now is: ", date)
                break
            else:
                sleep(5) 				# wait 5 seconds
                continue

        ix = packet_str.find('>')
        cc = packet_str[0:ix]
        packet_str = cc.upper()+packet_str[ix:]		# convert the ID to uppercase
        msg = {}
        # if not a heartbeat from the server
        if len(packet_str) > 0 and packet_str[0] != "#":
#########################################################################################
            s=packet_str
            ph=s.find(":>")
            hora=s[ph+2:ph+9]
            try:
               beacon=parse(s)  
            except:
               #print("parseverror >>>>", s)
               continue
            if beacon["aprs_type"] == "status" and beacon["beacon_type"] == "tracker" and beacon["dstcall"] == "OGNTRK" and "comment" in beacon:
               comment=beacon['comment']
            else:
               continue
            #print("ORIGMSG: ", s)
            #print (beacon)
            sp=comment.find(' ')
            txt=comment[0:sp]
            rest=comment[sp:]
            #print ("Txt:>>>", len(txt), txt, ":::>", sp, rest, ":::>", s, "\n")
            jstring="                   "
            if (len(txt) != 20):		# those are stad tracker status messages 
                status = beacon['comment']	# get the status message
                                                # and the station receiving that status report
                station = beacon['receiver_name'] # station
                ident = beacon['name']		# tracker ID
                otime = beacon['reference_timestamp']	# get the time from the system
                if len(status) > 254:
                    status = status[0:254]
                #print ("Status report >>>>>>>>>>>:", ident, station, otime, status)
                inscmd = "insert into OGNTRKSTATUS values ('%s', '%s', '%s', '%s' )" % (ident, station, otime, status)
                try:
                    curs.execute(inscmd)
                except MySQLdb.Error as e:
                    try:
                        print(">>>MySQL1 Error [%d]: %s" % (
                            e.args[0], e.args[1]))
                    except IndexError:
                        print(">>>MySQL2 Error: %s" % str(e))
                    print(">>>MySQL3 error:",  numtrksta, inscmd)
                    print(">>>MySQL4 data :",  data)
                numtrksta += 1			# number of records saved

                continue			# nothing else to do

						# deal with the decoding
            jstring=" " 
            #print ("Decoding >>>>", jstring, txt, decKey)
            try:
                   jstring=ogndecode.ogn_decode_func(txt, decKey)
                   if len(jstring) > 0:
                      jstring=jstring[0:jstring.find('}')+1]
                      #print ("Return:>>>>", len(jstring), jstring)
                      decode=json.loads(jstring)
                      #print (decode)
                      ID=beacon["name"]
                      station=beacon["receiver_name"]

                      now = datetime.utcnow()	# get the UTC timea
                      qentry= { "TIME": now, "ID":ID, "station": station, "hora": hora, "rest": rest, "DECODE": decode}
                      queue.append(qentry)	# add the entry to the queue
                      numdecodes += 1		# increase the counter
                      print(qentry)
            except Exception as e:
                   print ("DECODE Error:", e, ID, station, hora, jstring, txt)
                   continue
            nqueue=[]				# the new queue if we need to delete entries
            i=0
            for e in queue:
                etime=e["TIME"]
                delta=(now - etime)
                #print("Delta>>>", delta)
                if (delta.total_seconds() > DELAY):
                    aprsmsg=genaprsmsg(e)
                    aprsmsg += " %ddly \n"%delta.seconds
                    print("APRSMSG: ", aprsmsg)
                    rtn = config.SOCK_FILE.write(aprsmsg)
                    i += 1
                    numaprsmsg += 1
                else:
                    nqueue.append(e)
            if (i > 0):
                queue=nqueue
            #print ("NEXT---->")


#########################################################################################
 
#        sleep(SLEEP)					# sleep n seconds


except KeyboardInterrupt:
    print("Keyboard input received, ignore")
    pass

shutdown(sock)
print("Exit now ...", nerrors)
exit(0)
