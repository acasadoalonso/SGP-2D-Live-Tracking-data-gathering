#
# OGN tracker integration functions
#
# -------------------------------------------------------------------------------------------------------------------------------- #
import kglid

def ogntbuildtable(conn, ognttable, prt=False):	# function to build the OGN tracker table of relation between flarmid and registrations
	auxtable={}
	cursG=conn.cursor()             # set the cursor for searching the devices
	cursG.execute("select id, flarmid, registration from TRKDEVICES where devicetype = 'OGNT' and active = 1; " ) 	# get all the devices with SPIDER
        for rowg in cursG.fetchall(): 	# look for that registration on the OGN database
                                
        	ogntid=rowg[0]		# OGN tracker ID
        	flarmid=rowg[1]		# Flarmid id to be linked
        	registration=rowg[2]	# registration id to be linked
		if flarmid == None or flarmid == '': 			# if flarmid is not provided 
			flarmid=ogntgetflarmid(conn, registration, prt)	# get it from the registration
		else:
			if flarmid[3:9] not in kglid.kglid: # check that the registration is on the table - sanity check
                		print "Warning: flarmid=", flarmid, "not on kglid table"

		ognttable[ogntid]=flarmid
	
		if ogntid[3:]  not in kglid.kglid:	# check that the registration is on the table - sanity checka
			o='NoregO'
		else:
			o=kglid.kglid[ogntid[3:]]
		if flarmid[3:]  not in kglid.kglid:	# check that the registration is on the table - sanity checka
			f='Noregf'
		else:
			f=kglid.kglid[flarmid[3:]]
		auxtable[o]=f
	print "OGNTtable:", ognttable
	print "OGNTtable:", auxtable
	return(ognttable)

# -------------------------------------------------------------------------------------------------------------------------------- #
def ogntgetflarmid(conn, registration, prt=False):

	cursG=conn.cursor()             # set the cursor for searching the devices
	try:
		cursG.execute("select idglider, flarmtype from GLIDERS where registration = '"+registration+"' ;")
       	except MySQLdb.Error, e:
           	try:
                   	print ">>>MySQL Error [%d]: %s" % (e.args[0], e.args[1])
              	except IndexError:
                   	print ">>>MySQL Error: %s" % str(e)
                     	print ">>>MySQL error:", "select idglider, flarmtype from GLIDERS where registration = '"+registration+"' ;"
                    	print ">>>MySQL data :",  registration
		return("NOREG") 
        rowg = cursG.fetchone() 	# look for that registration on the OGN database
	if rowg == None:
		return("NOREG") 
       	idglider=rowg[0]		# flarmid to report
       	flarmtype=rowg[1]		# flarmtype flarm/ica/ogn
	if idglider not in kglid.kglid:	# check that the registration is on the table - sanity check
		print "Warning: flarmid=", idglider, "not on kglid table"
	if flarmtype == 'F':
		flarmid="FLR"+idglider 	# flarm 
	elif flarmtype == 'I':
		flarmid="ICA"+idglider 	# ICA
	elif flarmtype == 'O':
		flarmid="OGN"+idglider 	# ogn tracker
	else: 
		flarmid="RND"+idglider 	# undefined
	if prt:
		print "GGG:", registration, rowg, flarmid
	return (flarmid)

#########################################################################


