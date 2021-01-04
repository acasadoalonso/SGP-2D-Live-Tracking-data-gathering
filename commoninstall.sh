#!/bin/bash 
if [ $# = 0 ]; then
	sql='NO'
else
	sql=$1
fi
echo								#
echo " "							#
echo "Installing the common components of the OGN  ...." 	#
echo "=================================================="	#
echo " "							#
echo								#
export LC_ALL=en_US.UTF-8 && export LANG=en_US.UTF-8		#
sudo apt-get install -y software-properties-common 		#
sudo apt-get install -y python3-software-properties 		#
sudo apt-get install -y build-essential 			#
#sudo rm /etc/apt/sources.list.d/ondre*				#
#sudo add-apt-repository ppa:ondrej/php				#
echo								#
echo " "							#
echo "Lets update the operating system libraries  ...." 	#
echo "=================================================="	#
echo " "							#
echo								#
sudo apt-get update						#
sudo apt-get install -y language-pack-en-base 			# 
export LC_ALL=en_US.UTF-8 && export LANG=en_US.UTF-8		#
echo "export LC_ALL=en_US.UTF-8 && export LANG=en_US.UTF-8 " >>~/.profile #
echo "export LD_LIBRARY_PATH=/usr/local/lib" >>~/.profile 	#
sudo apt-get -y upgrade						#
sudo apt install -y cifs-utils					#
sudo apt install -y nfs-common					#
echo								#
echo " "							#
echo "Installing the packages required . (LAMP stack)..."	#
echo "=================================================="	#
echo " "							#
echo								#
cd /var/www/html/main						#
sudo apt install -y mariadb-server mariadb-client		#
sudo apt install -y libmariadb-dev				#
if [ $sql = 'MySQL' ]			
then		
	sudo apt-get install -y tasksel  			#
	sudo apt policy mysql-server				#
	sudo apt install mysql-server=5.7.32-1ubuntu18.04	#
	sudo apt install mysql-client=5.7.32-1ubuntu18.04	#
fi								#
sudo tasksel install lamp-server                                #
sudo apt-get install -y percona-toolkit				#
sudo apt-get install -y sqlite3 ntpdate				#
sudo apt-get install -y python3-dev python3-pip 		#
sudo apt-get install -y figlet inetutils-* mailutils		#
sudo apt-get install -y avahi-daemon libcurl4-openssl-dev       #
sudo apt-get install -y dos2unix libarchive-dev	 autoconf mc	#
sudo apt-get install -y pkg-config git	mutt vim		# 
git config --global user.email "acasadoalonso@gmail.com"        #
git config --global user.name "Angel Casado"                    #
sudo apt-get install -y apache2 php 				#
sudo apt-get install -y php-sqlite3 php-mysql php-cli 		#
sudo apt-get install -y php-mbstring php-json			#
sudo apt-get install -y php7.4					#
sudo apt-get install -y ntpdate					#
sudo apt-get install -y ssmtp					#
sudo apt-get install -y at sshpass minicom 			#
sudo apt-get install -y fakeroot debhelper 			#
sudo apt-get install -y libfile-fcntllock-perl			#
sudo a2enmod rewrite						#
sudo phpenmod mbstring						#
echo								#
echo "Installing phpmyadmin  ... "				#
echo								#
sudo apt-get install -y phpmyadmin 				#
sudo service apache2 restart					#
sudo apt-get -y autoremove					#
echo								#
echo " "							#
echo "Installing the PYTHON modules required  ..."		#
echo "=================================================="	#
echo " "							#
echo								#
#sudo -H python3 -m pip install --upgrade pip			#
pip3 -V								#
sudo -H python3 -m pip install ephem pytz geopy configparser 	#
sudo -H python3 -m pip install pycountry uritemplate requests	#
sudo -H python3 -m pip install beeprint ogn.client		#
sudo -H python3 -m pip install tqdm psutil python-dateutil	#
sudo -H python3 -m pip install ttn               		#
sudo -H python3 -m pip install pyserial 			#
sudo -H python3 -m pip install eciespy pycryptodome rsa         #
sudo -H python3 -m pip install mariadb               		#
sudo -H python3 -m pip install ansible               		#
sudo -H python3 -m pip install ansible-lint            		#
sudo -H python3 -m pip install molecule               		#
sudo -H python3 -m pip install docker               		#
sudo -H python3 -m pip install yamllint               		#
if [ $sql = 'MySQL' ]					
then	
	sudo -H pip3 uninstall mysqlclient			#
fi
sudo apt-get install -y libmysqlclient-dev 			#
sudo -H pip3 install --no-binary mysqlclient mysqlclient 	#
cd /var/www/html/						#
if [ ! -d /etc/local ]						#
then								#
    sudo mkdir /etc/local					#
    sudo chmod 777 /etc/local					#
fi								#
echo								#
if [ ! -d /var/www/data ]					#
then								#
    sudo mkdir /var/www/data					#
    sudo chmod 777 /var/www/data				#
fi								#
if [ ! -d /var/www/html/cuc ]					#
then								#
    sudo mkdir /var/www/html/cuc				#
    sudo chmod 777 /var/www/html/cuc				#
fi								#
echo								#
echo " "							#
echo "Installing the templates needed  ...." 			#
echo "=================================================="	#
echo " "							#
echo								#
cd /var/www/html/main						#
echo "Running msqladmin .... assign root password ... "		#
sudo mysqladmin -u root password ogn				#
cd /var/www/html/main						#
if [ $sql = 'docker' ]			
then			
   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
   sudo apt-key fingerprint 0EBFCD88
   sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"
   sudo apt update
   sudo apt-get install -y docker-ce docker-ce-cli containerd.io
   sudo usermod -aG docker $USER
   cp doc/.my.cnf ~/
   sudo bash dockerfiles/mariadbnet.sh
   sudo bash dockerfiles/mariadb.sh
   sudo bash dockerfiles/mariadbpma.sh
   sudo mysql -u root -pogn -h MARIADB <doc/adduser.sql	
   echo "SET GLOBAL log_bin_trust_function_creators = 1; " | sudo mysql -u root -pogn -h MARIADB
fi
cd								#
sudo mysql_secure_installation					#
sudo apt-get install percona-toolkit				#
sudo dpkg-reconfigure tzdata					#
sudo apt-get -y autoremove					#
echo								#
echo " "							#
echo "End of common componets  ...." 				#
echo "=================================================="	#
echo " "							#
echo								#
