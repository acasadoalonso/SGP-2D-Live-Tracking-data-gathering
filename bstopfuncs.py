#!/bin/python3
#-------------------------------------------------------------------------------------------------------------------#
# this functions deals with the data received by the birdstop detectors    api.birdstop.io 
#-------------------------------------------------------------------------------------------------------------------#
# The data is received through a MQTT broker, and we subscribe to the topic that matches the publish topic of the birdstop detectors
# The data is received in JSON format, and we convert it to a dict, and we extract the information of the fix, and we store it in a buffer, and we push it to the OGN APRS, and we store it in the DDBB
# The data received is in the format:
# {
#   "id": "birdstop_BCN1_1042",
#   "type": "bird",
#   "site_id": "BCN1",
#   "timestamp": "2025-06-12T14:22:05Z			# the time when the bird was seen, in ISO 8601 format
#   "latitude": 41.3096,
#   "longitude": 2.0902,
#   "altitude_m": 45.2,
#   "speed_ms": 12.3		# the ground speed of the bird, in m/s
# }
# 
#
# python 3.11

import random
import json
import time
import psutil
import config
import adsbregfuncs
import platform
from   adsbregfuncs import getadsbreg, getsizeadsbcache
from   time import sleep

from   datetime import datetime
from   geopy.distance import geodesic       	# use the Vincenty algorithm^M
from   parserfuncs import deg2dmslat, deg2dmslon, dao
from   paho.mqtt import client as mqtt_client
from   dtfuncs import naive_utcnow, naive_utcfromtimestamp

import psutil

from   dtfuncs import naive_utcnow, naive_utcfromtimestamp

#-------------------------------------------------------------------------------------------------------------------#
#-------------------------------------------------------------------------------------------------------------------#
# example: curl -G "http://3.22.63.131/v1/detections"   -H "X-API-Key: bsdk_live_ogn_xk9mPqR2vTwL4nYsJ7hB"   --data-urlencode "type=bird"   --data-urlencode "from=2026-03-15T00:00:00"   --data-urlencode "min_confidence=0.8"   --data-urlencode "limit=25" | jq
#

example= {
  "id": "birdstop_BCN1_1042",
  "type": "bird",
  "site_id": "BCN1",
  "timestamp": "2025-06-12T14:22:05Z",
  "latitude": 41.3096,
  "longitude": 2.0902,
  "altitude_m": 45.2,
  "heading": 182.5,
  "speed_ms": 12.3
}

global savedtime
savedtime = time.time()
prt=False

# ----------------------------------------------------------------------------------------------------------------
if prt:
   print ("\n\nBSTOP functions ...\n\n")		# just to inform that we are on the BSTOP functionsa
   print(config.BSTOPMQTT, config.BSTOPTOPIC, config.BSTOPUSER, config.BSTOPPASSWD)	# print the configuration for debugging

# Generate a Client ID with the subscribe prefix.
client_id = f'BSTOP-{random.randint(0, 100)}' 	# name of the client BSTOP and a random number to avoid conflicts with other clients
broker    = config.BSTOPMQTT			# URL of the Mosquitto server
port      = 1883				# the default
topic     = config.BSTOPTOPIC			# the susbcrive TOPIC that matches the publish topic
username  = config.BSTOPUSER			# the user
password  = config.BSTOPPASSWD			# the passowrd 
mqtt      = config.BSTOPMQTT			# the global pointer to the MQTT client instance, to be able to disconnect it when we finish



#-------------------------------------------------------------------------------------------------------------------#
def on_connect(client, userdata, flags, rc):	# function clled on connect

     if rc == 0:
         print("Connected to MQTT Broker!")	# just inform of it
     else:
         print("Failed to connect, return code %d\n", rc)

def connect_mqtt() -> mqtt_client:		# connect to the Mosquitto server

    py=platform.python_version()
    if py[0:4] >= '3.11':
       client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1, client_id)
    else:
       client = mqtt_client.Client(client_id)

    client.username_pw_set(username, password)	# provide un¡sername and password
    client.on_connect = on_connect		# define what function to call on connect
    print ("Connecting with Mosquitto:", broker)# 
    client.connect(broker, port)		# connect 
    return client				# return the client instance


def subscribe(client: mqtt_client):		# subcribe to the mosquitto serve with a tocpic

    def on_message(client, userdata, msg):	# this function is called for each messages retrieved from the Mosquitto
        message=msg.payload.decode()		# decode a UTF-8
	
        foundone = False			# assuming nothing found
        loopcount = userdata[0]["message_count"]# counter on the buffer 
        datafix   = userdata[1]["datafix"]	# buffer
        prt       = userdata[2]["prt"]		# print on|off
        aprspush  = userdata[3]["aprspush"]	# send data to APRS on|off
        #print ("UUU", loopcount, datafix, prt, aprspush, message)
        if prt:					# print some debuggin info
           print("message topic=",msg.topic)
           print("message qos=",msg.qos)
           print("message retain flag=",msg.retain)

        try:					# just in case of JSON not conformed
            j_obj = json.loads(message)         # convert to JSON
        except:
            print("JSON error:>>>>>", message, "<<<<<\n\n")
            return()
        while True:				# check if it is eligible
           if "timestamp" in j_obj:		# check if we have the timestamp        
               t=j_obj['timestamp']	    	# when the aircraft was seen
        					# ISO 8601 format: 2026-03-24T05:59:44
           else:
               print ("BSTOP No timestamp")	#
               break				# ignore the traffic with no timestamp
           d = datetime.fromisoformat(t)	# we use the timestamp as time of the fix
           tme  =d.strftime("%H%M%S")		# time in the format HHMMSS
           date = d.strftime("%y%m%d")		# date in the format YYMMDD
           #date = t[2:4]+t[5:7]+t[8:10]	# date and time in the format YYMMDD and HHMMSS
           #tme =  t[11:13]+t[14:16]+t[17:19]	# we use the timestamp as time of the fix, and we ignore the time when we receive the message, because it can be delayed
           lat=   j_obj['latitude']		# latitude
           lon=   j_obj['longitude']		# longitude
           if     j_obj['altitude_m']:		# altitude
                  alt= j_obj['altitude_m']*3.28084	# altitude in meters
           else:
                  alt= -1
                  break				# ignore if no altitude

           if alt > int(config.BSTOPfl):	# ignore if FL > 150
                  break

           birdid=j_obj['id']			# the ID of the birdstop device
           src='BSTOP'				# BSTOP is the default
           if "id" in j_obj:			# check if we have the ID of the target
               ID = j_obj['id'].upper()		# aircraft/bird/drone ID
           else:
               print ("BSTOP No id")
               break				# ignore the traffic with no ID
           ID = ID[-6:].replace('_','0')	# get the last 6 characters of the ID
           if ID.isnumeric():			# in case of number, convert to hex
              ID="%05X"%int(ID)			# convert to hex
           aid="OGNF"+ID[-5:]			# build the ICAO ID for OGN
           unitid="37F"+ID[-5:]			# build the uniqueID for OGN
           roc= 0 
           flg=0
           ecat=''
           if "type" in j_obj:			# check if drone or bird
              otype = j_obj['type']		# get the type of the target
              ecat = otype.upper()		# get the category	
           if 'speed_ms' in j_obj:		# if provided
                  gs=j_obj['speed_ms']*1.94384 	# ground speed in knots
           else:
                  gs=0.0			# if no speed provided 
                  break
           if gs > 999.9:
                  gs=999.0
           gs = int(gs)				# convert it to integer from float

           if     j_obj['heading']:		# true heading
                  trk=   int(j_obj['heading'])
           else:
                  trk=0
           if trk > 360:
                  trk=0


           vitlat = config.FLOGGER_LATITUDE	# get the distance to the dummy station 
           vitlon = config.FLOGGER_LONGITUDE
           distance = geodesic((lat, lon), (vitlat, vitlon)).km            # distance to the station
						# the dict with the info
           pos = {"ICAOID":aid, 'date':date, 'time':tme, 'Lat' :lat, 'Long':lon, 'altitude':alt, 'speed': gs, 'course': trk, 'roc': roc, 'rot':0, 'UnitID':unitid, 'extpos':'NO', 'dist':distance, 'GPS':'NO', 'flight':flg, 'FL':0, 'source':'ADSB', 'cat':ecat}  
           foundone = True			# mark that we found one
           userdata[1]["datafix"].append(pos)	# we added to the buffer
           userdata[0]["message_count"] += 1	# increase the counter on the buffer
           break

        #print ("LLL", loopcount, userdata[0]["message_count"] )
       
        datafix = userdata[1]["datafix"]	# we had stored the messages on the datafix array
        utc = naive_utcnow()
        if prt:					# for debugging
           print (">>>BSTOP:", loopcount, len(datafix), utc,  aprspush, prt)
        if aprspush:				# if we asked for APRSpush
           bstopaprspush(datafix, prt)		# push the data to the OGN APRS
           userdata[1]["datafix"]= []		# reset the buffer
        if (loopcount - int(loopcount/100000)*100000) == 0: 	# we send to the APRS in check of 100K messages
              global savedtime
              current_time = time.time()
              timediff=current_time-savedtime
              #print ("TTT", current_time, savedtime, timediff)
              mpsec=int(6000000.0/timediff)	# request per minute
              savedtime=current_time
        
              print (">>>BSTOP::", loopcount, "TimeDiff:", int(timediff),"Secs. ", mpsec, "msgs per minute, ", utc,  aprspush, prt, "::<<<<\n")

# -------------------------------------------	# end of on_message function
    if prt:
       print ("Subscribing to topic:", topic)	# just for debugging
    client.subscribe(topic)			# subcribe with that topic
    client.on_message = on_message		# define the function to call for each message
    return (client)				# return the client instance

def on_disconnect(client, userdata, rc):	# in the case of disconnect try to send the messages on the buffer

    loopcount = userdata[0]["message_count"]	# counter on the buffer 
    datafix   = userdata[1]["datafix"]
    prt       = userdata[2]["prt"]
    aprspush  = userdata[3]["aprspush"]
    utc = naive_utcnow()
    if prt:
       print ("Disconnecting ...", rc)
       print (">>>bstop:::", loopcount, len(datafix), utc,  aprspush, prt, rc, "<<<")
    if aprspush:				# if aprspush ... push the remaining data
       if len(datafix) > 0:			# if we have data on the buffer, push it to the OGN APRS
          bstopaprspush(datafix, prt)		# push the data to the OGN APRS
       userdata[0]["message_count"] = 0		# reset the counter on the buffer	
       userdata[1]["datafix"]= []		# reset the buffer
    client = 0					# reset the mqtt instance
    config.CLIENT = 0				# and the global pointer
    sleep (2)					# give it a chance to recover
    return(rc)
    

def bstopini(prt=False, aprspush=False):		# init the mosquito client

    global savedtime
    savedtime = time.time()
    client = connect_mqtt()			# create instance and connect
    client.user_data_set([{"message_count": 1}, {"datafix" :  []}, {'prt': prt}, {'aprspush':aprspush}])
    subscribe(client)				# subcribe to the bstop Etopic
    config.CLIENT=client			# save the client object
    client.on_disconnect = on_disconnect	# in case of disconect

    return(client)

def bstoprun(prt=False, aprspush=False):		# run the normal work

    client=config.CLIENT			# the mosquitto instance pointer
    if (client != 0):				# if not disconnected ???
       client.loop(5)				# give it 5 seconds to get all the messages
    else:					# init the broker again
       print ("Reinitialize the Mosquitto broker ...")
       bstopini(prt, aprspush)			# inititlize the mosquitto	
       client=config.CLIENT			# point to the new client
       client.loop(5)				# and recover the messages for 5 seconds again
     
     
def bstopfinish(prt=False, aprspush=False):	# run the normal work

    client=config.CLIENT			# point to the global instance
    if prt:
       print ("bstop finishing ...")
    client.disconnect()				# disconnect the mosquitto client
     



#-------------------------------------------------------------------------------------------------------------------#
# Store the data into the DDBB
#-------------------------------------------------------------------------------------------------------------------#

def bstopstoreitindb(datafix, curs, conn):   	# store the fix into the database

    import MySQLdb                          	# the SQL data base routines^M
    for fix in datafix:	    			# for each fix on the dict
        iid       = fix['ICAOID']	    	# extract the information
        dte       = fix['date']
        hora      = fix['time']
        station   = config.location_name
        latitude  = fix['Lat']
        longitude = fix['Long']
        altitude  = fix['altitude']
        speed     = fix['speed']
        course    = fix['course']
        roclimb   = fix['roc']
        rot       = fix['rot']
        sensitivity = 0
        gps       = fix['GPS']
        uniqueid  = str(fix["UnitID"])
        dist      = fix['dist']
        extpos    = fix['extpos']

        if altitude == None or altitude == 0:
            print ("STOREITINDB No altitude:", altitude, speed, roclimb)
            continue								# ignore the traffic with no altitude

        addcmd = "insert into OGNDATA values ('" + iid + "','" + dte + "','" + hora + "','" + station + "'," + \
            str(latitude) + "," + str(longitude) + "," + str(altitude) + "," + str(speed) + "," + \
            str(course) + "," + str(roclimb) + "," + str(rot) + "," + str(sensitivity) + \
            ",'" + gps + "','" + uniqueid + "'," + \
            str(dist) + ",'" + extpos + "', 'bstop' ) "
        try:				    	# store it on the DDBB
            #print addcmd
            curs.execute(addcmd)
        except MySQLdb.Error as e:		# if we have an error, we print it and we return False
            try:
                print(">>>MySQL Error [%d]: %s" % (e.args[0], e.args[1]))
            except IndexError:
                print(">>>MySQL Error: %s" % str(e))
                print(">>>MySQL error:", addcmd)
            return (False)                  	# indicate that we have errors
    conn.commit()                           	# commit the DB updates
    return(True)			    	# indicate that we have success

#-------------------------------------------------------------------------------------------------------------------#
# Push the data received into the OGN APRS
#-------------------------------------------------------------------------------------------------------------------#
#APRSMSG:  OGNF0D3F7>OGBSTOP,qAS,SpaiBSTOP:/235811h4318.13N\00822.61W^000/000/A=000173 id37F0D3F7  !W05!  Bird
#APRSMSG:  OGNF0D3F9>OGBSTOP,qAS,SpaiBSTOP:/000000h4318.27N\00822.45W^000/000/A=000173 id37F0D3F9  !W10!  Bird
#-------------------------------------------------------------------------------------------------------------------#


def bstopaprspush(datafix, prt=False):
    if prt:
        print ("APRSpush start: ", len(datafix))
    cnt=0					# counter of messgages
    for fix in datafix:	    			# for each fix on the dict
        if prt:
           print ("FIX: ", fix)
        aid      = fix['ICAOID']		# extract the information
        dte      = fix['date']
        hora     = fix['time']
        station  = config.location_name
        latitude = fix['Lat']
        longitude= fix['Long']
        daotxt="!W"+dao(latitude)+dao(longitude)+"!"  # the extended precision
        altitude = fix['altitude']
        speed    = fix['speed']
        course   = fix['course']
        roclimb  = fix['roc']
        rot      = fix['rot']
        sensitivity = 0
        gps      = fix['GPS']
        uniqueid = fix["UnitID"]
        src      = fix['source']
        dist     = fix['dist']
        extpos   = fix['extpos']
        flight   = fix['flight']
        FL       = fix['FL']
        cat      = fix['cat']
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
        if roclimb == None:
            roclimb = 0
        aprsmsg = aid+">OGBSTOP,qAS,"+config.BSTOPname+":/" + \
            hora+'h'+lat+"\\"+lon+"^"+ccc+"/"+sss+"/"
        if altitude != None and altitude > 0:
            aprsmsg += "A=%06d" % int(altitude)
        else:
            print ("APRSPUSH No altitude:", altitude, speed, roclimb)
            continue								# ignore the traffic with no altitude
        aprsmsg += " id"+uniqueid+" %+04dfpm " % (int(roclimb))+" "+str(rot)+"rot "+daotxt+" "
        if cat != None and cat != '':
           aprsmsg += " "+cat
        aprsmsg += " \n" 
        print("APRSMSG: ", aprsmsg[0:-1])
        rtn = config.SOCK_FILE.write(aprsmsg)
        if rtn == None or rtn == 0 :
            print("Error writing msg:", aprsmsg)
            return(0)
        try:
           config.SOCK_FILE.flush()
        except Exception as e:
           print ("error on flush: ", e)
        cnt += 1

    return (cnt)

#-------------------------------------------------------------------------------------------------------------------#
#LEMD>OGNSDR,TCPIP*,qAC,GLIDERN2:/141436h4030.49NI00338.59W&/A=002280
#LEMD>OGNSDR,TCPIP*,qAC,GLIDERN2:>141436h v0.2.8.RPI-GPU CPU:0.6 RAM:710.8/972.2MB NTP:0.3ms/-5.5ppm +56.9C 2/2Acfts[1h] RF:+50-3.2ppm/+0.76dB/+47.4dB@10km[3859]
#-------------------------------------------------------------------------------------------------------------------#


#-------------------------------------------------------------------------------------------------------------------#
# Build a dummy receiver
#-------------------------------------------------------------------------------------------------------------------#

def bstopsetrec(sock, prt=False, store=False, aprspush=False):			# define on APRS the dummy OGN station
    t = naive_utcnow()       		# get the date
    tme = t.strftime("%H%M%S")
    aprsmsg=config.BSTOPname+">OGNSDR,TCPIP*:/"+tme+"h"+config.BSTOPloc+" BSTOP dummy station \n"
    if prt:
       print("APRSMSG: ", aprsmsg)
    rtn = sock.write(aprsmsg)
    try:
       sock.flush()
    except Exception as e:       
       print ("error on flush: ", e)
    if rtn == 0:
       print("Error writing msg:", aprsmsg)
    tempcpu = 0.0
    cpuload =psutil.cpu_percent()/100
    memavail=psutil.virtual_memory().available/(1024*1024)
    memtot=psutil.virtual_memory().total/(1024*1024)
    aprsmsg=config.BSTOPname+">OGNSDR,TCPIP*:>"+tme+"h v0.3.0.BSTOP CPU:"+str(cpuload)+" RAM:"+str(memavail)+"/"+str(memtot)+"MB NTP:0.4ms/-5.4ppm +"+str(tempcpu)+"C\n"
    if prt:
       print("APRSMSG: ", aprsmsg)
    rtn = sock.write(aprsmsg)
    try:
       sock.flush()
    except Exception as e:       
       print ("error on flush: ", e)
    return

#-------------------------------------------------------------------------------------------------------------------#
if __name__ == '__main__':
    try:
       import config
       bstopini()
       bstoprun()
    except KeyboardInterrupt:
       print("Keyboard input received, ignore")
       exit()


