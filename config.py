#-------------------------------------
# OGN-APRSLOG Spain interface --- Settings
#-------------------------------------
#
#-------------------------------------
# Setting values
#-------------------------------------
#
import socket
import os
from configparser import ConfigParser
from parserfuncs import  getinfoairport  # the ogn/ham parser functions
configdir = os.getenv('CONFIGDIR')
if configdir == None:
    configdir = '/etc/local/'
configfile = configdir+'APRSconfig.ini'
if os.path.isfile(configfile):

    # get the configuration parameters
    cfg=ConfigParser()		# get the configuration parameters
    # reading it for the configuration file
    cfg.read(configfile)		# reading it for the configuration file
else:
    print("Config file: ", configfile, " not found \n")
    exit(-1)
hostname = socket.gethostname()
processid = str(os.getpid())
print("Starting Config...")
APRS_SERVER_HOST = cfg.get('APRS', 'APRS_SERVER_HOST').strip("'").strip('"')
APRS_SERVER_PORT = int(cfg.get('APRS', 'APRS_SERVER_PORT'))
APRS_USER = cfg.get('APRS', 'APRS_USER').strip("'").strip('"')
# See http://www.george-smart.co.uk/wiki/APRS_Callpass
APRS_PASSCODE = int(cfg.get('APRS', 'APRS_PASSCODE'))
APRS_FILTER_DETAILS = cfg.get(
    'APRS', 'APRS_FILTER_DETAILS').strip("'").strip('"')
APRS_FILTER_DETAILS = APRS_FILTER_DETAILS + '\n '
try:
    APRS_SERVER_PUSH = cfg.get('APRS', 'APRS_SERVER_PUSH').strip("'").strip('"')
    APRS_USER_PUSH = cfg.get('APRS', 'APRS_USER_PUSH').strip("'").strip('"')
    # See http://www.george-smart.co.uk/wiki/APRS_Callpass
    APRS_PASSCODE_PUSH = int(cfg.get('APRS', 'APRS_PASSCODE_PUSH'))
except:
    APRS_SERVER_PUSH = ' '

try:
    PUSH2OGNtext = cfg.get('APRS', 'PUSH2OGN').strip("'").strip('"')
except:
    PUSH2OGNtext = "False"

try:
    location_name = cfg.get('location', 'location_name').strip("'").strip('"')
except:
    location_name = ' '
if getinfoairport (location_name) != None:
    #print(getinfoairport (config.location_name))
    location_latitude  = getinfoairport (location_name)['lat']
    location_longitude = getinfoairport (location_name)['lon']
    FLOGGER_LATITUDE   = location_latitude
    FLOGGER_LONGITUDE  = location_longitude
else:
    location_latitude = cfg.get(
        'location', 'location_latitude').strip("'").strip('"')
    location_longitude = cfg.get(
        'location', 'location_longitud').strip("'").strip('"')

    FLOGGER_LATITUDE = cfg.get(
        'location', 'location_latitude').strip("'").strip('"')
    FLOGGER_LONGITUDE = cfg.get(
        'location', 'location_longitud').strip("'").strip('"')

try:
    cucFileLocation = cfg.get('server', 'cucFileLocation').strip("'").strip('"')
except:
    cucFileLocation = "/var/www/html/cuc/"

try:
    DELAY = cfg.get('server', 'DELAY').strip("'").strip('"')
except:
    DELAY = 1200				# default 20 munutes = 1200 seconds

try:
    SPOTtext = cfg.get('location', 'SPOT').strip("'").strip('"')
except:
    SPOTtext = 'False'
try:
    INREACHtext = cfg.get('location', 'INREACH').strip("'").strip('"')
except:
    INREACHtext = 'False'
try:
    CAPTURStext = cfg.get('location', 'CAPTURS').strip("'").strip('"')
    CAPTURSlogin = cfg.get('location', 'CAPTURSlogin').strip("'").strip('"')
    CAPTURSpasswd = cfg.get('location', 'CAPTURSpasswd').strip("'").strip('"')
except:
    CAPTURStext = 'False'
try:
    LT24text = cfg.get('location', 'LT24').strip("'").strip('"')
    LT24username = cfg.get('location', 'LT24username').strip("'").strip('"')
    LT24password = cfg.get('location', 'LT24password').strip("'").strip('"')
    LT24clientid = cfg.get('location', 'LT24clientid').strip("'").strip('"')
    LT24clientid = str(LT24clientid)
    LT24secretkey = cfg.get('location', 'LT24secretkey').strip("'").strip('"')
    LT24secretkey = str(LT24secretkey)
except:
    LT24text = 'False'
try:
    SPIDERtext = cfg.get('location', 'SPIDER').strip("'").strip('"')
    SPIuser = cfg.get('location', 'SPIuser').strip("'").strip('"')
    SPIpassword = cfg.get('location', 'SPIpassword').strip("'").strip('"')
    SPISYSid = cfg.get('location', 'SPISYSid').strip("'").strip('"')
except:
    SPIDERtext = 'False'
try:
    SKYLINEtext = cfg.get('location', 'SKYLINE').strip("'").strip('"')
except:
    SKYLINEtext = 'False'

try:
    OGNTtext = cfg.get('location', 'OGNT').strip("'").strip('"')
except:
    OGNTtext = 'False'

try:
    ADSBtext = cfg.get('location', 'ADSB').strip("'").strip('"')
except:
    ADSBtext = 'False'
try:
    ADSBhost = cfg.get('location', 'ADSBHOST').strip("'").strip('"')
except:
    ADSBhost = 'localhost'
try:
    ADSBfile = cfg.get('location', 'ADSBfile').strip("'").strip('"')
except:
    ADSBfile = '/tmp/aircraft.json'
try:
    ADSBname = cfg.get('location', 'ADSBname').strip("'").strip('"')
except:
    ADSBname = 'ADSBrecvr'
try:
    ADSBloc = cfg.get('location', 'ADSBloc').strip("'").strip('"')
except:
    ADSBloc = ''
try:
    ADSBregt = cfg.get('location', 'ADSBreg').strip("'").strip('"')
except:
    ADSBregt = 'True'
try:
    ADSBOpenSkyT = cfg.get('location', 'ADSBOpenSky').strip("'").strip('"')
except:
    ADSBOpenSkyT = 'False'
try:
    ADSBOpenSkyBox1 = cfg.get('location', 'ADSBOpenSkyBox1').strip("'").strip('"')
except:
    ADSBOpenSkyBox1 = ''
try:
    ADSBOpenSkyBox2 = cfg.get('location', 'ADSBOpenSkyBox2').strip("'").strip('"')
except:
    ADSBOpenSkyBox2 = ''
try:
    ADSBOpenSkyBox3 = cfg.get('location', 'ADSBOpenSkyBox3').strip("'").strip('"')
except:
    ADSBOpenSkyBox3 = ''
try:
    ADSBOpenSkyBox4 = cfg.get('location', 'ADSBOpenSkyBox4').strip("'").strip('"')
except:
    ADSBOpenSkyBox4 = ''
try:
    ADSBOpenSkyName = cfg.get('location', 'ADSBOpenSkyName').strip("'").strip('"')
except:
    ADSBOpenSkyName = ''
try:
    ADSBOpenSkyPswd = cfg.get('location', 'ADSBOpenSkyPswd').strip("'").strip('"')
except:
    ADSBOpenSkyPswd = ''
try:
    ADSBfl = cfg.get('location', 'ADSBfl').strip("'").strip('"')
except:
    ADSBfl = '15000'



try:
    AVXtext = cfg.get('location', 'AVX').strip("'").strip('"')
except:
    AVXtext = 'False'
try:
    AVXhost = cfg.get('location', 'AVXHOST').strip("'").strip('"')
except:
    AVXhost = 'localhost'
try:
    AVXname = cfg.get('location', 'AVXname').strip("'").strip('"')
except:
    AVXname = 'AVXrecvr'
try:
    AVXloc = cfg.get('location', 'AVXloc').strip("'").strip('"')
except:
    AVXloc = ''
try:
    AVXfl = cfg.get('location', 'AVXfl').strip("'").strip('"')
except:
    AVXfl = '15000'

try:
    ENAtext = cfg.get('location', 'ENA').strip("'").strip('"')
except:
    ENAtext = 'False'
try:
    ENAMQTT = cfg.get('location', 'ENAMQTT').strip("'").strip('"')
except:
    ENAMQTT = 'localhost'
try:
    ENATOPIC = cfg.get('location', 'ENATOPIC').strip("'").strip('"')
except:
    ENATOPIC = ''
try:
    ENAUSER = cfg.get('location', 'ENAUSER').strip("'").strip('"')
except:
    ENAUSER = ''
try:
    ENAPASSWD = cfg.get('location', 'ENAPASSWD').strip("'").strip('"')
except:
    ENAPASSWD = ''
try:
    ENAname = cfg.get('location', 'ENAname').strip("'").strip('"')
except:
    ENAname = 'ENArecvr'
try:
    ENAloc = cfg.get('location', 'ENAloc').strip("'").strip('"')
except:
    AVXloc = ''
try:
    ENAfl = cfg.get('location', 'ENAfl').strip("'").strip('"')
except:
    ENAfl = '15000'


try:
    prttext = cfg.get('server', 'prt').strip("'")
    if (prttext == 'False'):
        prt = False
    else:
        prt = True
except:
    prt = True

try:
    DDBhost = cfg.get('server', 'DDBhost').strip("'")
except:
    DDBhost = 'acasado.es'

try:
    DDBport = cfg.get('server', 'DDBport').strip("'")
except:
    DDBport = '60082'

try:
    DDBurl1 = cfg.get('server', 'DDBurl1').strip("'")
except:
    DDBurl1 = 'http://ddb.acasado.name:60082/download/?j=2'

try:
    DDBurl2 = cfg.get('server', 'DDBurl2').strip("'")
except:
    DDBurl2 = 'http://DDB.glidernet.org/download/?j=2'

DBpath = cfg.get('server', 'DBpath').strip("'").strip('"')
MySQLtext = cfg.get('server', 'MySQL').strip("'").strip('"')
DBhost = cfg.get('server', 'DBhost').strip("'").strip('"')
DBuser = cfg.get('server', 'DBuser').strip("'").strip('"')
DBpasswd = cfg.get('server', 'DBpasswd').strip("'").strip('"')
DBuserread = cfg.get('server', 'DBuserread').strip("'").strip('"')
DBpasswdread = cfg.get('server', 'DBpasswdread').strip("'").strip('"')
DBname = cfg.get('server', 'DBname').strip("'").strip('"')
LogDatas = cfg.get('server', 'LogData').strip("'").strip('"')
try:
    PIDfile = cfg.get('server', 'pid').strip("'").strip('"')
except:
    PIDfile = '/tmp/APRS.pid'
try:
    DLYPIDfile = cfg.get('server', 'dlypid').strip("'").strip('"')
except:
    DLYPIDfile = '/tmp/DLY.pid'
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
if (INREACHtext == 'True'):
    INREACH = True
else:
    INREACH = False
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
if (ADSBtext == 'True'):
    ADSB = True
else:
    ADSB = False
if (AVXtext == 'True'):
    AVX = True
else:
    AVX = False
if (ENAtext == 'True'):
    ENA = True
else:
    ENA = False
if (ADSBregt == 'True'):
    ADSBreg = True
else:
    ADSBreg = False
if (ADSBOpenSkyT == 'True'):
    ADSBOpenSky= True
else:
    ADSBOpenSky= False

if (PUSH2OGNtext == 'True'):
    PUSH2OGN = True
else:
    PUSH2OGN = False

# --------------------------------------#
assert len(APRS_USER) > 3 and len(str(APRS_PASSCODE)) > 0, 'Please set APRS_USER and APRS_PASSCODE in settings.py.'

# report the configuration paramenters
LogData = False
APP = "APRSLOG"					# the application name
if 'USER' in os.environ and prt:

    user = os.environ['USER']
    print("Hostname:            ", hostname, " and config file: ", configfile, processid, user)
    print("Config server values:", "MySQL =", MySQL, DBhost, DBuser, DBname, DBpath)
    print("Config APRS values:  ", APRS_SERVER_HOST, APRS_SERVER_PORT, APRS_SERVER_PUSH, PUSH2OGN, APRS_USER, APRS_PASSCODE, APRS_FILTER_DETAILS)
    print("Config location:     ", location_name, FLOGGER_LATITUDE, FLOGGER_LONGITUDE, "\nSPIDER=", SPIDER, "SPOT=", SPOT, "InReach=", INREACH, "CAPTURS=", CAPTURS, "LT24=", LT24, "SKYLINE=", SKYLINE, "\nOGN Tracker pairing=", OGNT, "ADSB=", ADSB, "ADSB Reg=", ADSBreg, "ADSB OpenSky=", ADSBOpenSky, "AVX", AVX, "ENA", ENA)
# --------------------------------------#
APP = 'APRS'					# alternate PUSH2OGN
SOCK = 0
SOCK_FILE = 0
CLIENT = 0
RegWarning = True
