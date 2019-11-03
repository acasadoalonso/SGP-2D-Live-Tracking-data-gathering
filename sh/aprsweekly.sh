#!/bin/bash
if [ $# = 0 ]; then
	server='localhost'
else
	server=$1
fi
echo "Server: "$server

hostname=$(hostname)

echo "DELETE FROM APRSLOG.GLIDERS; " | mysql --login-path=SARogn -v -h $server 
echo "INSERT INTO APRSLOG.GLIDERS SELECT * FROM OGNDB.GLIDERS; " | mysql --login-path=SARogn -v -h $server 
echo "select count(*) from GLIDERS;" |    mysql --login-path=SARogn -h $server APRSLOG
