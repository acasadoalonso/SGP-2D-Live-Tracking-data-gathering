#!/bin/sh
if [ $# = 0 ]; then
	server='localhost'
else
	server=$1
fi
hostname=$(hostname)
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

if [ -z $CONFIGDIR ]
then 
     export CONFIGDIR=/etc/local/
fi
DBuser=$(echo    `grep '^DBuser '   $CONFIGDIR/APRSconfig.ini` | sed 's/=//g' | sed 's/^DBuser //g')
DBpasswd=$(echo  `grep '^DBpasswd ' $CONFIGDIR/APRSconfig.ini` | sed 's/=//g' | sed 's/^DBpasswd //g' | sed 's/ //g' )
DBpath=$(echo    `grep '^DBpath '   $CONFIGDIR/APRSconfig.ini` | sed 's/=//g' | sed 's/^DBpath //g' | sed 's/ //g' )
SCRIPT=$(readlink -f $0)
SCRIPTPATH=`dirname $SCRIPT`

cd $DBpath
date														         >>DLYM.log 2>/dev/null
echo "Server: "$server                                                                                                   >>DLYM.log 
date													                 >>DLYM.log 2>/dev/null
echo "clean OGNDATA in APRSLOG"				  			                                         >>DLYM.log 2>/dev/null
echo "SELECT COUNT(*) from OGNTRKSTATUS  ; "                        | mysql -u $DBuser -p$DBpasswd -v -h $server APRSLOG >>DLYM.log 2>/dev/null
echo "DELETE FROM OGNTRKSTATUS WHERE otime < date('"$(date +%Y-%m-%d)"'); " | mysql -u $DBuser -p$DBpasswd -v -h $server APRSLOG >>DLYM.log 2>/dev/null
echo "SELECT COUNT(*) from OGNTRKSTATUS  ; "                        | mysql -u $DBuser -p$DBpasswd -v -h $server APRSLOG >>DLYM.log 2>/dev/null
date														     >>DLYM.log 2>/dev/null
wget chileogn.ddns.net/files/TRKDEVICES.sql -o /tmp/TRKDEVICES.sql
if [[ -f TRKDEVICES.sql && $(hostname) != 'CHILEOGN' ]]
then
       	echo "DELETE FROM TRKDEVICES ; "                       | mysql -u $DBuser -p$DBpasswd -v APRSLOG 		     >>DLYM.log 2>/dev/null           
        sed "s/LOCK TABLES \`TRKDEVICES\`/-- LOCK TABLES/g" <TRKDEVICES.sql  | sed "s/UNLOCK TABLES;/-- UNLOCK TABLES/g" |  sed "s/\/*\!40000 /-- XXXX TABLES/g" | mysql -u $DBuser -p$DBpasswd -v APRSLOG		     >>DLYM.log 2>/dev/null
	echo "select * FROM TRKDEVICES ; "                     | mysql -u $DBuser -p$DBpasswd -v APRSLOG        	     >>DLYM.log 2>/dev/null

	rm TRKDEVICES.sql
else
        pt-table-sync  --execute --verbose h=chileogn.ddns.net,D=APRSLOG,t=TRKDEVICES h=$server --user=$DBuser --password=$DBpasswd >>DLYM.log 2>/dev/null
fi
rm /tmp/TRKDEVICES.sql >/dev/null 2>/dev/null
echo "Done."     		     						                                     >>DLYM.log 2>/dev/null
date														     >>DLYM.log 2>/dev/null
mutt -a DLYM.log -s $hostname" DLYM daily report ..." -- $(cat SCRIPTPATH/mailnames.txt)
mv DLYM.log  archive/DLYMPROC$(date +%y%m%d).log 	2>/dev/null
mv dlym2ogn.log  archive/DLYMlog$(date +%y%m%d).log    	2>/dev/null
mv dlym2ognerr.log  archive/DLYMlogerr$(date +%y%m%d).log    	2>/dev/null
mv DLYM*.log archive					2>/dev/null
rm DLYM2LOG.alive  					2>/dev/null
cd

