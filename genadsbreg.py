#!/usr/bin/python3

#!/usr/bin/python3
#
# Python code to show access to OGN Beacons
#
# Version for gathering all the records for the world
#

from   datetime import datetime
from   ctypes import *
import time
import string
import sys
import os
import json
import csv
import socket
import signal
import atexit
import MySQLdb                          # the SQL data base routines^M
import sqlite3
import argparse

class create_dict(dict): 
  
    # __init__ function 
    def __init__(self): 
        self = dict() 
          
    # Function to add key:value 
    def add(self, key, value): 
        self[key] = value

programver = 'V1.00'			# manually set the program version !!!

print("\n\nGen the ADSB registration JSON file : "+programver)
print("==================================================================================")
#					  report the program version based on file date
print("Program Version:", time.ctime(os.path.getmtime(__file__)))
date = datetime.utcnow()                # get the date
dte = date.strftime("%y%m%d")           # today's date
hostname = socket.gethostname()		# get the hostname 
print("\nDate: ", date, "UTC on SERVER:", hostname, "Process ID:", os.getpid())
date = datetime.now()
print("Time now is: ", date, " Local time")
date = datetime.utcnow()
tme = date.strftime("%y-%m-%d %H:%M:%S")# today's date


# --------------------------------------#
#
import config				# import the configuration details

# --------------------------------------#
DBpath      = config.DBpath
DBhost      = config.DBhost
DBuser      = config.DBuser
DBpasswd    = config.DBpasswd
DBname      = config.DBname
OGNT        = config.OGNT
filedb      = "BasicAircraftLookup.sqb"
filefa      = "flightaware-20200924.csv"
# --------------------------------------#
parser = argparse.ArgumentParser(description="Gen the ADSB registration file")
parser.add_argument('-p',  '--print',     required=False,
                    dest='prt',   action='store', default=False)
parser.add_argument('-m',  '--MYSQL',     required=False,
                    dest='MYSQL',   action='store', default=False)
parser.add_argument('-s',  '--S3file',     required=False,
                    dest='S3file',   action='store', default="BasicAircraftLookup.sqb")
parser.add_argument('-f',  '--FlightAare',     required=False,
                    dest='fa',   action='store', default=False)
args = parser.parse_args()
prt      = args.prt			# print on|off
MYSQL    = args.MYSQL			# Use MySQL or SQLITE3
filedb   = args.S3file			# SQLITE3 file name
flighta  = args.fa

# --------------------------------------#
# --------------------------------------#
if MYSQL:
					# open the DataBase
   conn = MySQLdb.connect(host=DBhost, user=DBuser, passwd=DBpasswd, db=DBname)
   print("MySQL: Database:", DBname, " at Host:", DBhost)
else:
   conn = sqlite3.connect(filedb)
   print("SQLITE3 file:", filedb)

cursA = conn.cursor()     # set the cursor
cursM = conn.cursor()     # set the cursor


#----------------------genadsbreg.py start-----------------------#

mydict = create_dict()			# create the dictionary
cursA.execute("SELECT Aircraft.Icao as ICAO, Registration as REG, ModelID as MODEL  FROM Aircraft ;")
res=cursA.fetchall()			# get all the aircraft from the DB

counter=0				# counter of number of aircrafts seen
cnt    =0				# counter of extra aircraft from FA
cntfa  =0				# counter of extra aircraft from FA
for row in res:
    if row[2] == None:			# if no model ???
       model="UNKW"
    else:				# get the model description from the model table
       cursM.execute("SELECT Icao FROM Model WHERE ModelID = "+str(row[2])+" ;")
       mod = cursM.fetchone()
       model = mod[0]
       if model == None or model == '':
          model  = 'UNKW'
    mydict.add(row[0],({"Reg":row[1],"Model":model}))
    counter += 1
print ("Registrations from VRS:", counter)
# -----------------------------------------------------------------#
if flighta:				# if extra data from FlightAare 
   print ("Adding data from:", filefa)
   cnt=counter
   with open(filefa, newline='') as csvfile:
     reader = csv.DictReader(csvfile)
     for row in reader:
         model = row['t']
         icao=row['icao24']
         reg =row['r']
         if model == None or model == '':
             model  = 'UNKW'
             modelid = 0
         country=icao[0] 
         if country == '3' or country == '4' or country == '5' :
            mydict.add(icao,({"Reg":reg,"Model":model}))	# add it to the dict
            cntfa += 1
         if model !=  'UNKW':		# try to get the modelID (number) from the model table
             modelid = 0
             cursM.execute("SELECT ModelID FROM Model WHERE Icao = '"+model+"';")
             mod = cursM.fetchone()
             if mod != None:
                modelid=mod[0]
         counter += 1			# add that aircraft to the table
         sqlstm = "INSERT INTO Aircraft VALUES ("+str(counter)+",'"+icao+"','"+reg+"',"+str(modelid)+", 0, '"+tme+"');"
         
         cursA.execute(sqlstm)
         if counter%100000 == 0:
            print ("Process:", counter, cntfa, datetime.utcnow().strftime("%y-%m-%d %H:%M:%S"))


#print (mydict)
#stud_json = json.dumps(mydict, indent=4, sort_keys=True)
stud_json = json.dumps(mydict)
#print(stud_json) 
fd=open ("ADSBreg.py","w")
fd.write("ADSBreg="+stud_json)
fd.close()
print (len(stud_json), " Registration generated at ADSBreg.py ", counter, counter - cnt)
conn.commit()
conn.close()
exit(0)