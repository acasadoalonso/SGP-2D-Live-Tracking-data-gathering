#!/usr/bin/env bash

sudo apt-get update
sudo apt-get install -y apache2
if [ ! -d /home/vagrant/src ]
then 
   sudo -u vagrant mkdir /home/vagrant/src
   sudo -u vagrant ln -s /vagrant/public/main /home/vagrant/src/APRSsrc
fi
if [ -f /nfs/hosts ]
then 
	sudo cat /nfs/hosts >>/etc/hosts
fi

if [ -f /tmp/commoninstall.sh ]
then 
        sudo bash /tmp/commoninstall.sh
	echo "======================================================================="
	echo "Install the rest of the software running     bash /tmp/commoninstall.sh"
	echo "follow by running                            bash /tmp/install.sh"
	echo "======================================================================="
fi
sudo apt-get autoremove
echo "======================================================================"
echo "                   end of bootstrap                                   "
echo "======================================================================"
