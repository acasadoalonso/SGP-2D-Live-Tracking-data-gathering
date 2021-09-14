#!/bash/sh
if [ $# = 0 ]; then
	server='localhost'
else
	server=$1
fi
echo "Server: "$server
hostname=$(hostname)

if [ -z $CONFIGDIR ]
then 
     export CONFIGDIR=/etc/local/
fi
DBuser=$(echo    `grep '^DBuser '   $CONFIGDIR/APRSconfig.ini` | sed 's/=//g' | sed 's/^DBuser //g')
DBpasswd=$(echo  `grep '^DBpasswd ' $CONFIGDIR/APRSconfig.ini` | sed 's/=//g' | sed 's/^DBpasswd //g' | sed 's/ //g' )
DBpath=$(echo    `grep '^DBpath '   $CONFIGDIR/APRSconfig.ini` | sed 's/=//g' | sed 's/^DBpath //g' | sed 's/ //g' )

cd $DBpath

if [ -d /var/www/html/files ]
then
	mysqldump -u $DBuser -p$DBpasswd -h $server --add-drop-table APRSLOG GLIDERS  >/var/www/html/files/GLIDERS.sql     2>/dev/null
	mysqldump -u $DBuser -p$DBpasswd -h $server --add-drop-table OGNDB   STATIONS >/var/www/html/files/STATIONS.sql    2>/dev/null
	echo ".dump GLIDERS" | sqlite3 $DBpath/SAROGN.db                              >/var/www/html/files/GLIDERS.dump    2>/dev/null
	ls -lart                                                                    /var/www/html/files/									
fi
mysql -u $DBuser -p$DBpasswd -h $server -e "select count(*) from OGNTRKSTATUS" APRSLOG
mysql -u $DBuser -p$DBpasswd -h $server -e "delete          from OGNTRKSTATUS" APRSLOG
