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

cd /nfs/OGN/SWdata
wget chileogn.ddns.net/files/TRKDEVICES.sql -o /tmp/TRKDEVICES.sql
if [ -f TRKDEVICES.sql ]
then
	echo "=============================================APRSLOG.============================================="    
       	echo "DELETE FROM TRKDEVICES ; "                       | mysql --login-path=SARogn -v -h $server APRSLOG 		     
        sed "s/LOCK TABLES \`TRKDEVICES\`/-- LOCK TABLES/g" <TRKDEVICES.sql  | sed "s/UNLOCK TABLES;/-- UNLOCK TABLES/g" |  sed "s/\/*\!40000 /-- XXXX TABLES/g" | mysql --login-path=SARogn -v -h $server APRSLOG
	echo "select count(*) from TRKDEVICES;" |    mysql --login-path=SARogn -h $server APRSLOG
	#echo "=============================================SWIFACE.============================================="    
       	#echo "DELETE FROM TRKDEVICES ; "                       | mysql --login-path=SARogn -v SWIFACE -h $server2 		     
        #sed "s/LOCK TABLES \`TRKDEVICES\`/-- LOCK TABLES/g" <TRKDEVICES.sql  | sed "s/UNLOCK TABLES;/-- UNLOCK TABLES/g" |  sed "s/\/*\!40000 /-- XXXX TABLES/g" | mysql --login-path=SARogn -v SWIFACE -h casadonfs
	#echo "select * FROM TRKDEVICES ; "                     | mysql --login-path=SARogn -v SWIFACE -h $server2
	echo "=============================================GLIDERS.============================================="    
	echo "DELETE FROM APRSLOG.GLIDERS; " | mysql --login-path=SARogn -v -h $server 
	echo "INSERT INTO APRSLOG.GLIDERS SELECT * FROM OGNDB.GLIDERS; " | mysql --login-path=SARogn -v -h $server 
	echo "select count(*) from GLIDERS;" |    mysql --login-path=SARogn -h $server APRSLOG

	rm TRKDEVICES.sql
else
	~/perl5/bin/pt-table-sync  --execute --verbose h=chileogn.ddns.net,D=APRSLOG,t=TRKDEVICES h=$server >>APRSproc.log 2>/dev/null	
fi
echo "Done."     		     						                                    
date														   

