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
cd ~/src/APRSsrc
wget http://www.virtualradarserver.co.uk/Files/BasicAircraftLookup.sqb.gz
rm BasicAircraftLookup.sqb
gunzip BasicAircraftLookup.sqb.gz
python3 genadsbreg.py 
date										
echo "DELETE FROM Aircraft ; "                      | mysql --login-path=SARogn -v APRSLOG -h $server	
echo ".dump Aircraft " | sqlite3 *sqb  | sed -e '1,11d' | sed -n -e :a -e '1,4!{P;N;D;};N;ba'  | mysql --login-path=SARogn  APRSLOG -h $server		   
echo "DELETE FROM Model ;   "                       | mysql --login-path=SARogn -v APRSLOG -h $server	
echo ".dump Model "    | sqlite3 *sqb  | sed -e '1,8d'  | sed -n -e :a -e '1,2!{P;N;D;};N;ba'  | mysql --login-path=SARogn  APRSLOG -h $server		     
echo "SELECT COUNT(*) FROM Aircraft "    |  mysql --login-path=SARogn  APRSLOG -h $server -v		     
echo "SELECT COUNT(*) FROM Model    "    |  mysql --login-path=SARogn  APRSLOG -h $server -v		     
date										
