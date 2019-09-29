#!/bin/sh
cd /nfs/OGN/SWdata
wget chileogn.ddns.net/files/TRKDEVICES.sql -o /tmp/TRKDEVICES.sql
if [ -f TRKDEVICES.sql ]
then
	echo "=============================================APRSLOG.============================================="    
       	echo "DELETE FROM TRKDEVICES ; "                       | mysql -v -u ogn -pogn  APRSLOG 		     
        sed "s/LOCK TABLES \`TRKDEVICES\`/-- LOCK TABLES/g" <TRKDEVICES.sql  | sed "s/UNLOCK TABLES;/-- UNLOCK TABLES/g" |  sed "s/\/*\!40000 /-- XXXX TABLES/g" | mysql -v -u ogn -pogn APRSLOG
	echo "=============================================SWIFACE.============================================="    
       	#echo "DELETE FROM TRKDEVICES ; "                       | mysql -v -u ogn -pogn  SWIFACE -h casadonfs 		     
        #sed "s/LOCK TABLES \`TRKDEVICES\`/-- LOCK TABLES/g" <TRKDEVICES.sql  | sed "s/UNLOCK TABLES;/-- UNLOCK TABLES/g" |  sed "s/\/*\!40000 /-- XXXX TABLES/g" | mysql -v -u ogn -pogn SWIFACE -h casadonfs
	#echo "select * FROM TRKDEVICES ; "                     | mysql -v -u ogn -pogn  SWIFACE -h casadonfs
	echo "=============================================GLIDERS.============================================="    
	echo "DELETE FROM APRSLOG.GLIDERS; " | mysql -v -u ogn -pogn -h UBUNTU 
	echo "INSERT INTO APRSLOG.GLIDERS SELECT * FROM OGNDB.GLIDERS; " | mysql -v -u ogn -pogn -h UBUNTU 
	echo "select count(*) from GLIDERS;" |    mysql -h UBUNTU -u ogn -pogn APRSLOG

	rm TRKDEVICES.sql
else
	/home/angel/perl5/bin/pt-table-sync  --execute --verbose h=chileogn.ddns.net,D=APRSLOG,t=TRKDEVICES h=localhost >>APRSproc.log 2>/dev/null	
fi
echo "Done."     		     						                                    
date														   

