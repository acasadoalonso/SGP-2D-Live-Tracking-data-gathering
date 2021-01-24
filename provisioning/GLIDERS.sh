#!/bin/bash
echo "DROP TABLE GLIDERS" | mysql APRSLOG -h 172.17.0.2 -u root -pogn 
mysql APRSLOG -h 172.17.0.2 -u root -pogn </tmp/GLIDERS.sql
