#!/usr/bin/python3
#
# OGN tracker integration functions
#
# -------------------------------------------------------------------------------------------------------------------------------- #
from flarmfuncs import getflarmid, chkflarmid
from ognddbfuncs import getognreg

#
# function to build the OGN tracker table of relation between flarmid and registrations
#


def ogntbuildtable(conn, ognttable, prt=False):  # conn is the DB connection id, ogntable is where to return the pairs table

    oldtable = ognttable.copy()         # have a copy of it
    auxtable = {}			# the aux table to know the registrations
    cursG = conn.cursor()               # set the cursor for searching the devices
    # get all the devices with OGN tracker
    cursG.execute("select id, flarmid, registration from TRKDEVICES where devicetype = 'OGNT' and active = 1; ")
    for rowg in cursG.fetchall(): 	# look for that registration on the OGN database

        ogntid = rowg[0].upper()	# OGN tracker ID
        flarmid = rowg[1].upper()	# Flarmid id to be linked
        registration = rowg[2]          # registration id to be linked
        if prt:
            print("OGNTtable:", ogntid, flarmid, registration)
        if flarmid == None or flarmid == '':  # if flarmid is not provided
            # get it from the registration
            flarmid = getflarmid(conn, registration)
        else:
            chkflarmid(flarmid)

        ognttable[ogntid] = flarmid

        # check that the registration is on the table - sanity check
        o=getognreg(ogntid)
        if o == "NOreg":
            o = 'NoregO'
        # check that the registration is on the table - sanity checka
        f=getognreg(flarmid)
        if f == "NOreg":
            f = 'NoregF'
        auxtable[o] = f

    unmatched_item = set(oldtable.items()) ^ set(ognttable.items())
    if len(unmatched_item) != 0 and prt:
        print("OGNTtable:", ognttable)
        print("OGNTtable:", auxtable)
    return(ognttable)

# -------------------------------------------------------------------------------------------------------------------------------- #

#########################################################################
