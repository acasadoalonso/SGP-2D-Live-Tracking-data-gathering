#!/bin/bash
alive=$"/nfs/OGN/SWdata/APRS.alive"
if [ ! -f $alive ]
then
                logger  -t $0 "APRS Log is not alive"
                pnum=$(pgrep -x -f "python3 ~/src/APRSsrc/main/aprslog.py")
                if [ $? -eq 0 ] # if OGN repo interface is  not running
                then
                        sudo kill $pnum
                fi
#               restart OGN data collector
                bash ~/src/APRSsrc/main/sh/aprslog.sh 
                logger -t $0 "APRS Log seems down, restarting"
                echo $(date)" - "$(hostname)  >>/nfs/OGN/SWdata/.APRSrestart.log
else
                logger -t $0 "APRS Log is alive"
		rm $alive
fi

