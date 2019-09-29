#!/bin/bash
echo "DELETE FROM APRSLOG.GLIDERS; " | mysql -v -u ogn -pogn -h UBUNTU 
echo "INSERT INTO APRSLOG.GLIDERS SELECT * FROM OGNDB.GLIDERS; " | mysql -v -u ogn -pogn -h UBUNTU 
echo "select count(*) from GLIDERS;" |    mysql -h UBUNTU -u ogn -pogn APRSLOG
