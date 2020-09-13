#!/bash/sh
if [ $# = 0 ]; then
	server='localhost'
else
	server=$1
fi
echo "Server: "$server
hostname=$(hostname)

if [ -d /var/www/html/files ]
then
	mysqldump --login-path=SARogn -h $server --add-drop-table APRSLOG GLIDERS  >/var/www/html/files/GLIDERS.sql     2>/dev/null
	mysqldump --login-path=SARogn -h $server --add-drop-table OGNDB   STATIONS >/var/www/html/files/STATIONS.sql    2>/dev/null
	echo ".dump GLIDERS" | sqlite3 /nfs/OGN/DIRdata/SAROGN.db                  >/var/www/html/files/GLIDERS.dump    2>/dev/null
	ls -lart                                                                    /var/www/html/files/									
fi
mysql --login-path=SARsql -h $server -e "select count(*) from OGNTRKSTATUS" APRSLOG
mysql --login-path=SARsql -h $server -e "delete          from OGNTRKSTATUS" APRSLOG
