#!/usr/bin/python3
import MySQLdb
from ognddbfuncs import getognchk
unkglider = []
def getflarmid(conn, registration):  # get the FLARMID from the GLIDERS table on the database

    cursG = conn.cursor()           # set the cursor for searching the devices
    try:
        cursG.execute("select idglider, flarmtype from GLIDERS where registration = '"+registration+"' ;")
    except MySQLdb.Error as e:
        try:
            print(">>>MySQL Error [%d]: %s" % (e.args[0], e.args[1]))
        except IndexError:
            print(">>>MySQL Error: %s" % str(e))
            print(">>>MySQL error:", "select idglider, flarmtype from GLIDERS where registration = '"+registration+"' ;")
            print(">>>MySQL data :", registration)
        return("NOREG")
    rowg = cursG.fetchone() 	    # look for that registration on the OGN database
    if rowg is None:
        return("NOREG")
    idglider = rowg[0]		    # flarmid to report
    flarmtype = rowg[1]		    # flarmtype flarm/ica/ogn
    if not getognchk(idglider):     # check that the registration is on the table - sanity check
        if idglider not in unkglider:	# we do not want to repeat the warning many times
            print("Warning: FLARM ID=", idglider, "not on OGN DDB. But on GLIDERS table as:", registration)
            unkglider.append(idglider)	# add it to the list
    if flarmtype == 'F':
        flarmid = "FLR"+idglider    # flarm
    elif flarmtype == 'I':
        flarmid = "ICA"+idglider    # ICA
    elif flarmtype == 'O':
        flarmid = "OGN"+idglider    # ogn tracker
    else:
        flarmid = "RND"+idglider    # undefined
    #print "GGG:", registration, rowg, flarmid
    return (flarmid)
# -----------------------------------------------------------


def chkflarmid(idglider):           # check if the FLARM ID exist, if not add it to the unkglider table
    if len(idglider) == 9:
       glider = idglider[3:9]       # only the last 6 chars of the ID
    elif len(idglider) == 6:
       glider = idglider[0:6]       # only the last 6 chars of the ID
    else:
       return (False)
       

    if not getognchk(glider):       # check that the registration is on the table - sanity check
        if idglider not in unkglider:
            print("Warning: FLARM ID=", idglider, "not on OGN DDB...")
            unkglider.append(idglider)
            return (False)
        return(False)
    return (True)
# -----------------------------------------------------------
