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
if [ ! -f $alive ]
then
                logger  -t $0 "APRS Log is not alive"
                if [ -f $pid ] # if OGN repo interface is  not running
                then
			pnum=$(cat $pid)
                        sudo kill $pnum 
                        rm $pid 2>/dev/null
                fi
#               restart OGN data collector
                bash $SCRIPTPATH/aprslog.sh 
                echo $(date)" - "$(hostname)  >>$DBpath.APRSrestart.log
                sleep 10
                if [ -f $pid ] # if we have PID file
                then
                   logger -t $0 "APRS Log seems down, restarting: "$(cat $pid)
                else
                   logger -t $0 "APRS Log seems down, restarting, no PID yet "
                fi
else
		if [ ! -f $pid ]
		then
                	logger -t $0 "APRS NOPID yet Log is alive Process: "$alive
		else
                        pnum=$(pgrep -F $pid)
                        if [ $? -ne 0 ] # if aprsc is  not running
		        then
                           bash $SCRIPTPATH/aprslog.sh
                           echo $(date)" - "$(hostname)  >>$DBpath.APRSrestart.log
                           logger -t $0 "APRS Log seems down, restarting: old PID "$(cat $pid)
                        else 
                	   logger -t $0 "APRS Log is alive Process: "$(cat $pid)" "$alive
		        fi
		fi
		rm $alive 2>/dev/null
fi

