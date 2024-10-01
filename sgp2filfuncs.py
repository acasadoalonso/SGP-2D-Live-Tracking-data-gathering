#!/usr/bin/python3
# -*- coding: UTF-8 -*-

#
#   This script get the dat from the sgp.aero server and gen the SW JSON file
#
import sys
import json
import urllib.request, urllib.error, urllib.parse
import datetime
import time
import os
import math
import pycountry
import socket
from pprint import pprint
from ognddbfuncs import *
from getflarm import *


#-------------------------------------------------------------------------------------------------------------------#
import config
pgmver='2.2'
def sgp2fil(qsgpID, day, FlarmID, execopt=False, prt=False, web=False):
    FlarmID=FlarmID.upper()
    stats = {}                                              	# statistics
    cucpath = config.cucFileLocation
    SARpath = config.SARpath                			# directory where to stor IGC files
    pilotsID = {}
                                                        	# table with the pilots ID and namme
    flarmsID = {}
                                                        	# directory where will got the IGC files
    base = "/IGCfiles/SGP/"
    dirpath = SARpath+base
								# directory where to stor the JSON file generated
    hostname = socket.gethostname()
    if not web:
       print("\n\nExtract the IGC files from the www.sgp.aero web server", pgmver)
       print("Args:", qsgpID, day, execopt, FlarmID, execopt, prt)
       print("==============================================================\n\n")
       print("DBhost:", config.DBhost, "ServerName:", hostname)
    start_time = time.time()
    local_time = datetime.datetime.now()
    # get the data from the server
    j = urllib.request.urlopen('http://www.crosscountry.aero/c/sgp/rest/comps/')
    j_obj = json.load(j)                                    	# convert it
    if qsgpID == '0':                                       	# just display the list of competition and exit
        #print j_obj
        j = json.dumps(j_obj, indent=4)
        print(j)
        return('NOevent')                                       # nothing else to do it
    else:
        for xx in j_obj:                                    	# extract the data of our event
            if xx['id'] == int(qsgpID):
                if not web:
                   print("Title:", xx['fullEditionTitle'])

                                                        	# print the time for information only
        if not web:
           print("CompID:", qsgpID, "Time is now:", local_time)

    fl_date_time = local_time.strftime("%Y%m%d")            	# get the local time
    if not web:
       print("===========================: \n") 		# just a trace

#
# get the JSON string for the web server
#
    j = urllib.request.urlopen( 'http://www.crosscountry.aero/c/sgp/rest/comp/'+str(qsgpID))
    j_obj = json.load(j)                                    	# convert it to dict
    if prt and not web:
        #print j_obj
        j = json.dumps(j_obj, indent=4)
        print(j)
        # exit(0)
#
# the different pieces of information
#

    npil = 0							# number of pilots found
    pilots = j_obj["p"]						# get the pilot information
    if prt and not web:
       print("Pilots:", len(pilots))
       print("==========")
    for id in pilots:                                    	# display the pilot information for better doc
       #
       if prt and not web:
          print("---------------------")
       pid = pilots[id]["i"]                            	# get the pilot ID
       fname = pilots[id]["f"]                          	# first name
       lname = pilots[id]["l"]                          	# last name
       compid = pilots[id]["d"]                         	# competition number
       country = pilots[id]["z"]                        	# two letters country code
       model = pilots[id]["s"]                          	# aircraft model
       j = pilots[id]["j"]                              	# ranking list
       rankingid = pilots[id]["r"]                      	# ranking id
       flarmID = pilots[id]["q"]                        	# FlarmID
       registration = pilots[id]["w"]                   	# registration
       if flarmID == "":
                                                        	# get it from the OGN data
           flarmID = getognflarmid(registration)

       if hostname == "SWserver":				# deal with the different implementation of pycountry
                                                        	# the the 3 letter country code
           ccc = pycountry.countries.get(alpha_2=country)
           country = ccc.alpha_3				# convert to a 3 letter code
       else:	
                                                        	# the the 3 letter country code
           ccc = pycountry.countries.get(alpha_2=country)
           country = ccc.alpha_3				# convert to a 3 letter code

       pilotname = (fname+" "+lname).encode('utf8').decode('utf-8')
       if prt and not web:
          print("Pilot:", pid, pilotname, compid, country, model, j, rankingid, registration, flarmID)
       pilotsID[pid] = pilotname
       flarmsID[pid] = flarmID
       npil += 1					        # increase the number of pilots
       if prt and not web:
          print("---------------------")
    if not web:
       print("Competition")
       print("===========")
    comp = j_obj["c"]						# get the competition information
    comp_firstday = comp['a']			        	# first day of the competition
    comp_lastday = comp['b']			        	# last day of the competition
    comp_name = comp['t']			                # event name
    comp_shortname = comp['l']			        	# event short name
    comp_id = comp['i']
    if not web:
       print("Comp ID:", comp_id, "Name:", comp_name, "Short name:", comp_shortname, comp_firstday, comp_lastday)
    numberofactivedays = 0

    if j_obj.get("j") != None:
        numberofactivedays = j_obj["j"]
    if j_obj.get("i") == None:			        	# check if is fully setup the web site
        print("No index of days ... exiting.")
        return('Noindex')
    indexofdays = j_obj["i"]
    if day == 999:
       day=len(indexofdays)-1                                  	# print "Index of Days", indexofdays
    if day != 0:                                          	# check the days
        cday = 0
        for dayday in indexofdays:
            #print "DAYDAY", days, dayday
            if dayday["l"].upper() == day:
                day = cday
                break
            else:
                cday += 1
                continue

    date = indexofdays[day]["d"]		                # date
    title = indexofdays[day]["t"] 		                # day tittle
    shorttitle = indexofdays[day]["l"]    	                # day short title
    starttime = indexofdays[day]["a"]    	                # start time millis from midnite
    daytype = indexofdays[day]["y"]    	                	# day type: 1, 2, 3 ...
    dayid = indexofdays[day]["i"] 		                # day ID
    if not web:
       print("DATE:", date, "Title:", title, "Day:", shorttitle, "==>", day, "\nStart time(millis):", starttime, "Day type:", daytype, "Day ID:", dayid, "Number of active days:", numberofactivedays)
                                                        	# get the data for day
    d = urllib.request.urlopen(
        'http://www.crosscountry.aero/c/sgp/rest/day/'+str(qsgpID)+'/'+str(dayid))
    d_obj = json.load(d)                                    	# convert to dict
    race = d_obj["l"]				        	# get the race information
    results = d_obj["r"]			        	# get the results information
    if not web:
       print("Race:", race)                                    	# show the race name
       print("Results:")
       print("========")
       #pprint (results)
                                                        	# get the scoring info
    rr = results['s']
    # pprint(rr)
    p = 0                                                   	# number of pilots
    if os.path.isdir(dirpath+"/"+str(date)):
                                                        	# delete all the files on that directory
        os.system("rm "+dirpath+"/"+str(date)+"/*")
    for r in rr:                                            	# get all the pilots
        # pprint(r)
        pilotid = r['h']                                    	# pilot ID
        cn = r['j']                                         	# competition id
        if 'g' in r:
            fr = r['g']                                     	# flight recorder used
        else:
            fr = "ZZZ"
            print("No FR>>>>:", pilotid, cn)
                                                        	# file number of the web server
        filenum = r['w']
        if filenum == 0:
            print("Error: IGC file not found !!!>>> PID", pilotid, "Pilot: ", str(pilotsID[pilotid]).encode('utf-8').decode('utf-8'), cn, filenum)
            continue
        fftc = "http://www.crosscountry.aero/flight/download/sgp/" + \
            str(filenum)                                    	# the URL to download the IGC fle
        if not web:
           print("Pilot: ", str(pilotsID[pilotid]).encode('utf-8').decode('utf-8'), cn, filenum, "FR:", fr, "FlarmID:", flarmsID[pilotid])
        if not os.path.isdir(dirpath+"/"+str(date)):
            os.system("mkdir "+dirpath+"/"+str(date))
            os.system("chmod 775 "+dirpath+"/"+str(date))
            if not web:
                print(" OK directory made: "+dirpath+"/"+str(date))

        req = urllib.request.Request(fftc)
        req.add_header("Accept", "application/json")
        req.add_header("Content-Type", "application/text")
        fd = urllib.request.urlopen(req)                    	# open the url resource
                                                        	# call the routine that will read the file and handle the FLARM records
        igcfilename = dirpath+"/"+str(date)+"/"+cn+"."+fr[4:7]+".igc"
                                                            	# grab and convert FLARM records
        cnt = getflarmfile(fd, cn, igcfilename,  stats, prt)
        sys.stdout.flush()                                  	# print results
        if prt and not web:
            print("Number of records:", igcfilename, cnt, "CompID", cn)
            print("----------------------------------------------------------------")
        p += 1                                              	# counter of pilotsa
    if p != npil:
        print("Error on geting the score data ....Pilots:", npil, "Files:", p, "\n\n")
    if not web:
       print(stats)


                                                        	# print the number of pilots as a reference and control
       print("= Pilots ===========================", npil)

                                                        	# print information about the day
    d = urllib.request.urlopen('http://www.crosscountry.aero/c/sgp/rest/day/'+str(qsgpID)+'/'+str(dayid))
    d_obj = json.load(d)
    if prt and not web:
        print("____________________________________________________________")
        d = json.dumps(d_obj, indent=4)
        #print(d)
    if numberofactivedays == 0:
        print("No active days ...")
    if not web:
       print("=============================")
       print("Day: ", day, "DayID: ", dayid)
       print("=============================")
       #print "DDD", d_obj
    comp_day = d_obj["@type"]
    comp_id = d_obj["e"]				        # again the compatition ID
    comp_dayid = d_obj["i"]				        # the day ID
    comp_date = d_obj["d"]				        # date in milliseconds from the Unix epoch
    # day type: 1= valid, 2= practice, 3= canceled, 4= rest, 9= other
    comp_daytype = d_obj["y"]
    comp_daytitle = d_obj["l"]					# day title
    comp_shortdaytitle = d_obj["t"]				# short day title
    comp_starttime = d_obj["a"]					# start time millis from midnite
    comp_startaltitude = d_obj["h"]				# start altitude
    comp_finishaltitude = d_obj["f"]				# finish altitude
    if not web:
       print("Comp day:", comp_day, "Comp ID:", comp_id, "Comp ID DAY:", comp_dayid, date, "Title:", comp_daytitle, comp_shortdaytitle, "\nStart time (millis):", comp_starttime, "Start alt.:", comp_startaltitude, "Finish Alt.:", comp_finishaltitude)
    if "k" in d_obj:
        comp_taskinfo = d_obj["k"]			        # task infor data
    else:
        print("No task for that day...")
        print("WARNING: No valid JSON file generated .....................")
        return('NOtask')
    # event
    
    #
    # close the files and exit
    #
    fname=''
    if execopt:
        cwd = os.getcwd()
        if not web:
           print (getogninfo(FlarmID))
           print("Extracting the IGC file from embeded FLARM messages \nFrom CD:", cwd, "To:", dirpath + \
            "/"+str(date))
                                                            	# report current directory and the new one
        dirpath=dirpath+"/"+str(date)+"/"
        os.chdir(dirpath)
    
        fname = FlarmID+'.'+getognreg(FlarmID)+'.'+getogncn(FlarmID)+'.igc'
                                                            	# remove to avoid errors
        if os.path.isfile(fname):
                                                            	# remove if exists
            os.remove(fname)
                                                            	# get the new IGC files based on the FLARM messages
        cmd = "grep 'FLARM "+FlarmID+"\|ICAO  "+FlarmID+"' * | sort -k 3 | python3 " + cwd+"/genIGC.py "+FlarmID+" > "+fname
        os.system(cmd)
        if not web:
           print ("CMD:", cmd)
           print("Resulting IGC file is on:", dirpath, "As: ", fname)
    if not web: 
       print("Pilots found ... ", npil)
       print("=====================================================================: \n\n\n") 		# just a trace
    return(base+str(date)+"/"+fname)
