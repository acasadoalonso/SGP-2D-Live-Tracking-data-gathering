#!/bin/bash
alive=$"/nfs/OGN/SWdata/DLYM2OGN.alive"
if [ ! -f $alive ]
then
                logger  -t $0 "DLYM2OGN Log is not alive"
                pnum=$(pgrep -x -f "python3 ~/src/APRSsrc/main/dlym2ogn.py")
                if [ $? -eq 0 ] # if OGN repo interface is  not running
                then
                        sudo kill $pnum
                fi
#               restart OGN data collector
                bash ~/src/APRSsrc/main/sh/dlym2ogn.sh 
                logger -t $0 "DLYM2OGN Log seems down, restarting"
                echo $(date)" - "$(hostname)  >>/nfs/OGN/SWdata/.DLYMrestart.log
else
                logger -t $0 "DLYM2OGN Log is alive"
		rm $alive
fi

