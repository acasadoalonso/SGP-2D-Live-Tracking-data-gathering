#!/bin/sh
server="localhost"
cd ~/src
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
date=$yea$mon$day
#echo $date
rsync -rl  ./APRSsrc /nfs/OGN/src/
sudo  rm   /var/www/html/node/nohup.out 									     >/dev/null 2>/dev/null
rsync -rl  /var/www/html/node /nfs/OGN/src/APRSsrc
cd /var/www/html/
mv cuc/*json cuc/archive	2>/dev/null
cd /nfs/OGN/src
cp libfap.py kglid.py *funcs.py ~/src/APRSsrc
cd /nfs/OGN/SWdata
date														     >>proc.log 2>/dev/null
sudo wget "http://localhost/node/heatmap.php" >/dev/null 2>/dev/null
rm heatmap*
echo "clean OGNDATA in APRSLOG"							                                     >>proc.log 2>/dev/null
echo "DELETE FROM RECEIVERS WHERE otime < date('"$(date +%Y-%m-%d)"')-2;" | mysql -v -u ogn -pogn -h $server APRSLOG >>proc.log 2>/dev/null
echo "INSERT INTO OGNDATAARCHIVE SELECT * FROM OGNDATA;      " | mysql -v -u ogn -pogn -h $server APRSLOG            >>proc.log 2>/dev/null
echo "DELETE FROM OGNDATAARCHIVE where date < '"$date"'; "     | mysql -v -u ogn -pogn -h $server APRSLOG            >>proc.log 2>/dev/null
echo "DELETE FROM OGNDATA;"                                    | mysql -v -u ogn -pogn -h $server APRSLOG            >>proc.log 2>/dev/null
echo "DELETE FROM GLIDERS ; "                                  | mysql -v -u ogn -pogn -h $server APRSLOG            >>proc.log 2>/dev/null
echo "INSERT INTO GLIDERS  SELECT * FROM OGNDB.GLIDERS;      " | mysql -v -u ogn -pogn -h $server APRSLOG            >>proc.log 2>/dev/null
date														     >>proc.log 2>/dev/null
echo "Done."     		     						                                     >>proc.log 2>/dev/null
mv proc.log  archive/PROC$(date +%y%m%d).log
mv aprs.log  archive/APRSlog$(date +%y%m%d).log
mv DATA*.log archive		2>/dev/null
mv APRS*.log archive  		2>/dev/null
rm APRS.alive  			2>/dev/null
cd
