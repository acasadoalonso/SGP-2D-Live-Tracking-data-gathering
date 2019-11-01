#!/bin/sh
server="localhost"
server2="casadonfs"
hostname=$(hostname)

cd /nfs/OGN/SWdata
wget chileogn.ddns.net/files/TRKDEVICES.sql -o /tmp/TRKDEVICES.sql
if [ -f TRKDEVICES.sql ]
then
	echo "=============================================APRSLOG.============================================="    
       	echo "DELETE FROM TRKDEVICES ; "                       | mysql -v -u ogn -pogn  -h $server APRSLOG 		     
        sed "s/LOCK TABLES \`TRKDEVICES\`/-- LOCK TABLES/g" <TRKDEVICES.sql  | sed "s/UNLOCK TABLES;/-- UNLOCK TABLES/g" |  sed "s/\/*\!40000 /-- XXXX TABLES/g" | mysql -v -u ogn -pogn APRSLOG
	echo "=============================================SWIFACE.============================================="    
       	#echo "DELETE FROM TRKDEVICES ; "                       | mysql -v -u ogn -pogn  SWIFACE -h $server2 		     
        #sed "s/LOCK TABLES \`TRKDEVICES\`/-- LOCK TABLES/g" <TRKDEVICES.sql  | sed "s/UNLOCK TABLES;/-- UNLOCK TABLES/g" |  sed "s/\/*\!40000 /-- XXXX TABLES/g" | mysql -v -u ogn -pogn SWIFACE -h casadonfs
	#echo "select * FROM TRKDEVICES ; "                     | mysql -v -u ogn -pogn  SWIFACE -h $server2
	echo "=============================================GLIDERS.============================================="    
	echo "DELETE FROM APRSLOG.GLIDERS; " | mysql -v -u ogn -pogn -h $server 
	echo "INSERT INTO APRSLOG.GLIDERS SELECT * FROM OGNDB.GLIDERS; " | mysql -v -u ogn -pogn -h $server 
	echo "select count(*) from GLIDERS;" |    mysql -h $server -u ogn -pogn APRSLOG

	rm TRKDEVICES.sql
else
	/home/angel/perl5/bin/pt-table-sync  --execute --verbose h=chileogn.ddns.net,D=APRSLOG,t=TRKDEVICES h=localhost >>APRSproc.log 2>/dev/null	
fi
echo "Done."     		     						                                    
date														   

