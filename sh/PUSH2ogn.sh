#!/bin/bash
logger -t $0 "PUSH2OGN Log is starting"
date                            		>>/tmp/push2ogn.$$.log
python3 ~/src/APRSsrc/APRScalsunrisesunset.py 	>>/tmp/push2ogn.$$.log
echo "PUSH2OGN.sh:"            			>>/tmp/push2ogn.$$.log
echo "===========:"            			>>/tmp/push2ogn.$$.log
python3 ~/src/APRSsrc/push2ogn.py --SPIDER True --SPOT True --INREACH True --ADSB False		>>/tmp/push2ogn.$$.log 2>>/tmp/push2ogn.$$.err &
#python3 ~/src/APRSsrc/push2ogn.py  --ADSB True --USEDDB True	>>/tmp/push2ogn.$$.log 2>>/tmp/push2ogn.$$.err &
pgrep -a python3				>>/tmp/push2ogn.$$.log
cd


