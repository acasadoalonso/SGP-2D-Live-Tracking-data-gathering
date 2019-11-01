#!/bin/bash
server="localhost"
hostname=$(hostname)

echo "DELETE FROM APRSLOG.GLIDERS; " | mysql -v -u ogn -pogn -h $server 
echo "INSERT INTO APRSLOG.GLIDERS SELECT * FROM OGNDB.GLIDERS; " | mysql -v -u ogn -pogn -h $server 
echo "select count(*) from GLIDERS;" |    mysql -h $server -u ogn -pogn APRSLOG
