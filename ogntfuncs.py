#!/usr/bin/python3
#
# OGN tracker integration functions
#
# -------------------------------------------------------------------------------------------------------------------------------- #
import kglid
from flarmfuncs import *


# function to build the OGN tracker table of relation between flarmid and registrations
def ogntbuildtable(conn, ognttable, prt=False):
    oldtable = ognttable.copy()         # have a copy of it
    auxtable = {}			# the aux table to know the registrations
    cursG = conn.cursor()               # set the cursor for searching the devices
                                        # get all the devices with OGN tracker
    cursG.execute("select id, flarmid, registration from TRKDEVICES where devicetype = 'OGNT' and active = 1; ")
    for rowg in cursG.fetchall(): 	# look for that registration on the OGN database

        ogntid = rowg[0]		# OGN tracker ID
        flarmid = rowg[1]		# Flarmid id to be linked
        registration = rowg[2]          # registration id to be linked
        if prt:
            print("OGNTtable:", ogntid, flarmid, registration)
        if flarmid == None or flarmid == '': # if flarmid is not provided
                                        # get it from the registration
            flarmid = getflarmid(conn, registration)
        else:
            found=chkflarmid(flarmid)

        ognttable[ogntid] = flarmid

        # check that the registration is on the table - sanity checka
        if ogntid[3:] not in kglid.kglid:
            o = 'NoregO'
        else:
            o = kglid.kglid[ogntid[3:]]
        # check that the registration is on the table - sanity checka
        if flarmid[3:] not in kglid.kglid:
            f = 'NoregF'
        else:
            f = kglid.kglid[flarmid[3:]]
        auxtable[o] = f

    unmatched_item = set(oldtable.items()) ^ set(ognttable.items())
    if len(unmatched_item) != 0 and prt:
        print("OGNTtable:", ognttable)
        print("OGNTtable:", auxtable)
    return(ognttable)

# -------------------------------------------------------------------------------------------------------------------------------- #

#########################################################################
