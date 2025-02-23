#!/bin/bash
#
# generate the ADSB registration file
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
date
cd ~/src/APRSsrc/utils
rm BasicAircraftLookup.sqb.gz
echo "Get the VRS Basic Aircraft DB ... into a sqlite3 DB ..."
wget http://www.virtualradarserver.co.uk/Files/BasicAircraftLookup.sqb.gz
if [ -f BasicAircraftLookup.sqb.gz ]; then
   rm BasicAircraftLookup.sqb
   gunzip BasicAircraftLookup.sqb.gz
fi

date										
bash ../sh/genadsb_get_os_csv.sh		# get the opensky database	
date							
echo " "
echo "Import the VRS Basic Aircraft database into "$server
echo "=========================================== "$server
echo " "
echo "DELETE FROM Aircraft ; "                                                                 | mysql -u $DBuser -p$DBpasswd -v APRSLOG -h $server	
echo ".dump Aircraft " | sqlite3 *sqb  | sed -e '1,11d' | sed -n -e :a -e '1,4!{P;N;D;};N;ba'  | mysql -u $DBuser -p$DBpasswd  APRSLOG -h $server		   
echo "DELETE FROM Model ;   "                                                                  | mysql -u $DBuser -p$DBpasswd -v APRSLOG -h $server	
echo ".dump Model "    | sqlite3 *sqb  | sed -e '1,8d'  | sed -n -e :a -e '1,2!{P;N;D;};N;ba'  | mysql -u $DBuser -p$DBpasswd  APRSLOG -h $server		     
echo "DELETE FROM Operator ;   "                                                               | mysql -u $DBuser -p$DBpasswd -v APRSLOG -h $server	
echo ".dump Operator"  | sqlite3 *sqb  | sed -e '1,8d'  | sed -n -e :a -e '1,2!{P;N;D;};N;ba'  | mysql -u $DBuser -p$DBpasswd  APRSLOG -h $server

echo "SELECT 'Aircraft', COUNT(*) FROM Aircraft "                                              | mysql -u $DBuser -p$DBpasswd  APRSLOG -h $server -v		     
echo "SELECT 'Model',    COUNT(*) FROM Model    "                                              | mysql -u $DBuser -p$DBpasswd  APRSLOG -h $server -v		     
echo "SELECT 'Operator', COUNT(*) FROM Operator       "                                        | mysql -u $DBuser -p$DBpasswd  APRSLOG -h $server -v		     
date
cd ~/src/APRSsrc/
echo " "
echo "Generating the ADSBreg ..."
echo "=========================="
echo " "
python3 genadsbreg.py  -f True -o True -a True -m True -d $server
echo "Generation of the ADSBreg done ..."
cd ~/src/APRSsrc/utils
wc Basic*  *.csv
rm -f wget-log*
date
