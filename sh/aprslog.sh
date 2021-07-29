#!/bin/bash

if [ -z $CONFIGDIR ]
then 
     export CONFIGDIR=/etc/local/
fi
DBuser=$(echo    `grep '^DBuser '   $CONFIGDIR/APRSconfig.ini` | sed 's/=//g' | sed 's/^DBuser //g')
DBpasswd=$(echo  `grep '^DBpasswd ' $CONFIGDIR/APRSconfig.ini` | sed 's/=//g' | sed 's/^DBpasswd //g' | sed 's/ //g' )
DBpath=$(echo  `grep '^DBpath ' $CONFIGDIR/APRSconfig.ini` | sed 's/=//g' | sed 's/^DBpath //g' | sed 's/ //g' )
cd $DBpath
echo "========"$(hostname)"===============:"	>>aprs.log
date                            		>>aprs.log
python3 ~/src/APRSsrc/main/APRScalsunrisesunset.py >>aprs.log
echo "APRSLIVE.sh:"	            		>>aprs.log
echo "===========:"     	       		>>aprs.log
#python3 ~/src/APRSsrc/main/aprslog.py --LASTFIX True --MEM True --STATIONS True >>aprs.log 2>>aprserr.log &
python3 ~/src/APRSsrc/main/aprslog.py --MEM True --STATIONS True --LASTFIX True >>aprs.log 2>>aprserr.log &
pgrep -a python3				>>aprs.log
cd
