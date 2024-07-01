#!/bin/python3
#-------------------------------------------------------------------------------------------------------------------#
# this functions deals with the data received by the ENAIRE netwoar thru the Mosquitto server
#-------------------------------------------------------------------------------------------------------------------#
 

# python 3.11

import random
import json
import time
import psutil
import config
import adsbregfuncs
from   adsbregfuncs import getadsbreg, getsizeadsbcache
from   time import sleep

from   datetime import datetime
from   geopy.distance import geodesic       	# use the Vincenty algorithm^M
from   parserfuncs import deg2dmslat, deg2dmslon, dao
from   paho.mqtt import client as mqtt_client

msgsample= {					# sample of data comming form ENAIRE
    "lat": 39.5751748,
    "lon": -0.7216797,
    "icao_registration": "344645",
    "ground_bit_set": 0,
    "altitude": 3425,				# altitud in feet
    "barometric_vertical_rate": 62.5,		# RoC in feet per minute
    "ground_speed": 171.16704000000001,		# GS in knots
    "squawk_code": "0272",
    "flight_number": "VLG412B",
    "heading": 110.8685303, 			# true north
    "ecat": 3,
    "timestamp": 1717686297.6484375		# tiem from epoch
}
mmm= {
    "lat": 40.3646542,
    "lon": -3.4543261,
    "icao_registration": "342105",
    "ground_bit_set": 0,
    "altitude": 3875,
    "barometric_vertical_rate": 193.75,
    "ground_speed": 0.0493164,
    "squawk_code": "5117",
    "flight_number": "IBS3947",
    "heading": 322.097168,
    "ecat": 3,
    "timestamp": 1718179739.7421875
}
global savedtime
savedtime = time.time()

# ----------------------------------------------------------------------------------------------------------------

# Generate a Client ID with the subscribe prefix.
client_id = f'OGNENA-{random.randint(0, 100)}' 	# name of the client OGNENA-001
broker    = config.ENAMQTT			# URL of the Mosquitto server
port      = 1883				# the default
topic     = config.ENATOPIC			# the susbcrive TOPIC that matches the publish topic
username  = config.ENAUSER			# the user
password  = config.ENAPASSWD			# the passowrd 


def on_connect(client, userdata, flags, rc):	# function clled on connect

     if rc == 0:
         print("Connected to MQTT Broker!")	# just inform of it
     else:
         print("Failed to connect, return code %d\n", rc)

def connect_mqtt() -> mqtt_client:		# connect to the Mosquitto server

    client = mqtt_client.Client(client_id)

    client.username_pw_set(username, password)	# provide un¡sername and password
    client.on_connect = on_connect		# define what function to call on connect
    print ("Connecting with Mosquitto:", broker)# 
    client.connect(broker, port)		# connect 
    return client				# return the client instance


def subscribe(client: mqtt_client):		# subcribe to the mosquitto serve with a tocpic

    def on_message(client, userdata, msg):	# this function is called for each messages retrieved from the Mosquitto
        message=msg.payload.decode()		# decode a UTF-8
	
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
           if 'ground_bit_set' in j_obj:	# ignore traffics on the ground
              if j_obj['ground_bit_set']:
                 break
           ttt =  j_obj['timestamp']		# message time
           ts = int(ttt)       			# Unix time - seconds from the epoch
           t=datetime.utcfromtimestamp(ts)	# convert to time object the number os seconds from epoc
           date = t.strftime("%y%m%d")		# date and time
           tme = t.strftime("%H%M%S")
           lat=   j_obj['lat']			# latitude
           lon=   j_obj['lon']			# longitude
           if     j_obj['altitude']:		# altitude
                  alt=   j_obj['altitude']
           else:
                  alt= -1
                  break				# ignore if no altitude

           if alt > int(config.ENAfl):		# ignore if FL > 150
                  break

           icaoid=j_obj['icao_registration']# ICAO ID 24 bits
           if    'barometric_vertical_rate' in j_obj and j_obj['barometric_vertical_rate']:	# rate of climb
                  roc=   int(j_obj['barometric_vertical_rate'])
           else:
                  roc= 0 

           if 'ground_speed' in j_obj:		# if provided
                  gs=j_obj['ground_speed']*1.0  # ground speed in knots
           else:
                  gs=0.0			# if no speed provided 
                  break
           if gs > 999.9:
                  gs=999.0
           gs = int(gs)				# convert it to integera

           if     j_obj['heading']:		# true heading
                  trk=   int(j_obj['heading'])
           else:
                  trk=0
           if trk > 360:
                  trk=0

           if     'flight_number' in j_obj and  j_obj['flight_number']:	# flight number
                  flg=   j_obj['flight_number']	
           else:
                  flg=''

           if     'ecat' in j_obj and  j_obj['ecat']:	# category
                  ecat=   j_obj['ecat']	
           else:
                  ecat=''

           vitlat = config.FLOGGER_LATITUDE	# get the distance to the dummy station 
           vitlon = config.FLOGGER_LONGITUDE
           distance = geodesic((lat, lon), (vitlat, vitlon)).km            # distance to the station
						# the dict with the info
           pos = {"ICAOID":icaoid, 'date':date, 'time':tme, 'Lat' :lat, 'Long':lon, 'altitude':alt, 'speed': gs, 'course': trk, 'roc': roc, 'rot':0, 'UnitID':icaoid, 'extpos':'NO', 'dist':distance, 'GPS':'NO', 'flight':flg, 'FL':0, 'source':'ADSB', 'cat':ecat}  
           
           userdata[1]["datafix"].append(pos)	# we added to the buffer
           userdata[0]["message_count"] += 1	# increase the counter on the buffer
           break

        #print ("LLL", loopcount, userdata[0]["message_count"] )

        if (loopcount - int(loopcount/100)*100) == 0: 	# we send to the APRS in check of 100 messages
           #print(f"Received `{message}` from `{msg.topic}` topic", loopcount)
           datafix   = userdata[1]["datafix"]	# we had stored the messages on the datafix array
           utc = datetime.utcnow()
           if prt:				# for debugging
              print (">>>ENA:", loopcount, len(datafix), utc,  aprspush, prt)
           if aprspush:				# if we asked for APRSpush
              enaaprspush(datafix, prt)		# push the data to the OGN APRS
              userdata[1]["datafix"]= []	# reset the buffer
        if (loopcount - int(loopcount/100000)*100000) == 0: 	# we send to the APRS in check of 100K messages
              global savedtime
              current_time = time.time()
              timediff=current_time-savedtime
              #print ("TTT", current_time, savedtime, timediff)
              mpsec=int(6000000.0/timediff)		# request per minute
              savedtime=current_time
        
              print (">>>ENA::", loopcount, "TimeDiff:", int(timediff),"Secs. ", mpsec, "msgs per minutei ", utc,  aprspush, prt, "::<<<<")

# -------------------------------------------	# end of on_message function

    client.subscribe(topic)			# subcribe with that topic
    client.on_message = on_message		# define the function to call for each message
    return (client)				# return the client instance

def on_disconnect(client, userdata, rc):	# in the case of disconnect try to send the messages on the buffer

    loopcount = userdata[0]["message_count"]# counter on the buffer 
    datafix   = userdata[1]["datafix"]
    prt       = userdata[2]["prt"]
    aprspush  = userdata[3]["aprspush"]
    if prt:
       print ("Disconnecting ...", rc)
    if aprspush:				# if aprspush ... push the remaining data
       enaaprspush(datafix, prt)
       userdata[0]["message_count"] = 0
       userdata[1]["datafix"]= []
    utc = datetime.utcnow()
    print (">>>ENA:::", loopcount, len(datafix), utc,  aprspush, prt, rc, "<<<")
    client = 0					# reset the mqtt instance
    config.CLIENT = 0				# and the global pointer
    sleep (2)					# give it a chance to recover
    return(rc)
    

def enaini(prt=False, aprspush=False):		# init the mosquito client

    global savedtime
    savedtime = time.time()
    client = connect_mqtt()			# create instance and connect
    client.user_data_set([{"message_count": 1}, {"datafix" :  []}, {'prt': prt}, {'aprspush':aprspush}])
    subscribe(client)				# subcribe to the ENAIRE topic
    config.CLIENT=client			# save the client object
    client.on_disconnect = on_disconnect	# in case of disconect

    return(client)

def enarun(prt=False, aprspush=False):		# run the normal work

    client=config.CLIENT			# the mosquitto instance pointer
    if (client != 0):				# if not disconnected ???
       client.loop(5)				# give it 5 seconds to get all the messages
    else:					# init the broker again
       print ("Reinitialize the Mosquitto broker ...")
       enaini(prt, aprspush)			# inititlize the mosquitto	
       client=config.CLIENT			# point to the new client
       client.loop(5)				# and recover the messages for 5 seconds again
     
     
def enafinish(prt=False, aprspush=False):	# run the normal work

    print ("ENA finishing ...")
    client=config.CLIENT			# point to the global instance
    client.disconnect()				# disconnect the mosquitto client
     

#-------------------------------------------------------------------------------------------------------------------#
# Push the data received into the OGN APRS
#-------------------------------------------------------------------------------------------------------------------#

def enaaprspush(datafix, prt=False):

    for fix in datafix:	    			    # for each fix on the dict
        id       = fix['ICAOID']		    # extract the information
        dte      = fix['date']
        hora     = fix['time']
        station  = config.location_name
        station  = 'SpainTTT'
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
        if src == 'OGN':
           uniqueid = '07'+uniqueid[3:]
           continue
        else:   
           uniqueid = '25'+uniqueid[3:]
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
        ENAname=config.ENAname
        aprsmsg = "ICA"+id+">OGADSB,qAS,"+ENAname+":/" + \
            hora+'h'+lat+"\\"+lon+"^"+ccc+"/"+sss+"/"
        if altitude != None and altitude > 0:
            aprsmsg += "A=%06d" % int(altitude)
        else:
            continue								# ignore the traffic with no altitude
        aprsmsg += " id25"+id+" %+04dfpm " % (int(roclimb))+" "+str(rot)+"rot "+daotxt+" " 
        if flight and flight != '':
           if cat != '':
               aprsmsg += "fnA"+str(cat)+":"+flight+" "
           else:
               aprsmsg += "fn:"+flight+" "
        regmodel = getadsbreg(id)
        if FL > 0 :
           aprsmsg += " FL%03d " % int(FL)
        if regmodel:
            reg =regmodel['Reg']
            model=regmodel['Model']
            aprsmsg += "reg"+reg+" model"+model+" \n"
        else:
            aprsmsg += " \n"
        if prt:
           print ("APRSMSG:", aprsmsg)
        rtn = config.SOCK_FILE.write(aprsmsg)
        config.SOCK_FILE.flush()

        if rtn == 0:
            print("Error writing msg:", aprsmsg)

    return (True)

#-------------------------------------------------------------------------------------------------------------------#
# Build a dummy receiver
#-------------------------------------------------------------------------------------------------------------------#

def enasetrec(sock, prt=False, store=False, aprspush=False):			# define on APRS the dummy OGN station
    t = datetime.utcnow()       		# get the date
    tme = t.strftime("%H%M%S")
    aprsmsg=config.ENAname+">OGNSDR,TCPIP*:/"+tme+"h"+config.ENAloc+" \n"
    if prt:
       print("APRSMSG: ", aprsmsg)
    rtn = sock.write(aprsmsg)
    sock.flush()
    if rtn == 0:
        print("Error writing msg:", aprsmsg)
    tempcpu = 0.0
    cpuload =psutil.cpu_percent()/100
    memavail=psutil.virtual_memory().available/(1024*1024)
    memtot =psutil.virtual_memory().total/(1024*1024)
    aprsmsg =config.ENAname+">OGNSDR,TCPIP*:>"+tme+"h v0.3.0.ENA CPU:"+str(cpuload)+" RAM:"+str(memavail)+"/"+str(memtot)+"MB NTP:0.4ms/-5.4ppm +"+str(tempcpu)+"C\n"
    if prt:
       print("APRSMSG: ", aprsmsg)
    rtn = sock.write(aprsmsg)
    sock.flush()
    return



if __name__ == '__main__':
    try:
       import config
       enaini()
       enarun()
    except KeyboardInterrupt:
       print("Keyboard input received, ignore")
       exit()


