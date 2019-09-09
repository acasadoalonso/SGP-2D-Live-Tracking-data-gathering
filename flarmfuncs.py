#!/usr/bin/python3
import kglid

unkglider = []


def getflarmid(conn, registration):

    cursG = conn.cursor()             # set the cursor for searching the devices
    try:
        cursG.execute(
            "select idglider, flarmtype from GLIDERS where registration = '"+registration+"' ;")
    except MySQLdb.Error as e:
        try:
            print(">>>MySQL Error [%d]: %s" % (e.args[0], e.args[1]))
        except IndexError:
            print(">>>MySQL Error: %s" % str(e))
            print(">>>MySQL error:", "select idglider, flarmtype from GLIDERS where registration = '"+registration+"' ;")
            print(">>>MySQL data :",  registration)
        return("NOREG")
    rowg = cursG.fetchone() 	    # look for that registration on the OGN database
    if rowg == None:
        return("NOREG")
    idglider = rowg[0]		    # flarmid to report
    flarmtype = rowg[1]		    # flarmtype flarm/ica/ogn
    if idglider not in kglid.kglid: # check that the registration is on the table - sanity check
        if idglider not in unkglider:
            print("Warning: flarmid=", idglider, "not on kglid table")
            unkglider.append(idglider)
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


def chkflarmid(idglider):
    glider = idglider[3:9]
    if glider not in kglid.kglid:   # check that the registration is on the table - sanity check
        if idglider not in unkglider:
            print("Warning: flarmid=", idglider, "not on kglid table")
            unkglider.append(idglider)
            return (False)
    return (True)
# -----------------------------------------------------------
