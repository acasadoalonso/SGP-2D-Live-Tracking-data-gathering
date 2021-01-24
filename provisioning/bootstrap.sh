#!/usr/bin/env bash

echo "======================================================================"
echo "                   Start  bootstrap                                   "
echo "======================================================================"
sudo apt-get update
if [ ! -d /home/vagrant/src ]
then 
   sudo -u vagrant mkdir /home/vagrant/src
   if [ -d /vagrant/public/main ]
   then
      sudo -u vagrant ln -s /vagrant/public/main /home/vagrant/src/APRSsrc
   fi
fi
if [ -f /nfs/hosts ]
then 
	sudo cat /nfs/hosts >>/etc/hosts
fi

if [ -f /tmp/commoninstall.sh ]
then 
	echo "======================================================================="
	echo "Install the rest of the software running     bash /tmp/commoninstall.sh"
	echo "follow it by running                         bash /tmp/install.sh      "
	echo "======================================================================="
        sudo bash /tmp/commoninstall.sh
        sudo bash /tmp/install.sh
fi
sudo apt-get autoremove
sudo apt-get clean
echo "======================================================================"
echo "                   end of bootstrap                                   "
echo "======================================================================"
