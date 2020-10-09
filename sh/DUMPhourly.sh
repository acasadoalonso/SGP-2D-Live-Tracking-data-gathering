#!/bin/bash
if [ ! -d /nfs/tmp ]
then
   sudo mount 192.168.1.10:/nfs/NFS/Documents /nfs
fi
sudo killall dump1090
sudo service dump1090-fa restart
sudo rm /nfs/tmp/his* >/dev/null 2>/dev/null
sudo rm /nfs/tmp/aircraft.json.* 2>/dev/null
touch   /nfs/tmp/ADSB
