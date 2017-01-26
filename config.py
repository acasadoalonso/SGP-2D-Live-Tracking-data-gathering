#-------------------------------------
# OGN-SAR Spain interface --- Settings
#-------------------------------------
#
#-------------------------------------
# Setting values
#-------------------------------------
#
import socket
from configparser import ConfigParser
configfile="/etc/local/APRSconfig.ini"
hostname=socket.gethostname()
print "Hostname:", hostname
cfg=ConfigParser()                                                              # get the configuration parameters
cfg.read(configfile)                                                            # reading it for the configuration file
print "Config.ini sections:", cfg.sections()                                    # report the different sections

APRS_SERVER_HOST        = cfg.get    ('APRS', 'APRS_SERVER_HOST').strip("'").strip('"')
APRS_SERVER_PORT        = int(cfg.get('APRS', 'APRS_SERVER_PORT'))
APRS_USER               = cfg.get    ('APRS', 'APRS_USER').strip("'").strip('"')
APRS_PASSCODE           = int(cfg.get('APRS', 'APRS_PASSCODE'))                 # See http://www.george-smart.co.uk/wiki/APRS_Callpass
APRS_FILTER_DETAILS     = cfg.get    ('APRS', 'APRS_FILTER_DETAILS').strip("'").strip('"')
APRS_FILTER_DETAILS     = APRS_FILTER_DETAILS + '\n '

FLOGGER_LATITUDE        = cfg.get('location', 'location_latitude').strip("'").strip('"')
FLOGGER_LONGITUDE       = cfg.get('location', 'location_longitud').strip("'").strip('"')

DBpath                  = cfg.get('server', 'DBpath').strip("'").strip('"')
MySQLtext               = cfg.get('server', 'MySQL').strip("'").strip('"')
SPIDERtext              = cfg.get('server', 'MySQL').strip("'").strip('"')
SPOTtext                = cfg.get('server', 'MySQL').strip("'").strip('"')
DBhost                  = cfg.get('server', 'DBhost').strip("'").strip('"')
DBuser                  = cfg.get('server', 'DBuser').strip("'").strip('"')
DBpasswd                = cfg.get('server', 'DBpasswd').strip("'").strip('"')
DBname                  = cfg.get('server', 'DBname').strip("'").strip('"')
LogDatas                = cfg.get('server', 'LogData').strip("'").strip('"')
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
# --------------------------------------#
assert len(APRS_USER) > 3 and len(str(APRS_PASSCODE)) > 0, 'Please set APRS_USER and APRS_PASSCODE in settings.py.'
 
LogData=False                                                                               # report the configuration paramenters
print "Config server values:",                  MySQL, DBhost, DBuser, DBpasswd, DBname, DBpath
print "Config APRS values:",                    APRS_SERVER_HOST, APRS_SERVER_PORT, APRS_USER, APRS_PASSCODE, APRS_FILTER_DETAILS
print "Config location :",     			FLOGGER_LATITUDE, FLOGGER_LONGITUDE
# --------------------------------------#

