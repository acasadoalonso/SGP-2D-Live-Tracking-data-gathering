#!/bin/bash
if [ $# = 0 ]; then
	server='mariadb'
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

echo "select count(*) from GLIDERS;" |    				mysql -u $DBuser -p$DBpasswd -v -h $server APRSLOG
echo "DELETE FROM APRSLOG.GLIDERS; " |                            	mysql -u $DBuser -p$DBpasswd -v -h $server 
echo "INSERT INTO APRSLOG.GLIDERS SELECT * FROM OGNDB.GLIDERS; " | 	mysql -u $DBuser -p$DBpasswd -v -h $server 
echo "SELECT COUNT(*) FROM APRSLOG.GLIDERS;" |                     	mysql -u $DBuser -p$DBpasswd -v -h $server 
