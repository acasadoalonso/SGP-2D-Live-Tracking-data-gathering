#!/bin/bash
mysql -u root -pogn -h mariadb         < ../doc/adduser.sql
echo "create database if not exists APRSLOG"          | mysql -u root -pogn -h mariadb
echo "set GLOBAL log_bin_trust_function_creators=on;" | mysql -u root -pogn -h mariadb
mysql -u root -pogn -h mariadb APRSLOG < ../APRSLOG.template.sql
mysql -u root -pogn -h mariadb APRSLOG < /var/www/html/files/GLIDERS.sql
