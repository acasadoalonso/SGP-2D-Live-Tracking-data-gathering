#!/usr/bin/python3
#
# Python code to push into the OGN APRS the delayed unencrypted PARS messages
#

import locale
import config                           # get the configuration data
import socket
import sys
import os
import time
import os.path
import psutil
import signal
import atexit
import MySQLdb                          # the SQL data base routines^M
import json
import ogndecode
import argparse
from time import sleep                  # use the sleep function
from datetime import datetime, timedelta
from ogn.parser import parse
from parserfuncs import deg2dmslat, deg2dmslon, dao, alive
from ognddbfuncs import getognreg, getogncn
from ogntfuncs import ogntbuildtable
from geopy.distance import geodesic     # use the Vincenty algorithm
from Keysfuncs import getprivatekey, getkeyfromencryptedfile, getkeys
from collections import deque

#########################################################################
#
def is_still_connected(sock):		# check if the sock is still valid
        try:
           sock.sendall(b"# ping")
           return True
        except:
           return False

def prtrep(trk, hdr):
    print(hdr)
    for t in trk:
        reg=getognreg(t[3:])
        cn =getognreg(t[3:])
        print("Trk: %9s %4d %-9s %4s " %(t, trk[t], reg, cn))
    return


def shutdown(sock, conn, prt=False):    # shutdown routine, close files and report on activity
    # shutdown before exit
    DQUEUE = False
    global numaprsmsg
    if is_still_connected(sock):
        try:
           sock.shutdown(0)             # shutdown the connection
           sock.close()                 # close the connection file
        except:
           print ("Ignore SOCK errors at this time...")
    try:
        conn.commit()                   # commit the DB updates
        conn.close()                    # close the database
    except Exception as e:
        print("Commit error...", e, datetime.now(), "Ignored at this time\n", file=sys.stderr)
    local_time = datetime.now()         # report date and time now
    now = datetime.utcnow()    		# get the date
    print("\n\n=================================================\nQueue: ", len(queue), now, "\n\n")
    i=1
    for e in queue:			# dump the entries on the queue
        etime=e['TIME']
        print(i, now-etime, "==>", etime, e['ID'], e['station'], e['hora'], e['rest'])
        if (prt):
            print(json.dumps(e['DECODE'], skipkeys=True, indent=4))
        aprsmsg=genaprsmsg(e)  		# gen the APRS message
        aprsmsg += " %ddly WARNING TIME \n" %delta.seconds  # include information about the delay
        print("APRSMSG: ", e["NumDec"], aprsmsg)  # print for debugging
        if DQUEUE and is_still_connected(sock):
           sock_file.write(aprsmsg)  	# send it to the APRS server
        i += 1				# one more to delete from table
        numaprsmsg += 1			# counter of published APRS msgs
    print("Shutdown now, Time now:", local_time, " Local time. \n")
    mem = process.memory_info().rss/(1024*1024)  	# in M bytes
    print("Memory available:      ", mem)
    prtrep(trackers, "Encrypting trackers msgs:")  # report the encrypted messages
    prtrep(utrackers, "Unencrypting trackers msgs:")  # report the non encrypte message, like trackers status or from non encrypting trackers
    prtrep(trkerrors, "Trackers with errors:")		# report the trackers with errors
    print("\n\nLast loc:              ", lastloc)
    if os.path.exists(config.DBpath+"DLYM2OGN.alive"):
        # delete the mark of being alive
        os.remove(config.DBpath+"DLYM2OGN.alive")
    if numdecodes > 0:
        print("\nNumber of records read: %d Trk status: %d Decodes: %d APRS msgs gen: %d Num Err Decodes %d Perc Err: %f%% \n" % (inputrec, numtrksta, numdecodes, numaprsmsg, numerrdeco, numerrdeco*100/numdecodes))
    return                              # job done

#########################################################################

#########################################################################
#########################################################################


def signal_term_handler(signal, frame):
    print('got SIGTERM ... shutdown orderly')
    shutdown(sock,conn) 			# shutdown orderly
    logfile.close()
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
    decode =entry["DECODE"]
    ID =entry["ID"]
    station =entry["station"]
    hora =entry["hora"]
    resto =entry["rest"]
    latitude =decode["Lat"]
    longitude =decode["Lon"]
    altitude =decode["Alt"]
    course =decode["Heading"]
    speed =decode["Speed"]
    roclimb =decode["RoC"]*3.28084
    RoT =decode["RoT"]
    DOP =decode["DOP"]

    resto=resto.lstrip(' ')                     # swap 2nd and 3rd words in rest of message
    sp1=resto.find(' ')				# find the end of first word
    if sp1 != -1:				# if not dound
        sp2=resto[sp1+1:].find(' ')+1+sp1
        db =resto[0:sp1]				# xx.xdB
        khz=resto[sp1+1:sp2]			# xx.xkHz
        e =resto[sp2+1:]			# xe
        rt=' '+db+' '+e+' '+khz			# the sequence now
    else:
        rt=' '+resto+' 0e '			# just a a white separator

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
    daotxt="!W"+dao(latitude)+dao(longitude)+"!"  # the extended precision
    #print ("DAO",daotxt, latitude, longitude)

    DOP=10+DOP
    HorPrec=int((DOP*2+5)/10)
    if(HorPrec>63):
        HorPrec=63
    VerPrec=int((DOP*3+5)/10)
    if(VerPrec>63):
        VerPrec=63
    gpstxt="gps"+str(HorPrec)+"x"+str(VerPrec)

    aprsmsg = ID+">OGNTRK,OGNDELAY*,"+station+":/" + hora+lat+"/"+lon+"'"+ccc+"/"+sss+"/"
    aprsmsg = ID+">OGNTRK,"+station+",OGNDELAY*:/" + hora+lat+"/"+lon+"'"+ccc+"/"+sss+"/"
    if altitude > 0:
        altitude=int(altitude*3.28084)		# convert to feet
        aprsmsg += "A=%06d" % altitude
    aprsmsg += " "+daotxt+" id06"+ID[3:]+" %+04dfpm " % (int(roclimb))+"%+04.1frot" % (float(RoT)) +rt+" "+gpstxt

    return(aprsmsg)
########################################################################


def genreport(curs, DK):		# report of OGNTRKSTATUS table 
    print("Report of records on the TRK status table on the DB\n")
    reccount = 0
    recstat = 0
    recvalid = 0
    cmd="select * from OGNTRKSTATUS"
    try:
        curs.execute(cmd)
    except MySQLdb.Error as e:
        try:
            print(">>>MySQL1 Error [%d]: %s" % (e.args[0], e.args[1]), file=sys.stderr)
        except IndexError:
            print(">>>MySQL2 Error: %s" % str(e), file=sys.stderr)
            print(">>>MySQL3 error:", cmd, file=sys.stderr)
            print(">>>MySQL4 data :", s, file=sys.stderr)
    for row in curs.fetchall():         # search for the first 20 the rows
        reccount += 1
        id1 = row[0]
        station = row[1]
        otime = row[2]
        status = row[3].lstrip(' ')
        reg=getognreg(id1[3:])
        cid=getogncn(id1[3:])
        sp=status.find(' ')		# look for the first space
        etxt=status[sp+1:]
        sp=etxt.find(' ')		# look for the second space
        txt=etxt[0:sp]			# that is the text to decode
        if len(txt) == 20:		# only encrypted msgs
            jstring=ogndecode.ogn_decode_func(txt, DK[0], DK[1], DK[2], DK[3])
            if len(jstring) == 0:
                continue
            jstring=jstring[0:jstring.find('}')+1]
            decode=json.loads(jstring)  # get the dict from the JSON string

            if "msg" in decode:
                print(">>>>>>> message on decode string:", decode["msg"])
                continue
            latitude =decode["Lat"]
            longitude =decode["Lon"]
            Acft =decode["Acft"]
            if latitude > 90.0 or latitude < -90.0 or longitude > 180.0 or longitude < -180.0 or Acft != 1:
                continue
            if prt:
                print("RRR:>>>:", id1, station, otime, reg, cid, status[0:7], decode, "<<<:RRR")
            recvalid += 1
        else:
            recstat += 1
            continue
    print("Records encrypted valid:", recvalid, "Recs non encrypted", recstat, "Recs total on table",reccount, "\n")
    return


#
########################################################################
#

programver = 'V1.5'
print("\n\nStart DLYM2OGN "+programver)
print("===================")

print("Program Version:", time.ctime(os.path.getmtime(__file__)))
print("==========================================")
date = datetime.utcnow()                # get the date
dte = date.strftime("%y%m%d")           # today's date
print("\nDate: ", date, "UTC on SERVER:", socket.gethostname(), "Process ID:", os.getpid())
location_latitude=config.location_latitude
location_longitude=config.location_longitude
print("Location coordinates:", location_latitude, location_longitude, "at: ", config.location_name)
date = datetime.now()			# local time

# --------------------------------------#
#
# get the configuration data
#
# --------------------------------------#
if os.path.exists(config.DLYPIDfile):  # check if another process running
    raise RuntimeError("DLY2APRS already running !!!")
    exit(-1)
#
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

APP = "DLYM2OGN"		# the application name
SLEEP = 10			# sleep 10 seconds in between calls to the APRS
DELAY = config.DELAY		# 20 minutes delay
nerrors = 0			# number of errors in *funcs found
day = 0				# day of running
loopcount = 0			# counter of loops
inputrec = 0			# number of input records
numerr = 0			# number of errors
numtrksta = 0 			# number of tracker status records
numdecodes = 0			# number of records decoded
numaprsmsg = 0			# number of APRS messages generated
numerrdeco = 0			# number of APRS messages generated
maxnerrs = 100
queue = []			# queue of pending messages
trackers = {}			# list of seems trackers encoding
utrackers = {}			# list of seems trackers non encoding
ognttable = {}			# init the instance of the table
lastloc = {}			# last position for this tracker
trkerrors = {}			# errors

# --------------------------------------#
DBpath = config.DBpath
DBhost = config.DBhost
DBuser = config.DBuser
DBpasswd = config.DBpasswd
DBname = config.DBname
# we force everything FALSE as we try to push to the APRS
SPIDER = False
SPOT = False
INREACH = False
CAPTURS = False
SKYLINE = False
LT24 = False
OGNT = False
# --------------------------------------#


parser = argparse.ArgumentParser(description="OGN Push to the OGN APRS the delayed tracks\n")
parser.add_argument('-p', '--print', required=False,
                    dest='prt', action='store', default=False)				# print the debugging info
parser.add_argument('-dly', '--delay', required=False,
                    dest='dly', action='store', default=-1)				# delay of the encrypted messages to diisplay
parser.add_argument('-l', '--log', required=False,
                    dest='log', action='store', default='DLYM2OGN'+dte+'.log')		# name of the LOG file
parser.add_argument('-c', '--comp', '--competition', required=False,
                    dest='comp', action='store', default=False)
parser.add_argument('-kf', '--keyfile', required=False,
                    dest='kfile', action='store', default='keyfile.encrypt')		# name of the file with the encrypted keys
parser.add_argument('-pk', '--privatekey', '--privkey', required=False,
                    dest='pkey', action='store', default='/utils/keypriv.PEM')		# name of the private key file on PEM format
parser.add_argument('-kp', '--keypath', required=False,
                    dest='kpath', action='store', default='/home/angel/src/APRSsrc/')	# path for the working files
parser.add_argument('-r', '--report', required=False,
                    dest='report', action='store', default=False)			# just print a report of the OGN tracker status on the DB
args = parser.parse_args()
# --------------------------------------------------------------------------------------------------------------------------------------------------- #
prt = args.prt				# print on|off
dly = args.dly				# delay in seconds, default config.DELAY
log = args.log				# name of the logfile
comp = args.comp			# if in competition or test
kfile = args.kfile			# name of encrypted file
pkey = args.pkey			# name of file with the private key
kpath = args.kpath			# path where ther are the keyfiles
report = args.report			# report ?
if (dly == -1):
    DELAY=config.DELAY
else:
    DELAY=int(dly)

# -----------------------------------------------------------------#
conn = MySQLdb.connect(host=DBhost, user=DBuser, passwd=DBpasswd, db=DBname)
curs = conn.cursor()               	# set the cursor

print("Time now is: ", date, " Local time, using DELAY: ", DELAY)
print("MySQL: Database:", DBname, " at Host:", DBhost)
# --------------------------------------#
# build the table from the TRKDEVICES DB table
ogntbuildtable(conn, ognttable, prt)
# --------------------------------------#
#keypath="/home/angel/src/APRSsrc/"
keypath=kpath
keyfile=keypath+kfile			# name where it is the keys encrypted
keypriv=keypath+pkey			# name of the private key file (PEM)

DK=[]					# decrypting keys
if os.path.exists(keyfile):		# check for the encrypted keyfile
    privkey=getprivatekey(keypriv)  	# get the private key
    decKey=getkeyfromencryptedfile(keyfile, privkey).decode('utf-8')
    if prt:
        print("DKfile", decKey)
    DK=getkeys(DK, decKey)		# get the keys
    if prt:
        print(DK)
    print(DK)
else:
    print("ERROR: No key file found !!!", keyfile, file=sys.stderr)
    exit(-1)
# --------------------------------------#
if report:
    genreport(curs, DK)
    exit(0)
# --------------------------------------#

#----------------------dlym2ogn.py start-----------------------#


with open(config.DLYPIDfile, "w") as f:  # set the lock file  as the pid
    f.write(str(os.getpid()))
    f.close()
atexit.register(lambda: os.remove(config.DLYPIDfile))

logfile=open(log, "a")   		# set the log file
logfile.write(">>: ProcessID"+str(os.getpid())+' '+str(date)+'<<:\n')
logfile.flush()
# create socket & connect to server
server=config.APRS_SERVER_PUSH
#server="aprs.glidernet.org"
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((server, config.APRS_SERVER_PORT))
print("Socket sock connected to: ", server, ":", config.APRS_SERVER_PORT)

# logon to OGN APRS network
config.APRS_USER='DLY2APRS'
config.APRS_PASSCODE='32159'

login = 'user %s pass %s vers DLY2APRS %s filter %s' % (config.APRS_USER, config.APRS_PASSCODE, programver, " b/OGN* d/OBS2OGN p/OBS2OGN \n")
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
# --------------------------------------#
day = now.day				# day of the month
process = psutil.Process(os.getpid())  # process info


try:

    #----------------------dlym2ogn.py main loop-----------------------#
    while True:
        func='NONE'
        current_time = time.time()
        local_time = datetime.now()
        elapsed_time = current_time - keepalive_time    # time since last keep_alive
        if (current_time - keepalive_time) > 180:      	# keepalives every 3 mins
            # and mark that we are still alive
            alive(config.DBpath+APP)			# mark that we are alive
            mem = process.memory_info().rss/(1024*1024)  # in  M bytes
            rec=">>: %s Mem:%d Queue:%d LoopCount:%d :<<" % (str(local_time), mem, len(queue), loopcount)  # mark the time
            rec += " ;;; Nrec: %d NTrksta: %d NDecodes: %d N.APRSmsgs: %d NErrDecodes %d ;;;\n" % (inputrec, numtrksta, numdecodes, numaprsmsg, numerrdeco)
            logfile.write(rec)				# mark the time
            logfile.flush()				# write the records
            run_time = time.time() - start_time
            keepalive_time = current_time
            keepalive_count = keepalive_count + 1       # just a control


            try:					# lets send a message to the APRS for keep alive
                rtn = sock_file.write("#Python ogn dly2ogn App\n\n")
                time.sleep(200/1000)
                sock_file.flush()		        # Make sure keepalive gets sent. If not flushed then buffered
                time.sleep(200/1000)

            except Exception as e:
                print(('Something\'s wrong with socket write. Exception type is %s' % (repr(e))), file=sys.stderr)
                now = datetime.utcnow()		        # get the UTC time
                print("UTC time is now: ", now, keepalive_count, run_time, file=sys.stderr)
                exit(1)

        now = datetime.utcnow()				# get the UTC time
        # number of second until beginning of the epoch
        tt = int((now-datetime(1970, 1, 1)).total_seconds())
        if now.day != day:				# check if day has changed
            print("End of Day...")
            shutdown(sock,conn)				# recycle
            logfile.close()
            exit(0)

        loopcount += 1			        	# we report a counter of calls to the interfaces

        sys.stdout.flush()				# flush the print messages
        sys.stderr.flush()				# flush the print messages
        if prt:
            print("In main loop. Count= ", inputrec)
        inputrec += 1
        try:
            packet_str = sock_file.readline() 		# Read packet string from socket

            if prt:
                print(packet_str)
        except socket.error:
            print("Socket error on readline :", inputrec, file=sys.stderr)
            continue
        if prt:
            print(packet_str)
        # A zero length line should not be return if keepalives are being sent
        # A zero length line will only be returned after ~30m if keepalives are not sent
        if len(packet_str) == 0:
            numerr += 1				# increase error counter
            if numerr > maxnerrs:		# if too mane errors
                print("Read returns zero length string. Failure.  Orderly closeout", numerr, file=sys.stderr)
                date = datetime.now()
                print("UTC now is: ", date, file=sys.stderr)
                break
            else:
                sleep(5) 			# wait 5 seconds
                continue

        ix = packet_str.find('>')
        cc = packet_str[0:ix]
        packet_str = cc.upper()+packet_str[ix:]  # convert the ID to uppercase
        msg = {}

        # if not a heartbeat from the server
        if len(packet_str) > 0 and packet_str[0] != "#" and packet_str[ix+1:ix+7] != "OGNFNT":
            #########################################################################################
            # deal with a normal APRS message
            s=packet_str
            ph=s.find(":/______")
            if ph > 0:
               continue				# no time ... ignore it
            ph=s.find(":>")
            hora=s[ph+2:ph+9]			# get the hora as: hhmmssh
            try:
                beacon=parse(s)  		# parse the APRS message
            except Exception as e:
                print("DLY: parse error >>>>", e, s, "<<<<\n", file=sys.stderr)
                continue			# nothing else to do !!

                # check if it is a OGN tracker status messagea
            #if beacon["dstcall"] == "OGNTTN":
                #print ("\n\nBBB", beacon, "\n\n")

            if beacon["aprs_type"] == "status" and (beacon["beacon_type"] == "tracker" or beacon["beacon_type"] == "unknown") and (beacon["dstcall"] == "OGNTRK" or beacon["dstcall"] == "OGTTN2" or beacon['dstcall'] == "OGOBS"):
                comment=s[ph+10:]	        # get the comment where it is the data
                #print ("CCC:", comment.rstrip(" \n\r"), ":", len(comment), s)
            else:
                continue			# otherwise ignore it
            sp=comment.find(' ')		# look for the first space
            txt=comment[0:sp]			# that is the text to decode
            rest=comment[sp:].rstrip("\n\r")    # save the rest: freq deviation, error bits, ...
            ident = beacon['name']		# tracker ID
            station = beacon['receiver_name'] 	# station
            #print ("Txt:>>>", len(txt), txt, ":::>", sp, rest, ":::>", s, "\n")
            if (len(txt) != 20):		# those are encoded tracker messages
                numtrksta += 1			# number of records saved
                ID = ident
                if ID not in utrackers:   	# did we see this tracker
                    utrackers[ID] = 1    	# init the counter
                else:
                    utrackers[ID] += 1   	# increase the counter

                continue			# nothing else to do, it is not an encrypted message

            # deal with the decoding case
            if ident not in ognttable:		# if is not on the table that we are working on ???
                if prt:
                    print(">>:TRK:", ident, station, "<<<")
                if comp:
                    continue			# nothing to do in case of competition
            else:
                flarmid=ognttable[ident]	# just in case
            ne=rest.find('kHz ')		# look for number of errors
            if ne > 0:
               nee=rest[ne+4:].find('e')
               nerr=int(rest[ne+4:ne+4+nee])
               if nerr > 10:			# if bigger than 10 is not worth the message
                  continue
            jstring=" " 			# init the json string for receiving the decoded message
            if prt:
                print("Decoding >>>>", jstring, ">>", txt, "<<", len(txt), ident, station, "<<<<")

            try:				# decode the encrypted message
                if prt:
                    print(">>>:", DK, txt)
						# ---------------------------------------------------------- #
                # invoke the decoding routine, passing the message and the decoding keys
                jstring=ogndecode.ogn_decode_func(txt, DK[0], DK[1], DK[2], DK[3])
						# ---------------------------------------------------------- #

            except Exception as e:		# catch the exception
                errordet=""			# error messages
                ee="%s" %e			# convert to string
                p1=ee.find("(char ")		# find the (char xxx) string
                if p1 != -1:			# if found ???
                    errordet=jstring[p1-3:p1+3]  # extract the position
                print("DECODE Error:", e, ">>:", errordet, ":<<", ident, station, hora, jstring, comment, "\n\n",  file=sys.stderr)
                numerrdeco += 1			# increse the counter
                continue			# nothing else to do
            if len(jstring) > 0:		# if valid ???
                numdecodes += 1			# increase the counter
                jstring=jstring[0:jstring.find('}')+1]
                decode=json.loads(jstring)  # get the dict from the JSON string
                #print ("DDD", decode)
                if "msg" in decode:
                    print(">>>>>>> message on decode string:", decode)
                    continue
                ID=beacon["name"]		# tracker ID
                station=beacon["receiver_name"]  # station

                latitude =decode["Lat"]
                longitude =decode["Lon"]
                altitude =decode["Alt"]
                Acft =decode["Acft"]

                if latitude > 90.0 or latitude < -90.0 or latitude == 0.0 or longitude > 180.0 or longitude < -180.0 or (Acft != 1 and Acft != 14) or altitude == 0 or altitude > 15000 or altitude < 0:
                    if ID not in trkerrors:
                       reg=getognreg(ID[3:])
                       cn =getognreg(ID[3:])
                       if altitude == 0 or altitude > 15000 or altitude < 0:
                           print("Altitude error:", ID, reg, cn, station, hora, altitude,   "::::", packet_str,  file=sys.stderr)
                       else:
                           print("Coord error:",    ID, reg, cn, station, hora, ">>>:", txt, ogndecode.ogn_decode_func(txt, DK[0], DK[1], DK[2], DK[3]), "::::", packet_str, "::::", file=sys.stderr)
                    if ID not in trkerrors:   	# did we see this tracker
                        trkerrors[ID] = 1    	# init the counter
                    else:
                        trkerrors[ID] += 1   	# increase the counter
                    numerrdeco += 1		# increase the counter of errors
                    continue
                if prt:
                   print ("Return:>>>>", len(jstring), jstring, "DECODE:", decode, "<<<<")
                if ID not in lastloc:
                    lastloc[ID]=(latitude, longitude)
                else:				# check now the distance from previous position
                    prevloc=lastloc[ID]		# remember what was the last location for reporting.
                    distance=geodesic((latitude, longitude), lastloc[ID]).km
                    if distance > 25.0:		# very unlikely that the tracker moved 25 kms from previous position
                        print("Dist error:", distance, ID, station, hora, latitude, longitude, prevloc, ">>>:", txt, ogndecode.ogn_decode_func(txt, DK[0], DK[1], DK[2], DK[3]), file=sys.stderr)
                        if ID not in trkerrors: # did we see this tracker
                            trkerrors[ID] = 1   # init the counter
                        else:
                            trkerrors[ID] += 1  # increase the counter
                        numerrdeco += 1		# increase the counter of errors
                        continue
                    lastloc[ID]=(latitude, longitude)  # register the last localtion
                
                distance=geodesic((latitude, longitude), (location_latitude,location_longitude)).km
                if distance > 250.0:		# very unlikely that the tracker moved 25 kms from previous position
                        print("Dist error from home: ", distance, ID, station, hora, latitude, longitude,  ">>>:", txt, ogndecode.ogn_decode_func(txt, DK[0], DK[1], DK[2], DK[3]), file=sys.stderr)
                        if ID not in trkerrors: # did we see this tracker
                            trkerrors[ID] = 1   # init the counter
                        else:
                            trkerrors[ID] += 1  # increase the counter
                        numerrdeco += 1		# increase the counter of errors
                        continue

                # everything seems to be OK, so lets place the entry on the queue
                now = datetime.utcnow()  	# get the UTC time
						# ------------------------------------------------------------------------------------- #
                # place it on the queue
                qentry= {"NumDec": numdecodes, "TIME": now, "ID": ID, "station": station, "hora": hora, "rest": rest, "DECODE": decode}
                queue.append(qentry)  		# add the entry to the queue
						# ------------------------------------------------------------------------------------- #
                if prt:
                    print(">>>N#", numdecodes, len(queue), qentry, "<<<<")
                if ID not in trackers:   	# did we see this tracker
                    trackers[ID] = 1    	# init the counter
                else:
                    trackers[ID] += 1    	# increase the counter

            else:				# if NOT valid ???
                numerrdeco += 1			# increse the counter
                continue
#       end of if of valid decoding messages 

#       =============================================================================================================
                # check now if we need to publish delayed entries
        nqueue=[]				# the new queue if we need to delete entries
        idx=0					# index to rebuild the table
        ddd=0
        for e in queue: 			# scan the queue for entries to push to the APRS
            etime=e["TIME"]			# get the time
            delta=(now - etime)			# get the time difference
            #print("Delta>>>", delta)
            dts=int(delta.total_seconds())  	# time difference in seconds
            if (dts > DELAY): 			# if higher that DELAY ??
                aprsmsg=genaprsmsg(e)  		# gen the APRS message
                aprsmsg += " %ddly \n" %delta.seconds  # include information about the delay
                if prt:
                    print("APRSMSG: ", e["NumDec"], aprsmsg)  # print for debugging
                rtn = sock_file.write(aprsmsg)  # send it to the APRS server
                time.sleep(500/1000)
                sock_file.flush()	        # Make sure gets sent. If not flushed then buffereda
                logfile.write(aprsmsg)  	# log into filea
                print("APRSMSG: ", e["NumDec"], aprsmsg)  # print for debugging

                idx += 1			# one more to delete from table
                numaprsmsg += 1			# counter of published APRS msgs
            else:
                nqueue.append(e)		# keep that entry on the table
                if ddd == 0:			# if first on the queue
                    ddd = dts			# remember that
        # end of for loop of dequeuing messages
#       =============================================================================================================

        if (idx > 0):				# if we found at least one entry
            queue=nqueue			# this is the new queue
            del nqueue 				# delete the old queue
        mem = process.memory_info().rss  	# in bytes

        if prt or mem < 2*1024*1024 or (loopcount - int(loopcount/1000)*1000) == 0:        	# if less that 2 Mb
            now = datetime.utcnow()		# get the UTC time
            print(">>>:##MEM##>>> Ndec:", numdecodes, "Qlen:", len(queue), "Delta:", ddd, "<<<", process.memory_info().rss, ">>>", now)  # in bytes


# end of while

#       sleep(SLEEP)				# sleep n seconds

#----------------------dlym2ogn.py end of main loop-----------------------#

#########################################################################################
except KeyboardInterrupt:
    print("Keyboard input received, end of program, shutdown")
    pass

shutdown(sock,conn)					# shotdown tasks
logfile.close()
print("Exit now ...          ", nerrors)
exit(0)

