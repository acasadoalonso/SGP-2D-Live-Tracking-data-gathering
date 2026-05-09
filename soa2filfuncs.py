#!/usr/bin/python3
# -*- coding: UTF-8 -*-
#
# SoaringSpot IGC files extractor 
# ===============================
#
import sys
import json
import urllib.request, urllib.error, urllib.parse
import base64
import datetime
import time
import hmac
import hashlib
import base64
#import OpenSSL
#import uritemplate
import pycountry
import math
import os
import socket
import config
from ognddbfuncs import *
from getflarm import *
from simplehal import HalDocument, Resolver
from pprint import pprint
from config import *
from dtfuncs import naive_utcnow

pgmver='2.2'
#-------------------------------------------------------------------------------------------------------------------#


##################################################################


def getapidata(url, auth):                  # get the data from the API server

    req = urllib.request.Request(url)
    req.add_header('Authorization', auth)   # build the authorization header
    req.add_header("Accept", "application/json")
    req.add_header("Content-Type", "application/hal+json")
    r = urllib.request.urlopen(req)         # open the url resource
    j_obj = json.load(r)                    # convert to JSON
    return j_obj                            # return the JSON object

###################################################################


# get the data from the soaring spot and return it as a HAL document
def gdata(url, key, prt='no'):
    global auth                             # auth and apiurl are globals
    global apiurl
    j_obj = getapidata(url, auth)           # call the fuction that get it
                                            # convert to HAL
    if prt == 'yes':                        # if print is required
        print(json.dumps(j_obj, indent=4))
    cd = HalDocument.get_data(HalDocument.from_python(
        j_obj), apiurl+'rel/' + key)        # get the data from the HAL document
    return cd


def getemb(base, ctype):
    global apiurl
    return(base['_embedded'][apiurl+'rel/'+ctype])


def getlinks(base, ctype):
    global apiurl
    return (base['_links'][apiurl+'rel/'+ctype]['href'])


###################################################################
def soa2fil(client, secretkey,idx, FlarmID, execopt,prt=False, web=False):
   global auth                             	# auth and apiurl are globals
   global apiurl
   FlarmID=FlarmID.upper()
   fr=''
   idflram=''
   if not web:
      print ("\nSoaringSpot IGC files extractor for SAR4comp           Program version:", pgmver)
      if prt:
         print ("Args: ", client, secretkey, idx, FlarmID, execopt)
   SARpath = config.SARpath
   cwd = os.getcwd()			    	# get the current working directory
                                            	# where to find the clientid and secretkey files
   secpath = cwd+"/SoaringSpot/"
   apiurl = "http://api.soaringspot.com/"      	# soaringspot API URL
   rel = "v1"                                  	# we use API version 1
   taskType = "SailplaneRacing"                	# race type
                                            	# the subdirectory where to store the extracted files
   base = "/IGCfiles/SOA/"			# destination file base
   dirpath = SARpath+base			# destination file
   if execopt:                                 	# if we choose the option of gen the IGC file

                                            	# delete all the files to avoid problems
      os.system("rm -r "+dirpath+"/*")
      if not web:
         print ("Directory  "+dirpath+"/ deleted")

# ==============================================#
   hostname = socket.gethostname()	    	# hostname as control
   start_time = time.time()                    	# get the time now
   utc = naive_utcnow()            		# the UTC time
                                            	# print the time for information only
   date = utc.strftime("%Y-%m-%dT%H:%M:%SZ")   	# get the local time
   local_time = datetime.datetime.now()        	# the local time
   fl_date_time = local_time.strftime("%Y%m%d") # get the local time
   dttoday = local_time.strftime("%Y-%m-%d")    # get the local time
   if not web:
      print("Hostname:", hostname)
      print("UTC Time is now:", utc)
      print(date)                             	#
      print("Local Time is now:", local_time, dttoday)	# print the time for information only
      if prt:
         print("Config params.  SECpath:", secpath)

   nonce = base64.b64encode(os.urandom(36))    	# get the once base
                                            	# open the file with the client id
   secretkey = secretkey.rstrip()
   message = nonce+date.encode(encoding='utf-8')+client.encode(encoding='utf-8')   # build the message
                                            	# and the message digest
   digest = hmac.new(secretkey, msg=message, digestmod=hashlib.sha256).digest()
   signature = str(base64.b64encode(digest).decode())   # build the digital signature
                                            	# the AUTHORIZATION ID is built now

   auth = apiurl+rel+'/hmac/v1 ClientID="'+client+'",Signature="' + \
    signature+'",Nonce="'+nonce.decode(encoding='utf-8')+'",Created="'+date+'" '
   #print ("URLiauth:", auth)
                                            	# get the initial base of the tree
   url1 = apiurl+rel
                                            	# get the contest data, first instance
   cd = gdata(url1, 'contests', prt='no')[0]

   category = cd['category']
   eventname = cd['name']
   compid = cd['id']
   country = cd['country']                     	# country code - 2 chars code
   compcountry = country		    	# country as defaults for pilots
                                            	# convert the 2 chars ID to the 3 chars ID
   ccc = pycountry.countries.get(alpha_2=country)
   country3 = ccc.alpha_3
   endate = cd['end_date']
   lc = getemb(cd, 'location')                 	# location data
   lcname = lc['name']                         	# location name

   print("\n\n= Contest ===============================")
   print("Category:", category, "Comp name:", eventname, "Comp ID:", compid)
   print("Loc Name:", lcname,   "Country: ", country, country3, "End date:",  endate)
   print("=========================================\n\n")

   npil = 0                                    	# init the number of pilots
   stats = {}                                  	# statistics
                                            	# directory where it goes the IGC files
   igcdir = ''

# Build the tracks and turn points, exploring the contestants and task within each class
# go thru the different classes now within the daya
   PrevTaskDate = ""
   if not web:
      print("Classes:\n========\n\n")
   last=idx
   for cl in getemb(cd, 'classes'):
       #print "CLCLCL", cl
       classname = cl["type"]                  	# search for each class
       if not web:
          print("Class:", classname, "\n\n")      	# search for each class
                                            	# search for the contestants on each class
       url3 = getlinks(cl, "class_results")
       #print ("URL",url3)
       ll= len(gdata(url3, "class_results", prt='no')) 
       i=0
       if last == 999:		# case of LAST
           ctt = gdata(url3,   "class_results", prt='no')[ll-2]   # get the results data
           idx=ll-2
           tasktype = ctt["task_type"]
           taskdate = ctt["task_date"]
           print ("Selecting for: ", taskdate, "Index: ", idx)
       i=0
       while i < ll and False:
           ctt = gdata(url3,   "class_results", prt='no')[i]   # get the results data
           print ("LLL", i, ctt)
           i +=1
           print("==============================================================================================================================")

       if ll  > idx:
           ctt = gdata(url3,   "class_results", prt='no')[idx]   # get the results data
       else:
           print("The class ", classname, "it is not ready yet\n")
           continue                            	# the class is not ready
       
       #pprint ( gdata(url3,   "class_results", prt='no'))   # get the results data
       tasktype = ctt["task_type"]
       taskdate = ctt["task_date"]
       if not web:
       	  print("Task Type: ", tasktype, "Task date: ", taskdate)

       if PrevTaskDate == "":                  	# check the cases where the task dates are not the same within an index day
           PrevTaskDate = taskdate
       elif PrevTaskDate != taskdate:
           print(">>>>Warning: Task dates are different for the same index day !!!")
       fft = getemb(ctt, "results")            	# go to the results data
       for ft in fft:
           #print "FT", ft, "\n\n"
                                            	# go the contestants (pilot) information
           cnt = getemb(ft, "contestant")
           pil = getemb(cnt, "pilot")[0]       	# get the pilot name information
           #print ("LLL", pil)
           npil += 1
           ognid = ''
           if "igc_file" in ft:
               fftc = getlinks(ft, "flight")   	# URL to the file to be downloaded
               igcfile = ft["igc_file"]        	# full IGC file DIR/IGCfilename
                                            	# the first 3 char are the directory where it goes for example: 95I
               igcdir = igcfile[0:3]
           else:
               print(">>> missing FILE >>>>>", pil["first_name"].encode('utf8').decode('utf-8'), pil["last_name"].encode('utf8').decode('utf-8'))
               continue
           if 'aircraft_registration' in cnt:
               regi = cnt['aircraft_registration']
               ognid=getognflarmid(regi)         # get the flarm if from the OGN DDB
           else:
               regi=''
               ognid=''

           igcfilename = dirpath+"/"+taskdate+"/"+classname+"-"+igcfile[4:]
           if not os.path.isdir(dirpath+"/"+taskdate):
               os.system("mkdir "+dirpath+"/"+taskdate)
               os.system("chmod 775 "+dirpath+"/"+taskdate)
               print(" OK directory made: "+dirpath+"/"+taskdate)     	# create the directory if needed
           if "nationality" in pil:            	# extracts the nationality as a doc
               nationality = pil['nationality']
           else:
               nationality = "UNKOWN"          	# report that we are extracting the flight of that pilot
           if "live_track_id" in cnt:
                 livetrk = cnt['live_track_id']# flarmID and OGN pair
           else:
                 livetrk = 'NOFLARM'
                 print ("No FlarmID for:", pil)
                 continue
           if len(livetrk) == 9:
               idflarm = livetrk[3:9]		# case that just the FlarmID, no piaring
           if len(livetrk) == 19:              	# format:  FLR123456 OGN654321
               idflarm = livetrk[3:9]		# case that just the FlarmID and OGN tracker pair
           if len(livetrk) == 6:               	# in case of missing FLR/ICA/OGN (deprecated)
               idflarm = livetrk[0:6]		# case that just the FlarmID, no piaring
           if 'flight_recorders' in cnt:
               fr = cnt['flight_recorders']
               fr = fr.rstrip('\n')
               fr = fr.rstrip('\r')
               fr = fr.replace ('\n', ' ')
               fr = fr.replace ('\r', ' ')


           if not web:
              print("Pilot:>>>>", pil["first_name"], pil["last_name"], nationality, fr, idflarm, regi, ognid)
           time.sleep(3)
           try: 
               req = urllib.request.Request(fftc)  	# open the URL
           except HTTPError:			# in case of HTTP error
               time.sleep(2)			# give it a second chance
               req = urllib.request.Request(fftc)  	# open the URL
                                            	# build the authorization header
           req.add_header('Authorization', auth)
           req.add_header("Accept", "application/json")
           req.add_header("Content-Type", "application/hal+json")
           r = urllib.request.urlopen(req)     	# open the url resource
           # call the routine that will read the file and handle the FLARM records
           # grab and convert the FLARM records
           cnt = getflarmfile(r, igcfile, igcfilename, stats, prt)
           sys.stdout.flush()                  	# print the records
           if prt and not web:
               print("Number of records:", igcfilename, cnt)
               print("----------------------------------------------------------------")
       if not web:
          print("----------------------------------------------------------------\n\n")
   if not web:
      print("Stats:", stats)
#
# Check if the exec option is requested
#
   fname=''
   if execopt:
       cwd = os.getcwd()
       if os.path.isdir(dirpath):
                                            # report current directory and the new one
           os.chdir(dirpath)
       else:
           print("Not available target directory:", dirpath+taskdate)
       nf= os.listdir(dirpath+'/'+taskdate)
       if len(nf) == 0:
          print(">>> No files generated ...")
          exit(-1)
       else:
          print("Files generated: ...", nf)
       fname = FlarmID+'.'+getognreg(FlarmID)+'.'+getogncn(FlarmID)+'.igc'
                                            # remove the file to avoid errors
       #print("FFF", fname)
       if os.path.isfile(fname):
           os.remove(fname)                                # remove if exists
           # get the new IGC files based on the FLARM messages
       cmd = "(cd "+dirpath+" && grep 'FLARM "+FlarmID+"\|ICAO  "+FlarmID+"' "+taskdate+"/* | sort -k 3 | python3 " + cwd+"/genIGC.py "+FlarmID+") > "+fname

       if not web: 
          print("Extracting the IGC file from embeded FLARM messages \nFrom CD:", cwd, "To:", dirpath)
          print ("CMD:", cmd)
          print("Resulting IGC file is on:", dirpath, "As: ", fname)

       os.system(cmd)


# print the number of pilots as a reference and control
   if not web:
      print("= Pilots ===========================", npil)
   return (base+fname)
