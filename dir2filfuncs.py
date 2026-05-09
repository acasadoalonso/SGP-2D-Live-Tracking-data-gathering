#!/usr/bin/python3
# -*- coding: UTF-8 -*-

#-------------------------------------------------------------------------------------------------------------------#
#
#   This script get the data from a directory and extract the FLARM information
#
#-------------------------------------------------------------------------------------------------------------------#
import sys
import json
import urllib.request
import urllib.error
import urllib.parse
import datetime
import time
import os
import math
import pycountry
import socket
from pprint import pprint
from ognddbfuncs import *
from getflarm import *
import config

def dir2fil(FlarmID, prt=False, web=False):
    FlarmID=FlarmID.upper()
    hostname = socket.gethostname()
    if not web:
       print("Args: ", FlarmID, prt)
       print("DBhost:", config.DBhost, "ServerName:", hostname)
    stats = {}                                              # statistics
    SARpath = config.SARpath	                            # directory where to store IGC directory
    # directory where will got the IGC files
    dirpath = SARpath+"IGCfiles/DIR/"
    # directory where will got the IGC files
    tmppath = SARpath+"IGCfiles/TMP/"
    start_time = time.time()
    local_time = datetime.datetime.now()
    if not web:
       print("Extracting FLARM info from files at: ", dirpath, ":", FlarmID)
       print("==============================================================\n\n")

    							    # check that we have such directory
    if not os.path.isdir(dirpath):
        print("Not IGC directory: ", dirpath, "\n\n", file=sys.stderr)
        return(-1)                                          # nothing else to do
    # if the working directory does not exists ??
    if not os.path.isdir(tmppath):
        os.system("mkdir "+tmppath)                         # make it !!!
    else:
        						    # remove and clean the working directory
        os.system("rm "+tmppath+"/*")
    ld = os.listdir(dirpath)                                # get the list of files
    							    # count of number of records processed
    cnt = 0
    nfil= 0
    fname=''
    for f in ld:                                            # scan all the files on the from directory
        fd = open(dirpath+"/"+f, 'rb')                      # open the file
        nfil += 1					    # number of files visited
        # extract the FLARM data from the embeded records
        cnt += getflarmfile(fd, f, tmppath+f, stats, prt)
        fd.close()                                          # close the file
        sys.stdout.flush()                                  # print results
    if not web:
        print("Records processed:", cnt, "\n\nStats & Warnings:", stats)     # print the stats
    if (FlarmID == '' or FlarmID == 'NFLARM') and not web:  # if no FlarmID, nothing else to do
        print("Files processed now at:", tmppath, nfil, "Files \n")
        print("==============================================================\n\n")
        return(fname)                                       # nothing else to do ...
    # remember the current directory
    cwd = os.getcwd()
    if not web:
       print("From CD:", cwd, "To:", tmppath)               # report it
    # report current directory and the new one
    os.chdir(tmppath)
    # file name of the rebuilt file
    fname = FlarmID+'.'+getognreg(FlarmID)+'.'+getogncn(FlarmID)+'.igc'
    if os.path.isfile(fname):                               # remove to avoid errors
        os.remove(fname)                                    # remove if exists
        # get the new IGC files based on the FLARM messages
    cmd = "grep 'FLARM "+FlarmID+"\|ICAO  "+FlarmID+"' * | sort -k 3 | python3 " + cwd+"/genIGC.py "+FlarmID+" > "+fname
    
    os.system(cmd)
    if not web:
       print ("CMD:", cmd)
       print("New IGC rebuilt file:", fname, " is at:", tmppath)
       print("==============================================================\n\n")
    return ("/IGCfiles/TMP/"+fname)
