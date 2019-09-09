#!/usr/bin/python3
#

from datetime import datetime
from datetime import timedelta
import time
import sys
import os
import MySQLdb                              # the SQL data base routines^M
print("Start availability V1.0")
print("========================")
import config
DBhost = config.DBhost
DBuser = config.DBuser
DBpasswd = config.DBpasswd
DBname = config.DBname
# --------------------------------------#
conn = MySQLdb.connect(host=DBhost, user=DBuser, passwd=DBpasswd, db=DBname)
curs = conn.cursor()                      # set the cursor
date = datetime.utcnow()         # get the date
dte = date.strftime("%y%m%d")             # today's date

#----------------------avail.py start-----------------------

stareq = sys.argv[1:]
if stareq:
    station = stareq[0]
else:
    exit(-1)

try:

    inscmd = "select * from RECEIVERS where idrec = '" + \
        station+"' order by `otime` desc ;"
    #print inscmd
    try:
        curs.execute(inscmd)
    except MySQLdb.Error as e:
        try:
            print(">>>MySQL1 Error [%d]: %s" % (e.args[0], e.args[1]))
        except IndexError:
            print(">>>MySQL2 Error: %s" % str(e))
            print(">>>MySQL3 error:",  cout, inscmd)
            print(">>>MySQL4 data :",  data)
        exit(-1)
    row = curs.fetchone()
    if row == None:
        print("Not found")
        exit(-1)
    sta = row[0]
    otime = row[4]
    date = datetime.utcnow()
    diff = date-otime
    # status=row[9]
    print("T==>",  sta, otime, date, diff)
    if diff.seconds > 300:
        print("Not OK")
    else:
        print("OK")

except KeyboardInterrupt:
    print("Keyboard input received, ignore")
    pass

print("Exit now ...")
exit(1)
