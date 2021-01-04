#!/bin/bash
alive=$"/nfs/OGN/SWdata/APRS"$(hostname)".alive"
pid=$"/tmp/aprs.pid"
pid=$(echo  `grep '^pid' /etc/local/APRSconfig.ini` | sed 's/=//g' | sed 's/^pid//g')
if [ ! -f $alive ]
then
                logger  -t $0 "APRS Log is not alive"
                if [ -f $pid ] # if OGN repo interface is  not running
                then
			pnum=$(cat $pid)
                        sudo kill $pnum 
                        rm $pid
                fi
#               restart OGN data collector
                bash ~/src/APRSsrc/main/sh/aprslog.sh 
                echo $(date)" - "$(hostname)  >>/nfs/OGN/SWdata/.APRSrestart.log
                sleep 10
                if [ -f $pid ] # if we have PID file
                then
                   logger -t $0 "APRS Log seems down, restarting: "$(cat $pid)
                else
                   logger -t $0 "APRS Log seems down, restarting, no PID yet "
                fi
else
                logger -t $0 "APRS Log is alive Process: "$(cat $pid)" "$alive
		rm $alive
fi

