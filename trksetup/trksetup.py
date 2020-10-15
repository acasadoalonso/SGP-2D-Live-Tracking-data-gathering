#!/usr/bin/python3
######################################################################
# This program reads thhe config params inside the tracker and set the new ones
######################################################################
import argparse
import serial
from time import sleep          # use the sleep function
import time
import ttn
import json
import datetime
import signal
import os
import binascii

def signal_term_handler(signal, frame):
    mqtt_client.close()
    print('got SIGTERM ... Bye...: ', counter)
    os._exit(0)

########
def getdevappkey(app_client, dev_id):
    device      = app_client.device(dev_id)
    ld= device.lorawan_device
    APP_key  = binascii.b2a_hex(ld.app_key).decode('utf-8').upper()
    return (APP_key)


########
def printparams(ser, trkcfg, prt=False):	# print the parameters 
				# ser serial, trkcfg the tracker configuration table possible values
    ID=""			# tracker ID
    MAC=""			# tracker MAC ID
    cnt=0
    param={}			# params decoded
    etx=b'\x03'			# the Control C
    while cnt < 100:		# at least 100 lines !!!
        line = ser.readline()   # read a '\n' terminated line
        if len(line) == 0:      # end of data ???
           break		# all done
        l=line.decode('utf-8').rstrip()
        if cnt == 0:		# first line is the ID
           ID=line[0:10]
           MAC=line[11:23]
           if ID[0:4] != b'1:3:':
              print("ID>>>:", ID)
              ser.write(etx)	# send a Ctrl-C 
              continue
        if l[0:7] == '/spiffs':	# ignore the spiffs lines
           continue
        if prt:
        	print (l)	# print the data received
        cnt += 1		# increase the counter
        sv=l.find(" = ")	# look for the = sign
        if sv == -1:		# if not found ignore the line
           continue
        for par in trkcfg:	# scan for config parameters
            s  = l.find(' ')	# look for te first space
            p  = l[0:s]		# get only the first token
            sc = l.find(';')	# look for the end of the value
            v  = l[sv+3:sc]	# get the value
            if par == p :	# it is our param ?
               if v[0:2] == '0x':
                  v=int(v, 16)
               param[par]=v	# yes, save the value 
               break
    if ID == '':
       print ("ID:", ID, "Please check if the tracker is ON !!!") 
       return False  
    trackerID=ID[4:].decode('utf-8')
    MAC=MAC.decode('utf-8')
    param["TrackerID"]=trackerID
    param["MAC"]=MAC
    if prt:
    	print ("Tracker ID:", trackerID, "MAC:", MAC)
    	print ("Parameters:\n", param, "\n")
    return(param)		# return the table with the parameters already parsed
#######
trkcfg=[ "Address", 		# config parameters to scan
         "AddrType",
         "AcftType",
         "Encrypt",
         "EncryptKey[0]",
         "EncryptKey[1]",
         "EncryptKey[2]",
         "EncryptKey[3]",
         "Verbose",
         "BTname",
         "Pilot",
         "Crew",
         "Manuf",
         "Model",
         "Type",
         "SN",
         "ID",
         "Reg",
         "Class",
         "Task",
         "Base",
         "ICE",
         "TrackerID",
         "PilotID"]

#######
# .....................................................................#
signal.signal(signal.SIGTERM, signal_term_handler)
# .....................................................................#


app_id     = "ogn"
dev_id     = ""
appEui     = "70B3D57ED0035895"
appKey     = "ttn-account-v2.V4Z-WSzqhfR0FKiKFYu4VLgNEbxP9QluACwD1pSfwmE"



#######
# --------------------------------------#
#
# OGN tracker SETUP manager 
#
# --------------------------------------#
print ("\n\nOGN tracker setup program:\nIt gets the information from the tracker firmware and hendles the setup parameter.\nThe tracker mus be connected to the USB port.")
print ("==================================================================================\n\n")
import config			# get the configuration parameters
parser = argparse.ArgumentParser(description="OGN manage the OGN TRACKERS setup parameters")
parser.add_argument('-p', '--print',       required=False, dest='prt',      action='store', default=False)
parser.add_argument('-u', '--usb',         required=False, dest='usb',      action='store', default=0)
parser.add_argument('-s', '--setup',       required=False, dest='setup',    action='store', default=False)
parser.add_argument('-k', '--printkeys',   required=False, dest='keys',     action='store', default=False)
parser.add_argument('-kf','--keyfile',     required=False, dest='keyfile',  action='store', default='keyfile')
parser.add_argument('-o', '--ognddb',      required=False, dest='ognddb',   action='store', default=True)
parser.add_argument('-t', '--ttn',         required=False, dest='ttn',      action='store', default=True)
parser.add_argument('-n', '--noencrypt',   required=False, dest='noencr',   action='store', default=True)

args  	= parser.parse_args()
prt   	= args.prt
setup 	= args.setup
keys  	= args.keys
usb   	= args.usb			
keyfile	= args.keyfile			
ognddb	= args.ognddb
ttnopt	= args.ttn
noencr	= args.noencr

if ognddb == "False":
   ognddb = False
else:
   ognddb = True			

if ttnopt == "False":
   ttnopt = False
else:
   ttnopt = True			

if noencr == "False":
   noencr = False
else:
   noencr = True			

# --------------------------------------#
keyfilename=keyfile		# name of the file containing the encryption keys
keyfilename='keyfile'		# name of the file containing the encryption keys
etx=b'\x03'			# the Control C
DecKey=[]			# the 4 hex values of the key
key=getkeyfile(keyfilename)	# get the key from the keyfile
DecKey=getkeys(DecKey, key)	# get the keys 4 words
#print (DecKey)
# --------------------------------------#
DBpath      = config.DBpath
DBhost      = config.DBhost
DBuser      = config.DBuser
DBpasswd    = config.DBpasswd
DBname      = config.DBname
OGNT        = config.OGNT

if not ognddb:
   import MySQLdb               # the SQL data base routines
				# open the DataBase
   conn = MySQLdb.connect(host=DBhost, user=DBuser, passwd=DBpasswd, db=DBname)

   print("MySQL: Database:", DBname, " at Host:", DBhost)
else:
   from ognddbfuncs import *
   print("Using OGN DDB database \n")

# --------------------------------------#
i=0
if not noencr:
    from Keys import *		# get the key handling functions
    import ogndecode
    encryptcmd=b'$POGNS,EncryptKey='# prepare the encryption keys
    for k in DecKey:		# prepare the format
        kh=hex(k)
        h=kh[2:]
        if i != 0:
          encryptcmd += b':'
        encryptcmd += h.encode('utf-8')
        if i == 3:
          encryptcmd += b'\n'
        if keys:
    	    print ("Key"+str(i)+":",h)
        i += 1
if usb == '-1':
        exit(0)
				# set the parameters 
ser 			= serial.Serial()
ser.port 		= '/dev/ttyUSB'+str(usb)
ser.baudrate 		= 115200
ser.parity		= serial.PARITY_NONE
ser.timeout		= 1
ser.break_condition	= True

ser.open()			# open the tracker console
#--------------------------------------#

ser.send_break(duration=0.25)	# send a break 
ser.write(b'$POGNS,Verbose=0\n')# make no verbose to avoid other messages
ser.write(b'$POGNS,Verbose=0\n')# do it again
ser.write(etx)			# send a Ctrl-C 
sleep(1)			# wait a second to give a chance to receive the data
try:
   param=printparams(ser, trkcfg, prt)# get the configuration parameters
except:
   ser.write(b'$POGNS,BTname=123456\n')# make no verbose to avoid other messages
   ser.write(b'$POGNS,BTname=123456\n')# do it again
   ser.write(etx)		# send a Ctrl-C 
   param=printparams(ser, trkcfg, prt)# get the configuration parameters
if param == False:		# if noot found, nothing else to do
   exit(1)
ID=param['TrackerID']		# get the tracker ID
MAC=param['MAC']		# get the tracker MAC ID
if not prt:
   print (param)		# if not prints it yet 
   print("\n\nTracker ID=", ID, "MAC", MAC, "\n\n")# tracker ID
if keys and not noencr:
	print (encryptcmd) 	# print the encrypt command
if setup and not noencr:
	ser.write(encryptcmd)	# Write the encryption keys
	ser.write("$POGNS,Encrypt=1".encode('utf-8')) 
sleep(1)			# wait a second to give a chance to receive the data
found=False			# assume not found YET
if ognddb:			# if using the OGN DDB
   devid=ID
   info=getogninfo(devid)	# get the info from the OGN DDB
   if info == "NOInfo":
        pass			# nothing to do
   else:
        if prt:
           print (info)
        ogntid 	= info['device_id']	# OGN tracker ID
        flarmid = info['device_aprsid']	# Flarmid id to be linkeda
        devtype = info['device_type']	# device type (glider, powerplane, paraglider, etc, ...)
        regist 	= info['registration'] 	# registration id to be linked
        pilot 	= 'OGN/IGC_Tracker'  	# owner
        compid 	= info['cn']  		# competition ID
        model  	= info['aircraft_model']  	# model
        print ("From OGN DDB:", ogntid, devtype, flarmid, regist, pilot, compid, model) 
        found=True
else:
   curs = conn.cursor()         # set the cursor for searching the devices
                                # get all the devices with OGN tracker
   curs.execute("select id, flarmid, registration, owner, compid, model from TRKDEVICES where devicetype = 'OGNT' and active = 1 and id = '"+ID+"'; ")
   for rowg in curs.fetchall(): 	# look for that registration on the OGN database

        ogntid 	= rowg[0]	# OGN tracker ID
        flarmid = rowg[1]	# Flarmid id to be linked
        regist 	= rowg[2]  	# registration id to be linked
        pilot 	= rowg[3]  	# owner
        compid 	= rowg[4]  	# competition ID
        model  	= rowg[5]  	# model
        devtype = 1		# always glider
        info    = {'device_id': ogntid, 'device_aprsid':flarmid, 'device_type' : 1, 'registration': regist, 'pilot' : pilot, 'cn': compid, 'aircraft_model' : model}
        print ("From DB:", ogntid, flarmid, regist, pilot, compid, model) # whatch out for multiples Ids !!!!
        print (info)
        if found:		# if found one already ???
           print("WARNING: Multiple IDs for the same tracker !!!! --> ", ID, ogntid)
        found=True
   if not found:
        print ("Device not found on the DataBase\n\n")
print( "==============================================================================================")
if found:			# set the last one !!!
   APP_key=''
   if ttnopt:

      devicetest = {      # the device dict
        "description"     : "OGN/IGC-"+regist+" ",
        "appEui"          : appEui,
        "devEui"          : "0000"+MAC,
        "appKey"          : binascii.b2a_hex(os.urandom(16)).upper(), 
        "fCntUp"          : 10,
        "fCntDown"        : 11,
        "latitude"        : 100,
        "longitude"       : 200,
        "altitude"        : 300,
        "disableFCntCheck": True,
        "uses32BitFCnt"   : True,
        "attributes"      : { "info": compid},
      }
      # ------------------------------------------------------------------ #
      dev_id      = flarmid.lower()
      handler     = ttn.HandlerClient    (app_id, appKey)
      app_client  = ttn.ApplicationClient(app_id, appKey, handler_address="", cert_content="/home/angel/.ssh/id_ras.pub", discovery_address="discovery.thethings.network:1900")
      if setup:
         try:
            app_client.delete_device  (dev_id)
         except:
            print ("Deleting Device:", dev_id, "with MAC:", MAC, "Not registered on the TTN\n")
         try:   
            app_client.register_device(dev_id, devicetest)
         except Exception as e:
            print ("Registering  Device error:", dev_id, "with MAC:", MAC,"Error:", e, "\n")
      try:
         device      = app_client.device(dev_id)
         ld          = device.lorawan_device
         APP_eui     = binascii.b2a_hex(ld.app_eui).decode('utf-8').upper()
         DEV_eui     = binascii.b2a_hex(ld.dev_eui).decode('utf-8').upper()
         DEV_addr    = binascii.b2a_hex(ld.dev_addr).decode('utf-8').upper()
         APP_key     = binascii.b2a_hex(ld.app_key).decode('utf-8').upper()
         lastseen    = int(ld.last_seen/1000000000)
         tme         = datetime.datetime.utcfromtimestamp(lastseen)
         print ("Device:   ", ld.dev_id, "On application:", ld.app_id, " with APPeui:", APP_eui, "DEVeui:", DEV_eui, "DEVaddr:", DEV_addr, "APPkey:", APP_key, "Last Seen:", tme.strftime("%y-%m-%d %H:%M:%S"), "\n\n")    
         print ("DevAppKey:", getdevappkey(app_client, dev_id), "\n\n")
      except Exception as e:
         print ("Device:", dev_id, "with MAC:", MAC, "Not registered on the TTN Error: ", e, "\n")

# ------------------------------------------------------------------ #

   if setup:			# if setup is required 
        cmd="$POGNS,Reg="+regist+"\n"
        ser.write(cmd.encode('UTF-8'))
        cmd="$POGNS,Pilot="+pilot+"\n"
        ser.write(cmd.encode('UTF-8'))
        cmd="$POGNS,ID="+compid+"\n"
        ser.write(cmd.encode('UTF-8'))
        cmd="$POGNS,Model="+model+"\n"
        ser.write(cmd.encode('UTF-8'))
        cmd="$POGNS,SN="+flarmid+"\n"
        ser.write(cmd.encode('UTF-8'))
        cmd="$POGNS,BTname="+flarmid+"\n"
        ser.write(cmd.encode('UTF-8'))
        cmd="$POGNS,Type="+str(devtype)+"\n"
        ser.write(cmd.encode('UTF-8'))
        cmd="$POGNS,AppKey="+APP_key+"\n"
        ser.write(cmd.encode('UTF-8'))
        ser.write(etx)		# send a Ctrl-C 
        sleep(1)			# wait a second to give a chance to receive the data
        printparams(ser, trkcfg, False)# print the new parameters
else:
   print("No information about the device on the databases !!!\n\n")
print( "==============================================================================================")
ser.close()
###################################################################################################################################################################
