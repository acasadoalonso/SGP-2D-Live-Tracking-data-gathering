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
print "Hostname:", hostname, " and config file: ", configfile
cfg=ConfigParser()                                                              # get the configuration parameters
cfg.read(configfile)                                                            # reading it for the configuration file
print "Config.ini sections:", cfg.sections()                                    # report the different sections

APRS_SERVER_HOST        = cfg.get    ('APRS', 'APRS_SERVER_HOST').strip("'").strip('"')
APRS_SERVER_PORT        = int(cfg.get('APRS', 'APRS_SERVER_PORT'))
APRS_USER               = cfg.get    ('APRS', 'APRS_USER').strip("'").strip('"')
APRS_PASSCODE           = int(cfg.get('APRS', 'APRS_PASSCODE'))                 # See http://www.george-smart.co.uk/wiki/APRS_Callpass
APRS_FILTER_DETAILS     = cfg.get    ('APRS', 'APRS_FILTER_DETAILS').strip("'").strip('"')
APRS_FILTER_DETAILS     = APRS_FILTER_DETAILS + '\n '
try:
	APRS_SERVER_ALT	= cfg.get    ('APRS', 'APRS_SERVER_ALT').strip("'").strip('"')
	APRS_USER_ALT   = cfg.get    ('APRS', 'APRS_USER_ALT').strip("'").strip('"')
	APRS_PASSCODE_ALT = int(cfg.get('APRS', 'APRS_PASSCODE_ALT'))                 # See http://www.george-smart.co.uk/wiki/APRS_Callpass
except:
	APRS_SERVER_ALT = ' '

try:
	PUSH2OGNtext   	= cfg.get    ('APRS', 'PUSH2OGN').strip("'").strip('"')
except:
	PUSH2OGNtext   	= "False" 

location_latitude       = cfg.get('location', 'location_latitude').strip("'").strip('"')
location_longitude      = cfg.get('location', 'location_longitud').strip("'").strip('"')

FLOGGER_LATITUDE        = cfg.get('location', 'location_latitude').strip("'").strip('"')
FLOGGER_LONGITUDE       = cfg.get('location', 'location_longitud').strip("'").strip('"')

try:
        cucFileLocation = cfg.get('server', 'cucFileLocation').strip("'").strip('"')
except:
        cucFileLocation = "/var/www/html/cuc/"

try:
	location_name   = cfg.get('location', 'location_name').strip("'").strip('"')
except:
	location_name   = ' '
try:
	SPOTtext        = cfg.get('location', 'SPOT').strip("'").strip('"')
except:
	SPOTtext='False'
try:
	CAPTURStext     = cfg.get('location', 'CAPTURS').strip("'").strip('"')
	CAPTURSlogin    = cfg.get('location', 'CAPTURSlogin').strip("'").strip('"')
	CAPTURSpasswd   = cfg.get('location', 'CAPTURSpasswd').strip("'").strip('"')
except:
	CAPTURStext='False'
try:
	LT24text        = cfg.get('location', 'LT24').strip("'").strip('"')
	LT24username    = cfg.get('location', 'LT24username').strip("'").strip('"')
	LT24password    = cfg.get('location', 'LT24password').strip("'").strip('"')
	LT24clientid    = cfg.get('location', 'LT24clientid').strip("'").strip('"')
	LT24clientid    = str(LT24clientid)
	LT24secretkey   = cfg.get('location', 'LT24secretkey').strip("'").strip('"')
	LT24secretkey   = str(LT24secretkey)
except:
	LT24text='False'
try:
	SPIDERtext      = cfg.get('location', 'SPIDER').strip("'").strip('"')
	SPIuser         = cfg.get('location', 'SPIuser').strip("'").strip('"')
	SPIpassword     = cfg.get('location', 'SPIpassword').strip("'").strip('"')
	SPISYSid        = cfg.get('location', 'SPISYSid').strip("'").strip('"')
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
DBuserread              = cfg.get('server', 'DBuserread').strip("'").strip('"')
DBpasswdread            = cfg.get('server', 'DBpasswdread').strip("'").strip('"')
DBname                  = cfg.get('server', 'DBname').strip("'").strip('"')
LogDatas                = cfg.get('server', 'LogData').strip("'").strip('"')
try:
	PIDfile         = cfg.get('server', 'pid').strip("'").strip('"')
except:
	PIDfile='/tmp/APRS.pid'
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
if (CAPTURStext == 'True'):
        CAPTURS = True
else:
        CAPTURS = False
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
if (PUSH2OGNtext == 'True'):
        PUSH2OGN = True
else:
        PUSH2OGN = False

# --------------------------------------#
assert len(APRS_USER) > 3 and len(str(APRS_PASSCODE)) > 0, 'Please set APRS_USER and APRS_PASSCODE in settings.py.'
 
LogData=False                                   # report the configuration paramenters
APP="APRSLOG"					# the application name
print "Config server values:",                  "MySQL=", MySQL, DBhost, DBuser, DBname, DBpath
print "Config APRS values:",                    APRS_SERVER_HOST, APRS_SERVER_PORT, APRS_SERVER_ALT, PUSH2OGN, APRS_USER, APRS_PASSCODE, APRS_FILTER_DETAILS
print "Config location :",     			location_name, FLOGGER_LATITUDE, FLOGGER_LONGITUDE, "SPIDER=", SPIDER, "SPOT=", SPOT, "CAPTURS=", CAPTURS, "LT24=", LT24, "SKYLINE=", SKYLINE, "OGNT=", OGNT
# --------------------------------------#
APP='APRS'					# alternate PUSH2OGN
SOCK=0
SOCK_FILE=0
RegWarning=True
