#!/bin/bash 
echo "DROP DATABASE IF EXISTS APRSLOG "       | mysql  -h 172.17.0.2 -u root -pogn 
echo "CREATE DATABASE IF NOT EXISTS APRSLOG " | mysql  -h 172.17.0.2 -u root -pogn 
mysql APRSLOG -h 172.17.0.2 -u root -pogn </tmp/APRSLOG.template.sql
