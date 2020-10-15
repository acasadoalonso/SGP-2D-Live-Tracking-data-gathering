import time
import ttn
import ogndecode
import json
import datetime
import signal
import os
import binascii

def signal_term_handler(signal, frame):
    mqtt_client.close()
    print('got SIGTERM ... Bye...: ', counter)
    os._exit(0)

#access_key = "ttn-account-v2.UsmQcln8EfGNG8OakB-cwI0KAnZWa_jPmtEU9gcZyTw"
#appKey     = "CD9EAB0FBBD28811CDF28EC307196834"
counter = 0

def uplink_callback(msg, client):
  date = datetime.datetime.utcnow()                # get the date
  tme = date.strftime("%y-%m-%d %H:%M:%S")           # today's date
  global counter
  #print(msg)
  pl=msg[5]
  pf=msg[6]
  if pl == True:
     pl=msg[6]
     pf=msg[7]
  #print ("Fields:", pl, "\n\n")
  if len(pl)==28:
     print("Received uplink from ", msg.dev_id, " UTC time: ", tme, "Fields:", pf, "\n")
     j=ogndecode.ogn_decode_func_plain(pl)
     #print("J:tring===>>>",j,"\n\n")
     try:
        m = json.loads(j)
        print (m, "\n")
     except Exception as e:
        print (e, "J string: ===>", j, "<<<=\n\n")
  counter += 1
  return

def connect_callback(res, client):
  if res:
     print("connected")
  return

def getdevappkey(app_client):
    device      = app_client.device(dev_id)
    ld= device.lorawan_device
    APP_key  = binascii.b2a_hex(ld.app_key).decode('utf-8').upper()

    return(APP_key)
# .....................................................................#
signal.signal(signal.SIGTERM, signal_term_handler)
# .....................................................................#


app_id     = "ogn"
dev_id     = "ogn60e6a0"
dev_id     = "ogn8e20f0"
appEui     = "70B3D57ED0035895"
appKey     = "ttn-account-v2.V4Z-WSzqhfR0FKiKFYu4VLgNEbxP9QluACwD1pSfwmE"


devicetest = {
  "description": "OGN-Tracker-test1",
  "appEui": "70B3D57ED0035895",
  "devEui": "00003C71BF60E6A0",
  "appKey": binascii.b2a_hex(os.urandom(16)).upper(), # remove for ABP
  "fCntUp": 10,
  "fCntDown": 11,
  "latitude": 100,
  "longitude": 200,
  "altitude": 300,
  "attributes": {
      "OGNIGC": "True",
  },
  "disableFCntCheck": True,
  "uses32BitFCnt": True,
}
my_device = {
            "appEui": "70B3D57ED0035895",
            "devEui": "00003C71BF60E6A0",
            "appKey": appKey,
            "devAddr": "26014FDF", # remove for OTAA
            "nwkSKey": binascii.b2a_hex(os.urandom(16)).upper(), # remove for OTAA
            "appSKey": binascii.b2a_hex(os.urandom(16)).upper(), # remove for OTAA
            "disableFCntCheck": True,
            "uses32BitFCnt": True,
        }

#
########################################################################
handler     = ttn.HandlerClient    (app_id, appKey)
app_client  = ttn.ApplicationClient(app_id, appKey, handler_address="", cert_content="/home/angel/.ssh/id_ras.pub", discovery_address="discovery.thethings.network:1900")
device      = app_client.device(dev_id)
ld= device.lorawan_device
APP_eui  = binascii.b2a_hex(ld.app_eui).decode('utf-8').upper()
DEV_eui  = binascii.b2a_hex(ld.dev_eui).decode('utf-8').upper()
DEV_addr = binascii.b2a_hex(ld.dev_addr).decode('utf-8').upper()
APP_key  = binascii.b2a_hex(ld.app_key).decode('utf-8').upper()
lastseen = int(ld.last_seen/1000000000)
tme = datetime.datetime.utcfromtimestamp(lastseen)
print (ld.dev_id, ld.app_id, "Aeui:", APP_eui, "Deui:", DEV_eui, "Daddr:", DEV_addr, "Akey:", APP_key, "Last Seen:", tme.strftime("%y-%m-%d %H:%M:%S"))    
print ("DevAppKey:", getdevappkey(app_client))
#devices     = app_client.devices()
#for dd in devices:
    #print ("DDD:", dd)
#app         = app_client.get()
#print ("AAA:", app)
# --------------------------------------------------------- #
#
# using mqtt client
#
# --------------------------------------------------------- #

mqtt_client = handler.data()
mqtt_client.set_uplink_callback(uplink_callback)
#mqtt_client.set_connect_callback(connect_callback)
mqtt_client.connect()
while True:
      try:
         time.sleep(60)
         pass
      except SystemExit:
         print (">>>>: System Exit <<<<<<\n\n")
         mqtt_client.close()
         break
      except KeyboardInterrupt:
         print (">>>>: Keyboard Interupt <<<<<<\n\n")
         mqtt_client.close()
         break
         
print ("Bye: ...: ", counter)
exit(0)
