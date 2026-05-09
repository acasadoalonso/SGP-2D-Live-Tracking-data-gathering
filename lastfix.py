import MySQLdb
import json
import config
dbname='APRSLOG'
dbuser=config.DBuser
dbpass=config.DBpasswd
dbhost=config.DBhost
dbhost="UBU2SQL"
dbconn=MySQLdb.connect(
    database=dbname, user=dbuser, password=dbpass, host=dbhost)
query = "select flarmid, lat, lon, altitude, date, time, station from GLIDERS_POSITIONS order by flarmid;"
with dbconn.cursor(MySQLdb.cursors.DictCursor) as cursor:
    cursor.execute(query)
    data = cursor.fetchall()
#print (json.dumps(data,indent=4))

with open("data_lastfix.json", "w") as write_file:
    json.dump(data, write_file)
print("Number of devices:", len(data))
