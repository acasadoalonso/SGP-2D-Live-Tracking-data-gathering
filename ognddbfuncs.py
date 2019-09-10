#!/usr/bin/python3
import json
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
    j_obj = json.load(r)                    # convert to JSONa
    _ogninfo_ = j_obj                       # save the data on the global storage
    return j_obj                            # return the JSON objecta

def getognreg(flarmid ):                    # get the ogn registration from the flarmID

        global _ogninfo_                    # the OGN info data
        if len(_ogninfo_) == 0:
            _ogninfo_=getddbdata()
        devices=_ogninfo_["devices"]        # access to the ddbdata
        for dev in devices:                 # loop into the registrations
            if dev["device_id"] == flarmid:  # if matches ??
                return dev["registration"]  # return the registration

        return "NOREG  "                    #if not found !!!


def getognchk(flarmid):                     # Check if the FlarmID exist or NOT

    global _ogninfo_                        # the OGN info data
    if len(_ogninfo_) == 0:
        _ogninfo_ = getddbdata()            # get the table from OGN DDB
    devices = _ogninfo_["devices"]          # access to the ddbdata
    for dev in devices:                     # loop into the registrations
        if dev["device_id"] == flarmid:     # if matches ??
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

    return "NOREG  "                        # if not found !!!


def getogncn(flarmid):                      # get the ogn competition ID from the flarmID

    global _ogninfo_                        # the OGN info data
    if len(_ogninfo_) == 0:
        _ogninfo_ = getddbdata()
    devices = _ogninfo_["devices"]          # access to the ddbdata
    for dev in devices:                     # loop into the registrations
        if dev["device_id"] == flarmid:     # if matches ??
            return dev["cn"]                # return the registration

    return "NOC"                            # if not found !!!

###################################################################
