#!/bin/sh
cd /nfs/OGN/SWdata
date														     >>APRSproc.log 2>/dev/null
if [ $# = 0 ]; then
	server='localhost'
else
	server=$1
fi
echo "Server: "$server                                                                                               >>APRSproc.log 
hostname=$(hostname)
cd ~/src/APRSsrc
day=$(date +%d)
mon=$(date +%m)
yea=$(date +%y)
if   [ $day = "08" ]; then
	day="07"
elif [ $day = "09" ]; then
        day="08"
elif [ $day = "10" ]; then
	day="09"
else
	let "day = $day - 1"
fi
if [   $day = "7" ]; then
	day="07"
elif [ $day = "6" ]; then
	day="06"
elif [ $day = "5" ]; then
        day="05"
elif [ $day = "4" ]; then
        day="04"
elif [ $day = "3" ]; then
        day="03"
elif [ $day = "2" ]; then
        day="02"
elif [ $day = "1" ]; then
        day="01"
fi

date=$yea$mon$day
#echo $date
cd /var/www/html/
mv cuc/*json cuc/archive	2>/dev/null
mv cuc/*tsk  cuc/archive	2>/dev/null
mv cuc/*lst  cuc/archive	2>/dev/null
mv cuc/*csv  cuc/archive	2>/dev/null
cd /var/www/html/SWS
mv cuc/*json cuc/archive	2>/dev/null
mv cuc/*tsk  cuc/archive	2>/dev/null
mv cuc/*lst  cuc/archive	2>/dev/null
cd /nfs/OGN/SWdata
date														     >>APRSproc.log 2>/dev/null
echo "Gen the heatmaps files from: "$hostname					                                     >>APRSproc.log 2>/dev/null
sudo wget "http://localhost/node/heatmap.php" -o /tmp/tempfile 							     >/dev/null     2>/dev/null
sudo rm /tmp/tempfile* heatmap.php.*  										     >/dev/null     2>/dev/null
date														     >>APRSproc.log 2>/dev/null
echo "clean OGNDATA in APRSLOG"							                                     >>APRSproc.log 2>/dev/null
echo "DELETE FROM RECEIVERS WHERE otime < date('"$(date +%Y-%m-%d)"')-3;" | mysql --login-path=SARogn -v -h $server APRSLOG >>APRSproc.log 2>/dev/null
echo "INSERT INTO OGNDATAARCHIVE SELECT * FROM OGNDATA;      " | mysql --login-path=SARogn -v -h $server APRSLOG     >>APRSproc.log 2>/dev/null
echo "DELETE FROM OGNDATAARCHIVE where date < '"$date"'; "     | mysql --login-path=SARogn -v -h $server APRSLOG     >>APRSproc.log 2>/dev/null
echo "DELETE FROM OGNTRKSTATUS WHERE otime < date('"$(date +%Y-%m-%d)"'); " | mysql --login-path=SARogn -v -h $server APRSLOG >>APRSproc.log 2>/dev/null
echo "SELECT COUNT(*) from OGNTRKSTATUS  ; "                   | mysql --login-path=SARogn -v -h $server APRSLOG     >>APRSproc.log 2>/dev/null
echo "DELETE FROM OGNDATA;"                                    | mysql --login-path=SARogn -v -h $server APRSLOG     >>APRSproc.log 2>/dev/null
echo "DELETE FROM GLIDERS ; "                                  | mysql --login-path=SARogn -v -h $server APRSLOG     >>APRSproc.log 2>/dev/null
echo "INSERT INTO GLIDERS  SELECT * FROM OGNDB.GLIDERS;      " | mysql --login-path=SARogn    -h $server APRSLOG     >>APRSproc.log 2>/dev/null
echo "SELECT COUNT(*) from GLIDERS  ; "                        | mysql --login-path=SARogn -v -h $server APRSLOG     >>APRSproc.log 2>/dev/null
echo "Report number of GLIDERS with the LAST FIX POSITION"			                                     >>APRSproc.log 2>/dev/null
echo "SELECT COUNT(*) from GLIDERS_POSITIONS   ; "             | mysql --login-path=SARogn -v -h $server APRSLOG     >>APRSproc.log 2>/dev/null
echo "DELETE from GLIDERS_POSITIONS WHERE length(flarmId) < 6;"| mysql --login-path=SARogn -v -h $server APRSLOG     >>APRSproc.log 2>/dev/null
echo "DELETE from GLIDERS_POSITIONS WHERE flarmId like '%RND%' ;"| mysql --login-path=SARogn -v -h $server APRSLOG   >>APRSproc.log 2>/dev/null
echo "SELECT COUNT(*) from GLIDERS_POSITIONS   ; "             | mysql --login-path=SARogn -v -h $server APRSLOG     >>APRSproc.log 2>/dev/null
date														     >>APRSproc.log 2>/dev/null
if [ -d /var/www/html/files ]
then
	mysqldump --login-path=SARogn -h $server --add-drop-table APRSLOG GLIDERS  >/var/www/html/files/GLIDERS.sql  2>/dev/null
	mysqldump --login-path=SARogn -h $server --add-drop-table OGNDB   STATIONS >/var/www/html/files/STATIONS.sql 2>/dev/null
	echo ".dump GLIDERS" | sqlite3 /nfs/OGN/DIRdata/SAROGN.db                  >/var/www/html/files/GLIDERS.dump 2>/dev/null
	ls -la /var/www/html/files/										     >>APRSproc.log 2>/dev/null
fi
if [[ $(hostname) == 'CHILEOGN' ]]
then
   mysqldump --login-path=SARogn -h $server --add-drop-table APRSLOG TRKDEVICES  >/var/www/html/files/TRKDEVICES.sql 2>/dev/null
else
   if [[ -f TRKDEVICES.sql ]]
   then
      rm TRKDEVICES.sql												     >/dev/null 2>/dev/null
   fi
   wget chileogn.ddns.net/files/TRKDEVICES.sql -o /tmp/TRKDEVICES.sql						     >/dev/null 2>/dev/null
fi
if [[ -f TRKDEVICES.sql && $(hostname) != 'CHILEOGN' ]]
then
       	echo "DELETE FROM TRKDEVICES ; "                       | mysql --login-path=SARogn -v APRSLOG 		     >>APRSproc.log 2>/dev/null           
        sed "s/LOCK TABLES \`TRKDEVICES\`/-- LOCK TABLES/g" <TRKDEVICES.sql  | sed "s/UNLOCK TABLES;/-- UNLOCK TABLES/g" |  sed "s/\/*\!40000 /-- XXXX TABLES/g" | mysql --login-path=SARogn -v APRSLOG		     >>APRSproc.log 2>/dev/null
	echo "select * FROM TRKDEVICES ; "                     | mysql --login-path=SARogn -v APRSLOG        	     >>APRSproc.log 2>/dev/null

	rm /tmp/TRKDEVICES.sql
else
        pt-table-sync  --execute --verbose h=chileogn.ddns.net,D=APRSLOG,t=TRKDEVICES h=$server 		     >>APRSproc.log 2>/dev/null
fi
echo "Done."     		     						                                     >>APRSproc.log 2>/dev/null
date														     >>APRSproc.log 2>/dev/null
mutt -a APRSproc.log -s $hostname" APRSlog daily report ..." -- $(cat ~/src/APRSsrc/sh/mailnames.txt)
mv APRSproc.log  archive/APRSPROC$(date +%y%m%d).log 								     2>/dev/null
mv aprs.log  archive/APRSlog$(date +%y%m%d).log      								     2>/dev/null
mv DATA*.log archive												     2>/dev/null
mv APRS*.log archive  												     2>/dev/null
rm APRS.alive  													     2>/dev/null
cd ~/src/APRSsrc
sudo  rm   /var/www/html/node/nohup.out	     							    		     >/dev/null 2>/dev/null
cd

