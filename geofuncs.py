#!/usr/bin/python3
# Geo routines
#coding:UTF-8
import math
import sys
import geopy
from geopy.distance import geodesic     # use the Vincenty algorithm^M

from math import radians, cos, sin, asin, sqrt, atan2, degrees

##########################################################################
def decdeg2dms(dd):              # convert degrees to D, M, S
    
    negative = dd < 0
    dd = abs(dd)
    minutes,seconds = divmod(dd*3600,60)
    degrees,minutes = divmod(minutes,60)
    if negative:
        if degrees > 0:
            degrees = -degrees
        elif minutes > 0:
            minutes = -minutes
        else:
            seconds = -seconds
    return (degrees,minutes,seconds)

def decdeg2DDMMmmm(dd):         # convert degrees to D, M, DM
    
    negative = dd < 0
    dd = abs(dd)
    
    """decimal degrees to deg dec min"""
    deg = int(dd)
    minsec = (dd - deg)*60.0
    
    minutes=float(int(minsec))
    
    mindec=(minsec-minutes)*1000.0
    
    if negative:
        if deg > 0:
            deg = -deg
    return (float(deg),minutes,mindec)

def dms2decdeg(g, m, s):        # convert DDMMSS to degrees
    
    return (float(g)+float(m)/60.0+float(s)/3600.0)

def DDMMmmm2decdeg(g, m, dm):   # convert DDMMmmm to degrees
    
    return (float(g)+(float(m)+float(dm)/1000.0)/60.0)

def tolatDMS(dd):               # convert degrees to string DDMMSS
    
        x=decdeg2dms(dd)
        if dd > 0:
            fmt="%02d%02d%02d0N"
        else:
            fmt="%02d%02d%02d0S"
        return (fmt%x)
    
def tolatDDMMmmm(dd):           # convert degrees to string DDMMmmm
    
        x=decdeg2DDMMmmm(dd)
        if dd > 0:
            fmt="%02d%02d%03dN"
        else:
            fmt="%02d%02d%03dS"
        return (fmt%x)
    
def tolonDMS(dd):               # convert degrees to string DDDMMSS
    
        x=decdeg2dms(dd)
        if dd > 0:
            fmt="%03d%02d%02d0E"
        else:
            fmt="%03d%02d%02d0W"
        return (fmt%x)

def tolonDDMMmmm(dd):           # convert degrees to DDDMMmmm 
    
        x=decdeg2DDMMmmm(dd)
        if dd > 0:
            fmt="%03d%02d%03dE"
        else:
            fmt="%03d%02d%03dW"
        return (fmt%x)

def DMS2lat(lat):               # convert string DDMMSS to degrees
    
        l=dms2decdeg(int(lat[0:2]), int(lat[2:4]), int(lat[4:6]))
        if lat[6:7] == 'N':
            return l
        if lat[6:7] == 'S':
            return -l
        else:
            return 0
            
def DDMMmmm2lat(lat):           # convert string DDMMmmm to degrees
        if lat[0:7].isnumeric():
           l=DDMMmmm2decdeg(int(lat[0:2]), int(lat[2:4]), int(lat[4:7]))
        else:
           print ("LAT:", lat, file=sys.stderr)
           l=0
        if lat[7:8] == 'N':
            return l
        if lat[7:8] == 'S':
            return -l
        else:
            return 0 

def DMS2lon(lon):               # convert string DDDMMSS to degrees
    
        l=dms2decdeg(int(lon[0:3]), int(lon[3:5]), int(lon[5:7]))
        if lon[7:8] == 'E':
            return l
        if lon[7:8] == 'W':
            return -l
        else:
            return 0
def DDMMmmm2lon(lon):           # convert string DDDMMmmm to degrees
    
        if lon[0:8].isnumeric():
           l=DDMMmmm2decdeg(int(lon[0:3]), int(lon[3:5]), int(lon[5:8]))
        else:
           print ("LON", lon, file=sys.stderr)
           l=0
        if lon[8:9] == 'E':
            return l
        if lon[8:9] == 'W':
            return -l
        else:
            return 0

##########################################################################
# add the NED North, East, Down to a current position
def getnewpos(lat, lon, alt, N, E, D):
# Define starting point.
    start = geopy.Point(lat, lon, alt)

# Define a general distance object, initialized with a distance of 1 km.
    dN = geopy.distance.geodesic(kilometers = N/1000.0) # get the distance as a point
    dE = geopy.distance.geodesic(kilometers = E/1000.0)

# Use the `destination` method with a bearing of 0 degrees (which is north)
# in order to go from point `start` 1 km to north.
    d1=dN.destination(point=start, bearing=0)           # go North
    d2=dE.destination(point=d1, bearing=90)             # go Easta
    #print "\n", d1, "\n", d2
    return (d2)                                         # return the result

def getnewcoor(lat, lon, alt, N, E, D):                 # get new coordenates DMS adding NED
    p=getnewpos(lat, lon, alt, N, E, D)                 # get the new position
    lat=tolatDDMMmmm(p.latitude)                        # the new latitude DMS
    lon=tolonDDMMmmm(p.longitude)                       # the new longitude DMS 
    return (lat, lon, alt-D)

def getnewDDMMmmm(lat, lon, alt, N, E, D):              # get the new DMS from DMS adding NED
    lt=DDMMmmm2lat(lat)                                 # convert to decimal degree
    ln=DDMMmmm2lon(lon)                                 #
    return(getnewcoor(lt, ln, alt, N, E, D))            # return the tuple in DMS format as well

##########################################################################

def haversine(pointA, pointB):

    if (type(pointA) != tuple) or (type(pointB) != tuple):
        raise TypeError("Only tuples are supported as arguments")

    lat1 = pointA[0]
    lon1 = pointA[1]

    lat2 = pointB[0]
    lon2 = pointB[1]

    # convert decimal degrees to radians 
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2]) 

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r


def initial_bearing(pointA, pointB):

    if (type(pointA) != tuple) or (type(pointB) != tuple):
        raise TypeError("Only tuples are supported as arguments")

    lat1 = radians(pointA[0])
    lat2 = radians(pointB[0])

    diffLong = radians(pointB[1] - pointA[1])

    x = sin(diffLong) * cos(lat2)
    y = cos(lat1) * sin(lat2) - (sin(lat1)
            * cos(lat2) * cos(diffLong))

    initial_bearing = atan2(x, y)

    # Now we have the initial bearing but math.atan2 return values
    # from -180 to + 180 degrees which is not what we want for a compass bearing
    # The solution is to normalize the initial bearing as shown below
    initial_bearing = degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360

    return compass_bearing
##########################################################################
def getnewpoint(lat, lon, dist, bearing):
# Define starting point.
    start = geopy.Point(lat, lon)
# Define a general distance object, initialized with a distance of 1 km.
    d = geopy.distance.geodesic(kilometers = dist/1000.0)   # get the distance as a point

# Use the `destination` method with a bearing of 0 degrees (which is north)
    np=d.destination(point=start, bearing=bearing)                  # go to 
    return (np.latitude, np.longitude)                              # return the result

##########################################################################
def convertline(tsk):                       # conver the start line on several point so it will draw as a LINE
    tasks=tsk['tasks'][0]                   # use the TSK
    tpt=tasks['TPpointstype']               # get the TP style ... Line, cylinder, etc, ...
    legs=tasks['legs']                      # get the legs
    ntp=len(tpt)                            # get the number of turning points
    lasttp=tpt[ntp-1]                       # check if the last is the START line
    if str(lasttp) == 'Line':               # only in the case of the LINE
        coor1=legs[(ntp-1)*2]               # coord of the start gate
        lat1=coor1[0]
        lon1=coor1[1]
        coor2=legs[(ntp-2)*2]               # get the coord of the first TP
        lat2=coor2[0]
        lon2=coor2[1]
        size=legs[(ntp-1)*2+1][0]           # get the size of the START GATE
        legs[(ntp-1)*2+1][0]=0
        p1=(lat1, lon1)
        p2=(lat2, lon2)
        bearing=initial_bearing(p1,p2)      # get the bearing from the start gate to the first TP
        np1=getnewpoint(lat1,lon1, size, bearing+90)  # next point is from center of start line to half of the size to the right
        np2=getnewpoint(lat1,lon1, size, bearing-90)
        np=[]
        np.append(np1[0])                   # append this to the existing .tsk
        np.append(np1[1])
        legs.append(np)                     # add this extra point
        s=[]
        s.append(0)
        legs.append(s)                      # set the size as ZERO
        np=[]
        np.append(np2[0])
        np.append(np2[1])
        legs.append(np)                     # add the other point of the perpendicular line
        s=[]
        s.append(0)                         # set the size as ZERO
        legs.append(s)

    firsttp=tpt[0]                          # check if the first TP  is the FINISH line
    if str(firsttp) == 'Line':              # only in the case of the LINE
        coor1=legs[0]                       # coord of the start gate
        lat1=coor1[0]
        lon1=coor1[1]
        coor2=legs[2]                       # get the coord of the first TP
        lat2=coor2[0]
        lon2=coor2[1]
        size=legs[1][0]                     # get the size / radius of the FINISH GATE
        legs[1][0]=0
        p1=(lat1, lon1)
        p2=(lat2, lon2)
        bearing=initial_bearing(p1,p2)      # get the bearing from the start gate to the first TP
        np1=getnewpoint(lat1,lon1, size, bearing+90)  # next point is from center of start line to radius the size to the right
        np2=getnewpoint(lat1,lon1, size, bearing-90)
        np=[]
        np.append(np1[0])                   # append this to the existing .tsk
        np.append(np1[1])
        legs.insert(0, np)
        s=[]
        s.append(0)
        legs.insert(1, s)
        np=[]
        np.append(np2[0])
        np.append(np2[1])
        legs.insert(2, np)
        s=[]
        s.append(0)
        legs.insert(3, s)

    return (tsk)                            # return the modifies .tsk




