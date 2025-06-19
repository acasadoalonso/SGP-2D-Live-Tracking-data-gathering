#!/bin/bash

if [ -z $CONFIGDIR ]
then 
     export CONFIGDIR=/etc/local/
fi
SCRIPT=$(readlink -f $0)
SCRIPTPATH=`dirname $SCRIPT`
DBuser=$(echo    `grep '^DBuser '   $CONFIGDIR/APRSconfig.ini` | sed 's/=//g' | sed 's/^DBuser //g')
DBpasswd=$(echo  `grep '^DBpasswd ' $CONFIGDIR/APRSconfig.ini` | sed 's/=//g' | sed 's/^DBpasswd //g' | sed 's/ //g' )
DBpath=$(echo  `grep '^DBpath ' $CONFIGDIR/APRSconfig.ini` | sed 's/=//g' | sed 's/^DBpath //g' | sed 's/ //g' )
#echo $DBpath
logger -t $0 "PUSH2OGN Log is starting"
date                            							>>/tmp/push2ogn.$$.log
python3 $SCRIPTPATH/../APRScalsunrisesunset.py 						>>/tmp/push2ogn.$$.log
echo "PUSH2OGN.sh:"            								>>/tmp/push2ogn.$$.log
echo "===========:"            								>>/tmp/push2ogn.$$.log
# grab the copy of the OGN DDB in json format
if [ ! -s ognddbdata.json ] ; then							# if size zero delete it
   rm ognddbdata.json
fi
if [ ! -f ognddbdata.json ] ; then							# if no file get it
   wget -O ognddbdata.json ddb.glidernet.org/download/?j=1 				>>/tmp/push2ogn.$$.log
fi

#python3 $SCRIPTPATH/../push2ogn.py --ENA  True  	                                >>/tmp/push2ogn.$$.log 2>>/tmp/push2ogn.$$.err &
#python3 ~/src/APRSsrc/push2ogn.py --ADSB   True --USEDDB True	                        >>/tmp/push2ogn.$$.log 2>>/tmp/push2ogn.$$.err &
python3 ~/src/APRSsrc/push2ogn.py --SPIDER True --SPOT True --INREACH True --AVX True	>>/tmp/push2ogn.$$.log 2>>/tmp/push2ogn.$$.err &
pgrep -a python3				                                        >>/tmp/push2ogn.$$.log
cd


