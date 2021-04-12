#!/bin/bash

if [ -z $CONFIGDIR ]
then 
     export CONFIGDIR=/etc/local
fi
pid=$(echo     `grep '^pid' $CONFIGDIR/APRSconfig.ini` | sed 's/=//g' | sed 's/^pid//g').PUSH2OGN
DBpath=$(echo  `grep '^DBpath ' $CONFIGDIR/APRSconfig.ini` | sed 's/=//g' | sed 's/^DBpath //g' | sed 's/ //g' )
if [ ! -f $pid ]
then
                logger  -t $0 "PUSH2OGN Log is not alive"
                if [ -f $pid ] # if OGN repo interface is  not running
                then
			pnum=$(cat $pid)
                        sudo kill $pnum 
                        rm $pid
                fi

#               restart OGN data collector
                #bash ~/src/sh/push2ogn.sh 
                logger -t $0 "PUSH2OGN Log seems down, restarting"
                echo $(date)" - "$(hostname)" - PUSH2OGN "  >>$DBpath/.APRSrestart.log
else
                logger -t $0 "PUSH2OGN Log is alive"
fi

DBuser=$(echo    `grep '^DBuser '   $CONFIGDIR/APRSconfig.ini` | sed 's/=//g' | sed 's/^DBuser //g')
DBpasswd=$(echo  `grep '^DBpasswd ' $CONFIGDIR/APRSconfig.ini` | sed 's/=//g' | sed 's/^DBpasswd //g' | sed 's/ //g' )
adsb=$(echo       `grep '^ADSB '    $CONFIGDIR/APRSconfig.ini` | sed 's/=//g' | sed 's/^ADSB //g')
if [ $adsb = "True" ]
then

	if [ ! -d /nfs/tmp ]
	then
   		sudo mount 192.168.1.10:/nfs/NFS/Documents /nfs
	fi
	echo `sudo service dump1090-fa status`  | grep "No data received from the dongle for a long time, it may have wedged" | wc >/tmp/tt
	res=$(cat /tmp/tt)
	r=$(echo $res | awk '/^/{print $1}')
	#echo $r
	pnum=$(pgrep dump1090)
	if [ $? -ne 0 ] ||  [ $r = 1 ]
	then 
   		#sudo killall dump1090 
   		sudo service dump1090-fa restart
   		#bash ~/dump1090.sh
   		logger -t $0 "dump1090  is restarted now"
	else
   		logger -t $0 "DUMP1090  is alive"
	fi
	rm /tmp/tt
fi   
