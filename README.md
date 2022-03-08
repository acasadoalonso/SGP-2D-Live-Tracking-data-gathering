# APRSlog

## SGP 2D live tracking - data crawling component

This is the data crawling component for the SGP 2D  live tracking application  
This programs collects the data from the OGN APRS, the SPIDER systems, the SPOT system, the Garmin InReach system, the LiveTrack24 devices (smart phones) and the SKYLINES (XCsoar) devices.

The data is captured and store it on a database, either a SQLITE3 or a MySQL databases.

Programs:

aprslog.py		  	The main data collector, collect the data and store it on the DB

push2ogn.sh		  	The program that collects the positions from the SPOT/SPIDER/INREACH/ ... servers and push it to the OGN APRS servers

config.py		    	The routine that reads the configuration file on /etc/local/APRSconfig.ini and set the configuration parameters

install.sh		  	The script of installation

ognddbfuncs.py			The table with all the flarms ID and its registration ID

adsbfuncs.py			The ADSB parser routine

flarmfuncs.py			The Flarm utility functions

ongtfuncs.py			The OGN tracker data gathering functions

lt24funcs.py			The LiveTrack data gathering functions

capturfuncs.py			The Captur data gathering functions

ogntfuncs.py			The OGN tracker equivalence functions

parserfuncs.py			The parsing functions of the APRS messages

skylfuncs.py			The SKYLINES (XCsoar) data gathering functions

spifuncs.py			The SPIDER data gathering functions

spotfuncs.py			The SPOT data gathering functions

inreachfuncs.py			The InReach data gathering functions

APRScalsunraisesunset.py	The routine to calculate the sunrise and sunset

utils/				Several util function used for testing


install.sh			Is the self installing script
==============================================================================================================0
