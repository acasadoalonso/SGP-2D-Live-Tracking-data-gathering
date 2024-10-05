#!/bin/bash
if [ -z $CONFIGDIR ]
then
     export CONFIGDIR=/etc/local/
fi
DBuser=$(echo    `grep '^DBuser '   $CONFIGDIR/APRSconfig.ini` | sed 's/=//g' | sed 's/^DBuser //g')
DBpasswd=$(echo  `grep '^DBpasswd ' $CONFIGDIR/APRSconfig.ini` | sed 's/=//g' | sed 's/^DBpasswd //g' | sed 's/ //g' )
DBpath=$(echo    `grep '^DBpath '   $CONFIGDIR/APRSconfig.ini` | sed 's/=//g' | sed 's/^DBpath //g' | sed 's/ //g' )
SCRIPT=$(readlink -f $0)
SCRIPTPATH=`dirname $SCRIPT`

alive=$DBpath"APRS"$(hostname)".alive"
pid=$(echo  `grep '^pid' $CONFIGDIR/APRSconfig.ini` | sed 's/=//g' | sed 's/^pid//g')
echo $pid $alive
hn=$(hostname)
cd /nfs/OGN/APRSdata/$hn
pwd
logger  -t $0 "APRS Log daily cleaninng files"
if [ -f $pid ] # if APRSlog
then
	pnum=$(cat $pid)
        sudo kill -9 $pnum
        rm $pid 2>/dev/null
fi
ls -la
sudo rm aprs.log	2>/dev/null
sudo rm aprserr.log	2>/dev/null
sudo rm APRS.sunset	2>/dev/null
sudo rm $alive 		2>/dev/null
sudo rm $pid 		2>/dev/null

ls -la
