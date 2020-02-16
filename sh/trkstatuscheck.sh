#!/bin/bash
pnum=$(pgrep -x -f "python3 /home/angel/src/APRSsrc/main/trkgetstatus.py")
if [ $? -eq 0 ]
then
        logger -t $0 "TRKSTATUS is running..."$p1
else
        logger -t $0 "TRKSTATUS is restarting"
        bash ~/src/APRSsrc/sh/trkstatus.sh
fi

