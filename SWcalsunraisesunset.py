#!/usr/bin/python
from parserfuncs import *
import config
#
# get the sunrise/sunset data
#
lat=config.location_latitude
lon=config.location_longitude
timeepoc=SRSSgetjsondata(lat, lon, prt=True)
print timeepoc
sunsetfile = open (config.DBpath+config.APP+".sunset", 'w') # create a file just to mark that we are alive
sunsetfile.write(str(timeepoc)+"\n") # write the time as control
sunsetfile.close()               # close the alive file
exit(0)
