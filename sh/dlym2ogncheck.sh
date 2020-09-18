#!/bin/bash
alive=$"/nfs/OGN/SWdata/DLYM2OGN.alive"
pid=$"/tmp/DLY.pid"
if [ ! -f $alive ]
then
                logger  -t $0 "DLYM2OGN Log is not alive"
                if [ -f $pid ] # if OGN repo interface is  not running
                then
                        sudo kill $(cat /tmp/DLY.pid)
                fi

#               restart OGN data collector
                bash ~/src/APRSsrc/main/sh/dlym2ogn.sh 
                logger -t $0 "DLYM2OGN Log seems down, restarting"
                echo $(date)" - "$(hostname)  >>/nfs/OGN/SWdata/.DLYMrestart.log
else
                logger -t $0 "DLYM2OGN Log is alive"
		rm $alive
fi

