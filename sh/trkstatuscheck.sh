#!/bin/bash
pid=$"/tmp/TRKS.pid"
pnum=$(pgrep -x -f "python3 /home/angel/src/APRSsrc/main/trkgetstatus.py")
if [ $? -eq 0 ]
then
        logger -t $0 "TRKSTATUS is running..."$pnum
else
        if [ -f $pid ] # if OGN repo interface is  not running
        then
              sudo kill $(cat /tmp/TRKS.pid)
        fi

        logger -t $0 "TRKSTATUS is restarting"
        bash ~/src/APRSsrc/sh/trkstatus.sh
fi

