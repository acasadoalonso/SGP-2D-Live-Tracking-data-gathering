#!/bin/bash
cd /nfs/OGN/SWdata 
#python /home/angel/src/APRSsrc/aprslog.py RECV >>aprs.log &
python /home/angel/src/APRSsrc/aprslog.py       >>aprs.log &
pgrep -a python
cd
