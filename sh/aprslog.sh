#!/bin/bash

if [ -z $CONFIGDIR ]
then 
     export CONFIGDIR=/etc/local/
fi
DBuser=$(echo    `grep '^DBuser '   $CONFIGDIR/APRSconfig.ini` | sed 's/=//g' | sed 's/^DBuser //g')
DBpasswd=$(echo  `grep '^DBpasswd ' $CONFIGDIR/APRSconfig.ini` | sed 's/=//g' | sed 's/^DBpasswd //g' | sed 's/ //g' )
DBpath=$(echo  `grep '^DBpath ' $CONFIGDIR/APRSconfig.ini` | sed 's/=//g' | sed 's/^DBpath //g' | sed 's/ //g' )

SCRIPT=$(readlink -f $0)
SCRIPTPATH=`dirname $SCRIPT`
if [ $# = 0 ]; then
	param='param'
else
	param=$1
fi

if [ -f $SCRIPTPATH/$param ]
then
   param=$(cat $SCRIPTPATH/$param)
else
   param=''
fi

cd $DBpath
echo "========"$(hostname)"===============:"	>>aprs.log
echo 'Parameters for aprslog.py: '$param	>>aprs.log
date                            		>>aprs.log
python3 $SCRIPTPATH/../APRScalsunrisesunset.py  >>aprs.log
echo "APRSLIVE.sh: "$(hostname)        		>>aprs.log
echo "========================:"       		>>aprs.log
python3 $SCRIPTPATH/../aprslog.py $param 	>>aprs.log 2>>aprserr.log &
pgrep -a python3				>>aprs.log
cd
