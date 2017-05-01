# APRSlog

## SGP 2D live tracking - data crawling component

This is the data crawling component for the SGP 2D  live tracking application  
This programs collects the data fro the OGN APRS, the SPIDER systems, the SPOT system, the LiveTrack24 devices (smart phones) and the SKYLINES (XCsoar) devices.

The data is captured and store it on a database, either a SQLITE3 or a MySQL databases.

Programs:

aprslog.py		The main data collector
config.py		The routine that reads the configuration file on /etc/local/APRSconfig.ini and set the configuration parameters
install.sh		The script of installation
kglid.py		The table with all the flarms ID and its registration ID
libfap.py		The APRS parser routine
lt24funcs.py		The LiveTrack data gathering functions
ogntfuncs.py		The OGN tracker equivalence functions
parserfuncs.py		The parsing functions of the APRS messages
skylfuncs.py		The SKYLINES (XCsoar) data gathering functions
spifuncs.py		The SPIDER data gathering functions
spotfuncs.py		The SPOT data gathering functions
UTILS/			Several util function used for testing
