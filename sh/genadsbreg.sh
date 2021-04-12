#!/bin/bash
#
# generate the ADSG registration file
#
if [ $# = 0 ]; then
	server='localhost'
else
	server=$1
fi
echo "Server: "$server     
hostname=$(hostname)

if [ -z $CONFIGDIR ]
then 
     export CONFIGDIR=/etc/local/
fi
DBuser=$(echo    `grep '^DBuser '   $CONFIGDIR/APRSconfig.ini` | sed 's/=//g' | sed 's/^DBuser //g')
DBpasswd=$(echo  `grep '^DBpasswd ' $CONFIGDIR/APRSconfig.ini` | sed 's/=//g' | sed 's/^DBpasswd //g' | sed 's/ //g' )

cd ~/src/APRSsrc/utils
wget http://www.virtualradarserver.co.uk/Files/BasicAircraftLookup.sqb.gz
rm BasicAircraftLookup.sqb
gunzip BasicAircraftLookup.sqb.gz
bash get_os_csv.sh			
date										
echo "DELETE FROM Aircraft ; "                                                                 | mysql -u $DBuser -p$DBpasswd -v APRSLOG -h $server	
echo ".dump Aircraft " | sqlite3 *sqb  | sed -e '1,11d' | sed -n -e :a -e '1,4!{P;N;D;};N;ba'  | mysql -u $DBuser -p$DBpasswd  APRSLOG -h $server		   
echo "DELETE FROM Model ;   "                                                                  | mysql -u $DBuser -p$DBpasswd -v APRSLOG -h $server	
echo ".dump Model "    | sqlite3 *sqb  | sed -e '1,8d'  | sed -n -e :a -e '1,2!{P;N;D;};N;ba'  | mysql -u $DBuser -p$DBpasswd  APRSLOG -h $server		     
echo "SELECT COUNT(*) FROM Aircraft "                                                          | mysql -u $DBuser -p$DBpasswd  APRSLOG -h $server -v		     
echo "SELECT COUNT(*) FROM Model    "                                                          | mysql -u $DBuser -p$DBpasswd  APRSLOG -h $server -v		     
date
cd ~/src/APRSsrc/
python3 genadsbreg.py  -f true -o true
echo "Generation of the ADSBreg done ..."							
