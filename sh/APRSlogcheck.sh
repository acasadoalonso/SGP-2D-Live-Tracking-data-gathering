#!/bin/bash
alive=$"/nfs/OGN/SWdata/APRS.alive"
#pid=$"/tmp/aprs.pid"
pid=$(echo  `grep '^pid' /etc/local/APRSconfig.ini` | sed 's/=//g' | sed 's/^pid//g')
if [ ! -f $alive ]
then
                logger  -t $0 "APRS Log is not alive"
                if [ -f $pid ] # if OGN repo interface is  not running
                then
                        pnum=$(cat $pid)
                        sudo $pnum 
                fi
#               restart OGN data collector
                bash ~/src/APRSsrc/main/sh/APRSlog.sh 
                logger -t $0 "APRS Log seems down, restarting"
                echo $(date)" - "$(hostname)  >>/nfs/OGN/SWdata/.APRSrestart.log
else
                logger -t $0 "APRS Log is alive"
		rm $alive
fi

