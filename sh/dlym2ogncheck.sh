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
alive=$DBpath/DLYM2OGN.alive
pid=$(echo  `grep '^dlypid' $CONFIGDIR/APRSconfig.ini` | sed 's/=//g' | sed 's/^dlypid//g')

if [ ! -f $alive ]
then
                logger  -t $0 "DLYM2OGN Log is not alive"
                if [ -f $pid ] # if OGN repo interface is  not running
                then
                        sudo kill $(cat $pid)
                fi

#               restart OGN data collector
                bash $SCRIPTPATH/dlym2ogn.sh 
                logger -t $0 "DLYM2OGN Log seems down, restarting"
                echo $(date)" - "$(hostname)  >>$DBpath/.DLYMrestart.log
else
                if [ -f $pid ]
                then
                	logger -t $0 "DLYM2OGN Log is alive ... "$(cat $pid)" -- "$(cat $alive)
                else
                	logger -t $0 "DLYM2OGN Log is alive ...  -- "$(cat $alive)
                fi
		rm $alive
fi

