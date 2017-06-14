#!/bin/sh

###############
## SSH setup ##
##
## persistence of ssh keys possible in /var/config/ (optionnal)
## persistence of /root possible in /root (optionnal)
##

if [ ! -f /etc/ssh/ssh_host_rsa_key ]
then
    # check for persisted hostkey
    if [ -f /var/config/etc/ssh/ssh_host_dsa_key ]; then
        cp /var/config/etc/ssh/ssh_host* /etc/ssh/
    else
        # create them if needed
        ssh-keygen -t rsa -b 2048 -N '' -f /etc/ssh/ssh_host_rsa_key &
        ssh-keygen -t dsa -N '' -f /etc/ssh/ssh_host_dsa_key &
        ssh-keygen -t ecdsa -N '' -f /etc/ssh/ssh_host_ecdsa_key &
        ssh-keygen -t ed25519 -N '' -f /etc/ssh/ssh_host_ed25519_key || true &
        wait `jobs -p` || true
        # and persist them in /var/config/etc/ssh
        mkdir -p /var/config/etc/ssh/
        cp /etc/ssh/ssh_host* /var/config/etc/ssh/
    fi
fi

# add optional persistence or /root
# /root
cp -an /root.orig/. /root

# make sure some base files and directories are present
if [ ! -d /root/.ssh ];then
    mkdir /root/.ssh
    chmod 700 /root/.ssh
    chown root:root /root/.ssh
fi
touch -a /root/.ssh/authorized_keys.local

## force authorized ssh keys from variables and concatene with local/persisted ones
if [ ! -z "${SSH_KEYS}" ]; then
    echo $SSH_KEYS | tr -d '"' | tr ',' '\n' > /root/.ssh/authorized_keys
    cat /root/.ssh/authorized_keys.local >> /root/.ssh/authorized_keys
    
    echo $SSH_KEYS | tr -d '"' | tr ',' '\n' > /var/www/.ssh/authorized_keys
else 
    cat /root/.ssh/authorized_keys.local > /root/.ssh/authorized_keys
fi

## force root password
if [ ! -z "${ROOT_PASSWORD}" ]; then
   echo "Setting root password as *${ROOT_PASSWORD}*"
   usermod --password "${ROOT_PASSWORD}" root
   sed -i 's/#PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config
   sed -i 's/#PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config
fi

## and start sshd
touch /var/log/sshd.log
tail -F -n0 /var/log/sshd.log &
/usr/sbin/sshd -E /var/log/sshd.log

## end SSH setup ##
###################

###############
## cron setup ##
##
## persistence of crontabs possible in /etc/crontabs/ (optionnal)
##

/usr/sbin/crond

## end cron setup ##
###################

###############
## Exim setup ##
##

sed -i 's/# tls_advertise_hosts = \*/tls_advertise_hosts = /' /etc/exim/exim.conf

touch /var/log/exim/mainlog
chown exim /var/log/exim/mainlog
tail -F -n0 /var/log/exim/* &
/usr/sbin/exim -bd -q15m &

## end Exim setup ##
###################

###############
## Apache setup ##
##
## persistence of application in /var/www (mandatory)
## persistence of php config in /etc/php7/conf.d (optionnal)
##

touch /var/log/apache2/access.log
chgrp wheel /var/log/apache2/access.log
tail -F -n0 /var/log/apache2/* &
cp -an /etc/php7/conf.d.orig/. /etc/php7/conf.d

if [ ! -d /var/www/public ]; then
    mkdir /var/www/public
    chown apache /var/www/public
fi
sed -i 's/Options Indexes FollowSymLinks/Options -Indexes +FollowSymLinks/' /etc/apache2/httpd.conf
sed -ie '264s/AllowOverride None/AllowOverride all/g' /etc/apache2/httpd.conf
## end Apache setup ##
###################

###################
## Start processes

## you may wish to start additional processes here
## make sure they detach from console
## ....

## and finally start main process (not detached)
exec httpd -D FOREGROUND

