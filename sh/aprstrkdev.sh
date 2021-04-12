#!/bin/sh
if [ $# = 0 ]; then
	server='localhost'
else
	server=$1
fi
echo "Server: "$server
if [ $# > 1 ]; then
	server2=$2
else
	server2='localhost'
fi
echo "Server2: "$server2
echo $# $2
hostname=$(hostname)


if [ -z $CONFIGDIR ]
then 
     export CONFIGDIR=/etc/local
fi
DBuser=$(echo    `grep '^DBuser '   $CONFIGDIR/APRSconfig.ini` | sed 's/=//g' | sed 's/^DBuser //g')
DBpasswd=$(echo  `grep '^DBpasswd ' $CONFIGDIR/APRSconfig.ini` | sed 's/=//g' | sed 's/^DBpasswd //g' | sed 's/ //g' )
DBpath=$(echo    `grep '^DBpath '   $CONFIGDIR/APRSconfig.ini` | sed 's/=//g' | sed 's/^DBpath //g' | sed 's/ //g' )

cd $DBpath
wget chileogn.ddns.net/files/TRKDEVICES.sql -o /tmp/TRKDEVICES.sql
if [ -f TRKDEVICES.sql ]
then
	echo "=============================================APRSLOG.============================================="    
       	echo "DELETE FROM TRKDEVICES ; "                       | mysql -u $DBuser -p$DBpasswd -v -h $server APRSLOG 		     
        sed "s/LOCK TABLES \`TRKDEVICES\`/-- LOCK TABLES/g" <TRKDEVICES.sql  | sed "s/UNLOCK TABLES;/-- UNLOCK TABLES/g" |  sed "s/\/*\!40000 /-- XXXX TABLES/g" | mysql -u $DBuser -p$DBpasswd -v -h $server APRSLOG
	echo "select count(*) from TRKDEVICES;" |    mysql -u $DBuser -p$DBpasswd -h $server APRSLOG
	#echo "=============================================SWIFACE.============================================="    
       	#echo "DELETE FROM TRKDEVICES ; "                       | mysql -u $DBuser -p$DBpasswd -v SWIFACE -h $server2 		     
        #sed "s/LOCK TABLES \`TRKDEVICES\`/-- LOCK TABLES/g" <TRKDEVICES.sql  | sed "s/UNLOCK TABLES;/-- UNLOCK TABLES/g" |  sed "s/\/*\!40000 /-- XXXX TABLES/g" | mysql -u $DBuser -p$DBpasswd -v SWIFACE -h casadonfs
	#echo "select * FROM TRKDEVICES ; "                     | mysql -u $DBuser -p$DBpasswd -v SWIFACE -h $server2
	echo "=============================================GLIDERS.============================================="    
	echo "DELETE FROM APRSLOG.GLIDERS; " | mysql -u $DBuser -p$DBpasswd -v -h $server 
	echo "INSERT INTO APRSLOG.GLIDERS SELECT * FROM OGNDB.GLIDERS; " | mysql -u $DBuser -p$DBpasswd -v -h $server 
	echo "select count(*) from GLIDERS;" |    mysql -u $DBuser -p$DBpasswd -h $server APRSLOG

	rm TRKDEVICES.sql
else
	pt-table-sync  --execute --verbose h=chileogn.ddns.net,D=APRSLOG,t=TRKDEVICES h=$server --user=$DBuser --password=$DBpasswd >>APRSproc.log 2>/dev/null	
fi
echo "Done."     		     						                                    
date														   

