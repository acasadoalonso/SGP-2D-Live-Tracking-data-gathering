#!/usr/bin/python3
# =================================================================
#
# Python code to gen the list of ADSB code and their registrations
#
# Version for gathering all the records for the world
#
# =================================================================

import config				# import the configuration details
from   datetime import datetime
import time
import os
import json
import csv
import socket
import MySQLdb                          # the SQL data base routines^M
import sqlite3
import argparse
from tqdm import tqdm
from dtfuncs import naive_utcnow

def linecount_wc(filename):
    return int(os.popen('wc -l '+filename).read().split()[0])


class create_dict(dict):

    # __init__ function
    def __init__(self):
        self = dict()

    # Function to add key:value
    def add(self, key, value):
        self[key] = value


programver = 'V1.02'			# manually set the program version !!!

print("\n\nGen the ADSB registration JSON file : "+programver)
print("==================================================================================")
#					  report the program version based on file date
print("Program Version:", time.ctime(os.path.getmtime(__file__)))
date = naive_utcnow()                # get the date
dte = date.strftime("%y%m%d")           # today's date
hostname = socket.gethostname()		# get the hostname
print("\nDate: ", date, "UTC on SERVER:", hostname, "Process ID:", os.getpid())
date = datetime.now()
print("Time now is: ", date, " Local time")
date = naive_utcnow()
tme = date.strftime("%y-%m-%d %H:%M:%S")  # today's date
Y = date.strftime("%Y")  # today's date
M = date.strftime("%m")  # today's date


# --------------------------------------#
#
# --------------------------------------#
DBpath = config.DBpath
DBhost = config.DBhost
DBuser = config.DBuser
DBpasswd = config.DBpasswd
DBname = config.DBname
OGNT = config.OGNT
# the 3 files to get that registration data
filedb = "utils/BasicAircraftLookup.sqb"
filefa = "utils/flightaware-20200924.csv"
filefa = "utils/flightaware-20231026.csv"
fileos = "utils/aircraftDatabase-"+Y+"-"+M+".csv"
# --------------------------------------#
parser = argparse.ArgumentParser(description="Gen the ADSB registration file\n")
parser.add_argument('-p', '--print', required=False,
                    dest='prt', action='store', default=False)
parser.add_argument('-m', '--MYSQL', required=False,
                    dest='MYSQL', action='store', default=False)
parser.add_argument('-s', '--S3file', required=False,
                    dest='S3file', action='store', default="utils/BasicAircraftLookup.sqb")
parser.add_argument('-a', '--adddb', required=False,
                    dest='adddb', action='store', default=False)
parser.add_argument('-f', '--FlightAware', required=False,
                    dest='fa', action='store', default=False)
parser.add_argument('-o', '--OpenSky', required=False,
                    dest='os', action='store', default=False)
args = parser.parse_args()
#
prt     = args.prt			# print on|off
MYSQL   = args.MYSQL			# Use MySQL or SQLITE3
adddb   = args.adddb			# fi add to the database
filedb  = args.S3file			# SQLITE3 file name
flighta = args.fa			# FlightAware CSV file
flighto = args.os			# Open Sky CSV vile
print ("Options: MySQL ", MYSQL, "addDB", adddb, "FA ", flighta, "OS ", flighto)
# --------------------------------------#
if MYSQL:
    # open the DataBase
    conn = MySQLdb.connect(host=DBhost, user=DBuser, passwd=DBpasswd, db=DBname)
    print("MySQL: Database:", DBname, " at Host:", DBhost)
else:
    conn = sqlite3.connect(filedb)
    print("SQLITE3 file:", filedb)

cursA = conn.cursor()     		# set the cursor for aircraft
cursM = conn.cursor()     		# set the cursor for model
# --------------------------------------#


#----------------------genadsbreg.py start-----------------------#

mydict = create_dict()			# create the dictionary
cursA.execute("SELECT Aircraft.Icao as ICAO, Registration as REG, ModelID as MODEL  FROM Aircraft ;")
res=cursA.fetchall()			# get all the aircraft from the DB

counter=0				# counter of number of aircrafts seen
cntfa  =0				# counter of extra aircraft from FA
cntos  =0				# counter of extra aircraft from Open Sky
cntdb  =0				# counter of records added to the DDBB
dups   =0				# Duplicated entries
for row in res:
    if row[2] == None:			# if no model ???
        model="UNKW"
    else:				# get the model description from the model table
        cursM.execute("SELECT Icao FROM Model WHERE ModelID = "+str(row[2])+" ;")
        mod = cursM.fetchone()
        if mod == None:
            model = 'UNKW'
        else:
            model = mod[0]
        if model == None or model == '':
            model = 'UNKW'
    ICAO=row[0].upper()
    mydict.add(ICAO, ({"Reg": row[1], "Model": model}))
    counter += 1
    if counter %10000 == 0:
        print("Process DB:", counter, naive_utcnow().strftime("%y-%m-%d %H:%M:%S"))
print("Registrations from VRS from DDBB:", counter)
cntbasic=counter
cntdb=counter
# -----------------------------------------------------------------#
if flighta:				# if extra data from FlightAare
    if not os.path.exists(filefa):
        print("FlightAware data not available \n")
        exit(-1)
    lc=linecount_wc(filefa)
    print("\nAdding data from:", filefa, lc)
    pbar=tqdm(total=lc)
    with open(filefa, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            model = row['t']
            icao=row['icao24'].upper()
            reg =row['r']
            if model == None or model == '':
                model = 'UNKW'
                modelid = 0
            country=icao[0]
            if country == '3' or country == '4' or country == '5':
                if icao not in mydict:
                    mydict.add(icao, ({"Reg": reg, "Model": model}))  # add it to the dict
                    cntfa += 1
                else:
                    dups +=1
            counter += 1		# add that aircraft to the table
            if adddb:
                if model != 'UNKW': 	# try to get the modelID (number) from the model table
                    modelid = 0
                    cursM.execute("SELECT ModelID FROM Model WHERE Icao = '"+model+"';")
                    mod = cursM.fetchone()
                    if mod != None:
                        modelid=mod[0]
                sqlstm = "INSERT INTO Aircraft VALUES ("+str(counter)+",'"+icao+"','"+reg+"',"+str(modelid)+", 0, '"+tme+"');"
                cursA.execute(sqlstm)
                cntdb +=1

            if counter %100000 == 0:
                print("Process FA:", counter, cntfa, naive_utcnow().strftime("%y-%m-%d %H:%M:%S"), cntdb)
            pbar.update(1)
    pbar.close()
    conn.commit()			# commit the changes

print("\nRegistrations from FA:", cntfa, "dups:", dups, "DB:", cntdb)

if flighto:				# if extra data from FlightAare
    if not os.path.exists(fileos):
        print("\nGen data to:", fileos)
        os.system("cd utils && bash get_os_csv.sh")
    lc=linecount_wc(fileos)
    print("\nAdding data from:", fileos, lc)
    pbar=tqdm(total=lc)
    with open(fileos, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            #print ("PPP", row)
            counter += 1		# add that aircraft to the table
            modelid = 0
            icao=row['icao24'].upper()
            reg =row['registration']
            if icao == '' or reg == '':
                continue
            model    =row['model']
            if model == None or model == '':
                model = 'UNKW'
                modelid = 0
            oper =row['operator']
            if oper == None or oper =='':
               oper = 0
            oper = 0 			# patch until we implement the operator table
            country=icao[0]
            if country == '3' or country == '4' or country == '5':
                if icao not in mydict:
                    mydict.add(icao, ({"Reg": reg, "Model": model}))  # add it to the dict
                    cntos += 1
                else:
                    dups +=1
            counter += 1		# add that aircraft to the table
            if adddb:
                if model != 'UNKW': 	# try to get the modelID (number) from the model table
                    model=model.replace("'", " ").replace('"', ' ')
                    modelid = 0
                    try:
                       cursM.execute('SELECT ModelID FROM Model WHERE Icao = "'+model+'";')
                    except:
                       print ("MySQL error record: ", cntdb)
                       print ("SQL:", "SELECT ModelID FROM Model WHERE Icao = '"+model+"';")
                    mod = cursM.fetchone()
                    if mod != None:
                        modelid=mod[0]
                sqlstm = "INSERT INTO Aircraft VALUES ("+str(counter)+",'"+icao+"','"+reg+"','"+str(modelid)+"', '"+str(oper)+"', '"+tme+"');"
                #print ("SQL:", sqlstm)
                try:
                   cursA.execute(sqlstm)
                except:
                   print ("MySQL error record: ", cntdb)
                   print ("SQL:", sqlstm)
                cntdb +=1

            if counter %100000 == 0:
                print("Process OS:", counter, cntos, naive_utcnow().strftime("%y-%m-%d %H:%M:%S"), cntdb)
            pbar.update(1)
    pbar.close()
    conn.commit()			# commit the changes


print("\nRegistrations entries from OS:", cntos, "dups:", dups, "DB:", cntdb)


print("# Entries on dict: ", len(mydict))
#stud_json = json.dumps(mydict, indent=4, sort_keys=True)
stud_json = json.dumps(mydict)
#print(stud_json)
print ("Records added to the DDBB\n", cntdb)
print ("Generating the ADSBreg.py file\n")
fd=open("ADSBreg.py", "w")
fd.write("ADSBreg="+stud_json)
fd.close()
print("Size of ADSBreg file", len(stud_json), " Registrations generated DDBB: ", counter, "Basic:", cntbasic, "FA:", cntfa, "OS:", cntos, "DDBB:", cntdb, "\n")
conn.commit()
conn.close()
exit(0)
