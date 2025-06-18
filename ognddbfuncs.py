#!/usr/bin/python3
import json
import socket
import urllib.request
import urllib.error
import urllib.parse
from urllib.error import HTTPError
import requests
import config
from ping3 import ping
from time import sleep                      # the sleep

global _ogninfo_                            # the OGN info data
_ogninfo_ = {}                              # the OGN info data
NOinfo = {"return": "NOinfo"}
####################################################################

HOST		=config.DDBhost		    # OGN DDB host name to try first
PORT		=config.DDBport		    # port to try
DDB_URL1 	=config.DDBurl1		    # url of where to get initially the DDB data
DDB_URL2 	=config.DDBurl2		    # second choice
                                            #url = "http://ddb.glidernet.org/download/?j=2"  # the OGN DDB source
prt		=config.prt

####################################################################

def findfastestaprs():				# find the fastest APRS server

   aprs=["glidern1.glidernet.org",		# list of aprs.glidernet.org server 
         "glidern2.glidernet.org",
         "glidern3.glidernet.org",
         "glidern4.glidernet.org",
         "glidern5.glidernet.org"]
   p=999					# start with a high value
   url=''
   for u in aprs:				# got thru all the servers
       try:
          pp=ping(u)				# ping the server
       except:
          return (u)
       if pp < p:				# if faster ?
          p=pp					# remember the ping time
          url=u					# remember the URL
   return(url)					# return the URL of the fastest server 
####################################################################

def servertest(host, port):

    args = socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM)
    for family, socktype, proto, canonname, sockaddr in args:
        s = socket.socket(family, socktype, proto)
        try:
            s.connect(sockaddr)
        except socket.error:
            return False
        else:
            s.close()
            return True

####################################################################

def getddbdata(prt=False):                  		# get the data from the API server

    j_obj=''					# empty as default
    global _ogninfo_                        	# the OGN info data
    if servertest(HOST, PORT):
        DDB_URL=DDB_URL1
    else:
        DDB_URL=DDB_URL2
    #if prt:
    if True:
       print("Trying DDB Connecting with: ", DDB_URL, HOST, PORT)
       #print("PING time: ",           ping(HOST))
    req = urllib.request.Request(url="http://DDB.glidernet.org/download/?j=1")
    req.add_header("Accept", "application/json")  # it return a JSON string
    req.add_header("Content-Type", "application/json")
    req.add_header("Request-Timeout", "60")
    req.add_header('User-Agent', 'Mozilla/5.0')
       #req = urllib.request.Request(url=DDB_URL)
    print ("RRR")
    f = urllib.request.urlopen(req)
    print ("RRR2")
    try:
       js=f.read().decode('utf-8')
       print ("RRR3")

       f.close()
       print ("RRR4")
       #r = urllib.request.urlopen(req)      # open the url resource
       #js=r.read().decode('UTF-8')
       print ("RRR", js)
       j_obj = json.loads(js)               # convert to JSON

       _ogninfo_ = j_obj                    # save the data on the global storage
       print ("DDB loaded... Size:", len (j_obj))
    except HTTPError as err:
       if err.code == 429:
          print("Error DDB Connecting with: ", DDB_URL, HOST, PORT, " too many request ... \n")
          sleep(10)
    except:
       print("DDB Connecting with: ", DDB_URL, HOST, PORT, " failed ... \n")
       j_obj=''
    print ("Size of DDB:", len(j_obj))
    return j_obj                            # return the JSON object

####################################################################

def getogninfo(devid):			    # return the OGN DDB infor for this device

    global _ogninfo_   		            # the OGN info data
    if len(_ogninfo_) == 0:
        _ogninfo_=getddbdata(prt)
        if len(_ogninfo_) == 0:
           return "NOInfo"  			    # if not found !!!
    devices=_ogninfo_["devices"]            # access to the ddbdata
    for dev in devices:                     # loop into the registrations
        if dev["device_id"] == devid:       # if matches ??
            return dev  		    # return the information
    return "NOInfo"  			    # if not found !!!


####################################################################
def getognreg(devid):                       # get the ogn registration from the flarmID

    global _ogninfo_                        # the OGN info data
    if len(_ogninfo_) == 0:
        _ogninfo_=getddbdata()
        if len(_ogninfo_) == 0:
           return "NOInfo"  			    # if not found !!!
    devices=_ogninfo_["devices"]            # access to the ddbdata
    for dev in devices:                     # loop into the registrations
        if dev["device_id"] == devid:   # if matches ??
            return dev["registration"]  # return the registration
    return "NOReg  "  # if not found !!!

####################################################################

def getognchk(devid):                       # Check if the FlarmID exist or NOT

    global _ogninfo_                        # the OGN info data
    if len(_ogninfo_) == 0:
        _ogninfo_ = getddbdata()            # get the table from OGN DDB
        if len(_ogninfo_) == 0:
           return False
    devices = _ogninfo_["devices"]          # access to the ddbdata
    for dev in devices:                     # loop into the devices
        if dev["device_id"] == devid:       # if matches ??
            return True

    return False

####################################################################

def getognflarmid(registration):            # get the FlarmID based on the registration

    global _ogninfo_                        # the OGN info data
    if len(_ogninfo_) == 0:
        _ogninfo_ = getddbdata()
        if len(_ogninfo_) == 0:
           return "NOInfo"  			    # if not found !!!
    devices = _ogninfo_["devices"]          # access to the ddbdata
    for dev in devices:                     # loop into the registrations
        if dev["registration"] == registration:  # if matches ??
            if dev['device_type'] == "F":
                dvce = "FLR"+dev['device_id']
            elif dev['device_type'] == "I":
                dvce = "ICA"+dev['device_id']
            elif dev['device_type'] == "O":
                dvce = "OGN"+dev['device_id']
            else:
                continue	            # Registrion found, but is not a Flarm/tracker
            return dvce                     # return the flarmID

    return "NOFlarm"                        # if not found !!!

####################################################################

def getogncn(devid):                        # get the ogn competition ID from the flarmID

    global _ogninfo_                        # the OGN info data
    if len(_ogninfo_) == 0:
        _ogninfo_ = getddbdata()
        if len(_ogninfo_) == 0:
           return "NOInfo"  			    # if not found !!!
    devices = _ogninfo_["devices"]          # access to the ddbdata
    for dev in devices:                     # loop into the compet
        if dev["device_id"] == devid:       # if matches ??
            return dev["cn"]                # return the competitionID

    return "NID"                            # if not found !!!

####################################################################

def getognmodel(devid):                     # get the ogn aircraft model from the flarmID

    global _ogninfo_                        # the OGN info data
    if len(_ogninfo_) == 0:
        _ogninfo_ = getddbdata()
        if len(_ogninfo_) == 0:
           return "NOInfo"  			    # if not found !!!
    devices = _ogninfo_["devices"]          # access to the ddbdata
    for dev in devices:                     # loop into the registrations
        if dev["device_id"] == devid:       # if matches ??
            return dev["aircraft_model"]  # return the aircraft model

    return "NoModel"                        # if not found !!!

###################################################################


def get_ddb_devices():
    if servertest(HOST, PORT):
        DDB_URL=DDB_URL1
    else:
        DDB_URL=DDB_URL2
    r = requests.get(DDB_URL, allow_redirects=False)
    for device in r.json()['devices']:
        device.update({'identified': device['identified'] == 'Y',
                       'tracked': device['tracked'] == 'Y'})
        yield device

####################################################################

def get_by_dvt(devdvt, dvt):
    global _ogninfo_                        # the OGN info dataa
    cnt = 0
    if len(_ogninfo_) == 0:
        _ogninfo_ = getddbdata()
        if len(_ogninfo_) == 0:
           return (cnt)
    devices = _ogninfo_["devices"]          # access to the ddbdata
    for device in devices:
        if device['device_type'] == dvt:
            devdvt.append(device)
            cnt += 1
    return (cnt)
####################################################################
