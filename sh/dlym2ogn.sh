#!/bin/bash
cd /nfs/OGN/SWdata 
echo "========"$(hostname)"===============:"	>>dlym2ogn.log
date                            		>>dlym2ogn.log
python3 ~/src/APRSsrc/main/APRScalsunrisesunset.py >>dlym2ogn.log
echo "DLYM2OGN.sh:"	            		>>dlym2ogn.log
echo "===========:"     	       		>>dlym2ogn.log
python3 ~/src/APRSsrc/main/dlym2ogn.py -d 30   	>>dlym2ogn.log 2>>dlym2ognerr.log &
pgrep -a python3				>>dlym2ogn.log
date                            		>>dlym2ogn.log
cd
