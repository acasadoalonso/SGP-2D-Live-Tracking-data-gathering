#-------------------------------------
# OGN-SAR Spain interface --- Settings
#-------------------------------------
#
#-------------------------------------
# Setting values
#-------------------------------------
#
import socket
import os
from configparser import ConfigParser
configdir=os.getenv('CONFIGDIR')
if configdir == None:
	configdir='/etc/local/'
configfile=configdir+'APRSconfig.ini'
hostname=socket.gethostname()
print "Hostname:", hostname
cfg=ConfigParser()                                                              # get the configuration parameters
cfg.read(configfile)                                                            # reading it for the configuration file
print "Config file used : ",  configfile
print "Config.ini sections:", cfg.sections()                                    # report the different sections

APRS_SERVER_HOST        = cfg.get    ('APRS', 'APRS_SERVER_HOST').strip("'").strip('"')
APRS_SERVER_PORT        = int(cfg.get('APRS', 'APRS_SERVER_PORT'))
APRS_USER               = cfg.get    ('APRS', 'APRS_USER').strip("'").strip('"')
APRS_PASSCODE           = int(cfg.get('APRS', 'APRS_PASSCODE'))                 # See http://www.george-smart.co.uk/wiki/APRS_Callpass
APRS_FILTER_DETAILS     = cfg.get    ('APRS', 'APRS_FILTER_DETAILS').strip("'").strip('"')
APRS_FILTER_DETAILS     = APRS_FILTER_DETAILS + '\n '

FLOGGER_LATITUDE        = cfg.get('location', 'location_latitude').strip("'").strip('"')
FLOGGER_LONGITUDE       = cfg.get('location', 'location_longitud').strip("'").strip('"')
try:
	location_name   = cfg.get('location', 'location_name').strip("'").strip('"')
except:
	location_name   = ' '
try:
	SPOTtext        = cfg.get('location', 'SPOT').strip("'").strip('"')
except:
	SPOTtext='False'
try:
	LT24text        = cfg.get('location', 'LT24').strip("'").strip('"')
	LT24username    = cfg.get('location', 'LT24username').strip("'").strip('"')
	LT24password    = cfg.get('location', 'LT24password').strip("'").strip('"')
except:
	LT24text='False'
try:
	SPIDERtext      = cfg.get('location', 'SPIDER').strip("'").strip('"')
	SPIuser         = cfg.get('location', 'SPIuser').strip("'").strip('"')
	SPIpassword     = cfg.get('location', 'SPIpassword').strip("'").strip('"')
except:
	SPIDERtext='False'
try:
	SKYLINEtext     = cfg.get('location', 'SKYLINE').strip("'").strip('"')
except:
	SKYLINEtext='False'

try:
	OGNTtext     = cfg.get('location', 'OGNT').strip("'").strip('"')
except:
	OGNTtext='False'


DBpath                  = cfg.get('server', 'DBpath').strip("'").strip('"')
MySQLtext               = cfg.get('server', 'MySQL').strip("'").strip('"')
DBhost                  = cfg.get('server', 'DBhost').strip("'").strip('"')
DBuser                  = cfg.get('server', 'DBuser').strip("'").strip('"')
DBpasswd                = cfg.get('server', 'DBpasswd').strip("'").strip('"')
DBname                  = cfg.get('server', 'DBname').strip("'").strip('"')
LogDatas                = cfg.get('server', 'LogData').strip("'").strip('"')
# --------------------------------------#
if (MySQLtext == 'True'):
        MySQL = True
else:
        MySQL = False
if (LogDatas == 'True'):
        LogData = True
else:
        LogData = False
if (SPIDERtext == 'True'):
        SPIDER = True
else:
        SPIDER = False
if (SPOTtext == 'True'):
        SPOT = True
else:
        SPOT = False
if (LT24text == 'True'):
        LT24 = True
else:
        LT24 = False
if (SKYLINEtext == 'True'):
        SKYLINE = True
else:
        SKYLINE = False
if (OGNTtext == 'True'):
        OGNT = True
else:
        OGNT = False

# --------------------------------------#
assert len(APRS_USER) > 3 and len(str(APRS_PASSCODE)) > 0, 'Please set APRS_USER and APRS_PASSCODE in settings.py.'
 
LogData=False                                   # report the configuration paramenters
APP="APRSLOG"					# the application name
print "Config server values:",                  "MySQL=", MySQL, DBhost, DBuser, DBpasswd, DBname, DBpath
print "Config APRS values:",                    APRS_SERVER_HOST, APRS_SERVER_PORT, APRS_USER, APRS_PASSCODE, APRS_FILTER_DETAILS
print "Config location :",     			location_name, FLOGGER_LATITUDE, FLOGGER_LONGITUDE, "SPIDER=", SPIDER, "SPOT=", SPOT, "LT24=", LT24, "SKYLINE=", SKYLINE, "OGNT=", OGNT
# --------------------------------------#
APP='APRS'
RegWarning=True
