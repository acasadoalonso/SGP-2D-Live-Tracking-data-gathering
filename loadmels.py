import json, requests
import config
import MySQLdb
from datetime import datetime


url = 'http://ognrange.onglide.com/perl/stations2.pl'

DBpath   =config.DBpath
DBhost   =config.DBhost
DBuser   =config.DBuser
DBpasswd =config.DBpasswd
DBname   =config.DBname
conn=MySQLdb.connect(host=DBhost, user=DBuser, passwd=DBpasswd, db=DBname)
curs=conn.cursor()                      # set the cursor

print "MySQL: Database:", DBname, " at Host:", DBhost

resp = requests.get(url=url)
data = json.loads(resp.text)
cout=0
#print data
#print json.dumps(data, indent=4, sort_keys=True)
stations=data['stations']
for station in stations:
	cc=station['s']
	latitude=station['lt']
	longitude=station['lg']
	otime=station['ut']
	altitude=0
	version=' '
	cpu=0
	temp=0
	rf=0
	status=' '
	if otime == ' ' or otime == '':
		continue

        inscmd="insert into RECEIVERS values ('%s', %f,  %f,  %f, '%s', '%s', %f, %f, '%s', '%s')" %\
                                         (cc, latitude, longitude, altitude, otime, version, cpu, temp, rf, status)
        print inscmd
	try:
                                        curs.execute(inscmd)
					cout +=1
        except MySQLdb.Error, e:
                                        try:
                                                print ">>>MySQL1 Error [%d]: %s" % (e.args[0], e.args[1])
                                        except IndexError:
                                                print ">>>MySQL2 Error: %s" % str(e)
                                        print ">>>MySQL3 error:",  inscmd
 
print ' DB records created: ',cout    # report number of records read and IDs discovered
conn.commit()                   # commit the DB updates
conn.close()                    # close the database
local_time = datetime.now() # report date and time now                                     
print local_time
