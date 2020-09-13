#!/usr/bin/python3
import json
import requests
import urllib.request, urllib.error, urllib.parse
global _ogninfo_                            # the OGN info data
_ogninfo_ = {}                              # the OGN info data
####################################################################


def getddbdata():                           # get the data from the API server

    global _ogninfo_                        # the OGN info data
    url = "http://ddb.glidernet.org/download/?j=1"  # the OGN DDB source
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/json")  # it return a JSON string
    req.add_header("Content-Type", "application/hal+json")
    r = urllib.request.urlopen(req)         # open the url resource
    js=r.read().decode('UTF-8')
    j_obj = json.loads(js)                  # convert to JSON

    _ogninfo_ = j_obj                       # save the data on the global storage
    return j_obj                            # return the JSON objecta

def getogninfo(devid):			    # return the OGN DDB infor for this device

    global _ogninfo_   		            # the OGN info data
    if len(_ogninfo_) == 0:
            _ogninfo_=getddbdata()
    devices=_ogninfo_["devices"]            # access to the ddbdata
    for dev in devices:                     # loop into the registrations
            if dev["device_id"] == devid:   # if matches ??
                return dev  		    # return the information
    return "NOInfo "                        #if not found !!!


def getognreg(devid):                       # get the ogn registration from the flarmID

    global _ogninfo_                        # the OGN info data
    if len(_ogninfo_) == 0:
            _ogninfo_=getddbdata()
    devices=_ogninfo_["devices"]            # access to the ddbdata
    for dev in devices:                     # loop into the registrations
            if dev["device_id"] == devid:   # if matches ??
                return dev["registration"]  # return the registration
    return "NOReg  "                        #if not found !!!


def getognchk(devid):                       # Check if the FlarmID exist or NOT

    global _ogninfo_                        # the OGN info data
    if len(_ogninfo_) == 0:
        _ogninfo_ = getddbdata()            # get the table from OGN DDB
    devices = _ogninfo_["devices"]          # access to the ddbdata
    for dev in devices:                     # loop into the devices
        if dev["device_id"] == devid:       # if matches ??
            return True

    return False


def getognflarmid(registration):            # get the FlarmID based on the registration

    global _ogninfo_                        # the OGN info data
    if len(_ogninfo_) == 0:
        _ogninfo_ = getddbdata()
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
                dvce = "UNK"+dev['device_id']

            return dvce                     # return the flarmID

    return "NOFlarm"                        # if not found !!!


def getogncn(devid):                        # get the ogn competition ID from the flarmID

    global _ogninfo_                        # the OGN info data
    if len(_ogninfo_) == 0:
        _ogninfo_ = getddbdata()
    devices = _ogninfo_["devices"]          # access to the ddbdata
    for dev in devices:                     # loop into the compet
        if dev["device_id"] == devid:       # if matches ??
            return dev["cn"]                # return the competitionID

    return "NID"                            # if not found !!!

def getognmodel(devid):                     # get the ogn aircraft model from the flarmID

    global _ogninfo_                        # the OGN info data
    if len(_ogninfo_) == 0:
        _ogninfo_ = getddbdata()
    devices = _ogninfo_["devices"]          # access to the ddbdata
    for dev in devices:                     # loop into the registrations
        if dev["device_id"] == devid:       # if matches ??
            return dev["aircraft_model"]    #return the aircraft model

    return "NoModel"                        # if not found !!!

###################################################################

DDB_URL = "http://ddb.glidernet.org/download/?j=1"


def get_ddb_devices():
    r = requests.get(DDB_URL)
    for device in r.json()['devices']:
        device.update({'identified': device['identified'] == 'Y',
                       'tracked': device['tracked'] == 'Y'})
        yield device

