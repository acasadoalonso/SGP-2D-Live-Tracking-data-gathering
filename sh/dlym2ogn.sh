#!/bin/bash

if [ -z $CONFIGDIR ]
then 
     export CONFIGDIR=/etc/local/
fi
DBuser=$(echo    `grep '^DBuser '   $CONFIGDIR/APRSconfig.ini` | sed 's/=//g' | sed 's/^DBuser //g')
DBpasswd=$(echo  `grep '^DBpasswd ' $CONFIGDIR/APRSconfig.ini` | sed 's/=//g' | sed 's/^DBpasswd //g' | sed 's/ //g' )
DBpath=$(echo    `grep '^DBpath '   $CONFIGDIR/APRSconfig.ini` | sed 's/=//g' | sed 's/^DBpath //g' | sed 's/ //g' )

cd $DBpath
echo "========"$(hostname)"===============:"	>>dlym2ogn.log
date                            		>>dlym2ogn.log
python3 ~/src/APRSsrc/main/APRScalsunrisesunset.py >>dlym2ogn.log
echo "DLYM2OGN.sh:"	            		>>dlym2ogn.log
echo "===========:"     	       		>>dlym2ogn.log
python3 ~/src/APRSsrc/main/dlym2ogn.py -d 3    	>>dlym2ogn.log 2>>dlym2ognerr.log &
pgrep -a python3				>>dlym2ogn.log
date                            		>>dlym2ogn.log
cd
