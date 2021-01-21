#!/bin/bash

# trap ctrl-c and call ctrl_c()
trap ctrl_c INT SIGINT SIGTERM
function ctrl_c() {
        echo "** Trapped CTRL-C"
	echo quit | nc -N localhost 30007
	exit
}
sudo mount 192.168.1.10:/nfs/NFS/Documents /nfs
stty -F /dev/ttyAMA0 9600 raw; { echo "{class:SOFTRF,mode:RELAY,nmea:{private:true}}" ; cat /dev/ttyAMA0 ; } | sudo ~/src/SoftRF/SoftRF/SoftRF &
while  [ 1 ]
do
	cat     /nfs/tmp/aircraft.json | nc -N localhost 30007
	sudo rm /nfs/tmp/hist* &> /dev/null 
	sleep 12
done
echo quit | nc -N localhost 30007
