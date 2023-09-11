#!/bin/bash
if [ -z $CONFIGDIR ]
then 
     export CONFIGDIR=/etc/local/
fi
DBuser=$(echo    `grep '^DBuser '   $CONFIGDIR/APRSconfig.ini` | sed 's/=//g' | sed 's/^DBuser //g')
DBpasswd=$(echo  `grep '^DBpasswd ' $CONFIGDIR/APRSconfig.ini` | sed 's/=//g' | sed 's/^DBpasswd //g' | sed 's/ //g' )
DBpath=$(echo    `grep '^DBpath '   $CONFIGDIR/APRSconfig.ini` | sed 's/=//g' | sed 's/^DBpath //g' | sed 's/ //g' )

SCRIPT=$(readlink -f $0)
SCRIPTPATH=`dirname $SCRIPT`

mysql -u root -p$DBpasswd -h mariadb         < ../doc/adduser.sql
echo "create database if not exists APRSLOG"          | mysql -u root -p$DBpasswd -h mariadb
echo "set GLOBAL log_bin_trust_function_creators=on;" | mysql -u root -p$DBpasswd -h mariadb
mysql -u root -p$DBpasswd -h mariadb APRSLOG < ../APRSLOG.template.sql
mysql -u root -p$DBpasswd -h mariadb APRSLOG < /var/www/html/files/GLIDERS.sql
