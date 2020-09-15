#!/bin/bash
alive=$"/nfs/OGN/SWdata/APRS.alive"
pid=$"/tmp/aprs.pid"
if [ ! -f $alive ]
then
                logger  -t $0 "APRS Log is not alive"
                if [ -f $pid ] # if OGN repo interface is  not running
                then
                        sudo kill $(cat /tmp/aprs.pid)
                fi
#               restart OGN data collector
                bash ~/src/APRSsrc/main/sh/aprslog.sh 
                logger -t $0 "APRS Log seems down, restarting"
                echo $(date)" - "$(hostname)  >>/nfs/OGN/SWdata/.APRSrestart.log
else
                logger -t $0 "APRS Log is alive"
		rm $alive
fi

