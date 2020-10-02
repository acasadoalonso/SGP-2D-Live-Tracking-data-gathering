#!/bin/bash
cd /nfs/OGN/SWdata 
echo "========"$(hostname)"===============:"	>>trks.log
date                            		>>trks.log
python3 ~/src/APRSsrc/main/APRScalsunrisesunset.py >>trks.log
echo "TRKserver.sh:"	            		>>trks.log
echo "============:"     	       		>>trks.log
python3 ~/src/APRSsrc/main/trkserver.py    	>>trks.log 2>>trks.log &
pgrep -a python3				>>trks.log
date                            		>>trks.log
cd
