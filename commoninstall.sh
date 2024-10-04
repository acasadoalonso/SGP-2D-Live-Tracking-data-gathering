#!/bin/bash 
if [ $# = 0 ]; then
	sql='NO'
else
	sql=$1
fi
SCRIPT=$(readlink -f $0)
SCRIPTPATH=`dirname $SCRIPT`
echo								#
echo " "							#
echo " "							#
echo "=================================================="	#
echo "Installing the common components of the OGN  ...." 	#
echo "=================================================="	#
echo " "							#
echo " "							#
echo								#
export LC_ALL=en_US.UTF-8 && export LANG=en_US.UTF-8		#
sudo apt-get install -y software-properties-common 		#
sudo apt-get install -y python3-software-properties 		#
sudo apt-get install -y build-essential 			#
sudo apt-get install -y python-is-python3			#
echo								#
echo " "							#
echo "=================================================="	#
echo "Lets update the operating system libraries  ...." 	#
echo "=================================================="	#
echo " "							#
echo								#
sudo apt-get update						#
sudo locale-gen en_US en_US.UTF-8				#
sudo update-locale 						#
export LC_ALL=en_US.UTF-8 && export LANG=en_US.UTF-8		#
echo "export LC_ALL=en_US.UTF-8 && export LANG=en_US.UTF-8 " >>~/.profile #
echo "export LD_LIBRARY_PATH=/usr/local/lib" >>~/.profile 	#
sudo apt-get -y upgrade						#
sudo apt install -y cifs-utils					#
sudo apt install -y nfs-common					#
echo								#
echo " "							#
echo "=================================================="	#
echo "Installing the packages required . (LAMP stack)..."	#
echo "=================================================="	#
echo " "							#
echo								#
								#
if [ ! -d /var/www/html ]					#
then								#
    if [ ! -d /var/www ]					#
    then							#
         sudo mkdir /var/www					#
         sudo chmod 777 /var/www/				#
         sudo chown www-data:root /var/www/			#
    fi								#
    sudo mkdir /var/www/html/					#
    sudo chmod 777 /var/www/html/				#
    sudo chown www-data:root /var/www/html/			#
fi								#
if [ ! -d /var/www/html/main ]					#
then								#
    sudo mkdir /var/www/html/main				#
    sudo chmod 777 /var/www/html/main				#
    sudo chown www-data:root /var/www/html/main			#
fi								#
cd /var/www/html/main						#
echo "============================="                            #
echo "Install now MariaDB & python3"                            #
echo "============================="                            #
sudo apt install -y mariadb-client				#
sudo apt install -y libmariadb-dev				#
sudo apt install -y python3-dev python3-pip 			#
sudo apt install -y python3-autopep8				#
if [ $sql = 'MariaDB' ]						#
then								#
     sudo apt install -y mariadb-server 			#
     sudo -H python3 -m pip install mariadb            		#
fi								#
if [ $sql = 'MySQL' ]						#
then								#
	sudo apt-get install -y tasksel  			#
	sudo apt policy mysql-server				#
	sudo apt install mysql-server=5.7.32-1ubuntu18.04	#
	sudo apt install mysql-client=5.7.32-1ubuntu18.04	#
        sudo tasksel install lamp-server                        #
fi								#
sudo apt-get install -y percona-toolkit				#
sudo apt-get install -y sqlite3 ntpdate				#
sudo apt-get install -y figlet inetutils-* nmap net-tools	#
sudo apt-get install -y avahi-daemon libcurl4-openssl-dev       #
sudo apt-get install -y dos2unix libarchive-dev	 autoconf mc	#
sudo apt-get install -y pkg-config git	mutt vim		# 
git config --global user.email "acasadoalonso@gmail.com"        #
git config --global user.name "Angel Casado"                    #
echo "============================"                             #
echo "Install now Apache2 & PHP   "                             #
echo "============================"                             #
sudo apt-get install -y apache2 php 				#
sudo apt-get install -y php-sqlite3 php-cli 			#
sudo apt-get install -y php-mysql 				#
sudo apt-get install -y php-mbstring php-json			#
sudo apt-get install -y php8.1	php8.1-mysql			#
sudo a2enmod rewrite						#
sudo phpenmod mbstring						#
sudo a2enmod headers						#
echo "==========================="                              #
echo "Install now other utilities"				#
echo "==========================="                              #
sudo apt-get install -y ntpdate					#
sudo apt-get install -y ssmtp					#
sudo apt-get install -y at sshpass minicom sshfs		#
sudo apt-get install -y fakeroot debhelper 			#
sudo apt-get install -y libfile-fcntllock-perl			#
sudo apt-get install -y nvme-cli				#
sudo apt-get install -y dnsutils				#
sudo apt-get install -y neofetch				#
echo	""							#
echo	""							#
if [ $sql = 'MySQL' ]						#
then								#
    sudo apt-get install -y phpmyadmin 				#
    sudo service apache2 restart				#
    sudo apt-get -y autoremove					#
    echo "================================================"     #
    echo "Running msqladmin .... assign root password ... "	#
    echo "================================================"     #
    if [ ! -f .DBpasswd    ]					#
    then							#
       echo "Type DB password ..."				#
       read DBpasswd						#
       echo $DBpasswd > .DBpasswd				#
    fi								#
    sudo mysqladmin -u root password $(cat .DBpasswd)		#
    sudo mysql_secure_installation				#
fi								#
echo								#
echo " "							#
echo "=================================================="	#
echo "Installing the PYTHON modules required  ..."		#
echo "=================================================="	#
echo " "							#
echo								#
pip install --upgrade pip					#
pip3 -V								#
sudo -H python3 -m pip install ephem pytz geopy configparser 	--break-system-packages
sudo -H python3 -m pip install pycountry uritemplate requests	--break-system-packages
sudo -H python3 -m pip install beeprint ogn.client		--break-system-packages
sudo -H python3 -m pip install tqdm psutil python-dateutil	--break-system-packages
sudo -H python3 -m pip install ping3               		--break-system-packages
sudo -H python3 -m pip install pipreqs               		--break-system-packages
sudo -H python3 -m pip install ttn               		--break-system-packages
sudo -H python3 -m pip install paho-mqtt			--break-system-packages
sudo -H python3 -m pip install pyserial 			--break-system-packages
sudo -H python3 -m pip install pyopenssl 			--break-system-packages
sudo -H python3 -m pip install eciespy pycryptodome rsa         --break-system-packages
sudo -H python3 -m pip install ansible               		--break-system-packages
sudo -H python3 -m pip install ansible-lint            		--break-system-packages
sudo -H python3 -m pip install molecule               		--break-system-packages
sudo -H python3 -m pip install docker               		--break-system-packages
sudo -H python3 -m pip install yamllint               		--break-system-packages
sudo -H python3 -m pip install setuptools 			--break-system-packages
sudo -H python3 -m pip install flake8 icecream         		--break-system-packages
sudo -H python3 -m pip install httpx               		--break-system-packages
sudo -H python3 -m pip install mysqlclient			--break-system-packages
sudo -H python3 -m pip install timezonefinder 			--break-system-packages
sudo -H python3 -m pip install airportsdata			--break-system-packages
sudo -H python3 -m pip install termcolor			--break-system-packages
sudo -H python3 -m pip install gitpython			--break-system-packages
pipreqs  --force .
if [ $sql = 'MySQL' ]						#	
then								#
	sudo -H pip3 uninstall mysqlclient			#
        sudo apt-get install -y libmysqlclient-dev		#
        sudo apt-get install percona-toolkit			#
   	sudo mysql_secure_installation				#
else								#
        sudo apt-get install libmariadb-dev			#
fi								#
sudo -H pip3 install --no-binary mysqlclient mysqlclient 	#
cd /var/www/html/						#
if [ ! -d /etc/local ]						#
then								#
    sudo mkdir /etc/local					#
    sudo chmod 777 /etc/local					#
    sudo chown $USER:root -R /etc/local				#
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
echo "=================================================="	#
echo "Installing the templates needed  ...." 			#
echo "=================================================="	#
echo " "							#
echo								#
if [ ! -d /var/www/html/main ]					#
then								#
     mkdir /var/www/html/main					#
     chmod 777 /var/www/html/main				#
fi								#
cd /var/www/html/main						#
if [ $sql = 'docker' -o $sql == 'MariaDB' ]			#
then								#
   echo " "							#
   echo "=================================================="	#
   echo "Install docker  ...." 					#
   echo "=================================================="	#
   echo " "							#
   if [ ! -f /usr/bin/docker ]					#
   then								#
      sudo curl -sSL https://get.docker.com | sh		#
      sudo usermod -aG docker $USER				#
      sudo apt update						#
   fi								#
   if [ $SCRIPTPATH/.. == 'src' ]				#
   then								#
   	cd $SCRIPTPATH/../SARsrc/dockerfiles			#
   	echo "Current directory: "$(pwd)			#
   	cp ../doc/.my.cnf ~/					#
   	arch=$(uname -m)					#
   	if [ $arch != 'x84-64' ]				#
   	then							#
      		cd Mariadb.debian				#
      		echo "Create the container for the non-AMD64 architecture" #
      		echo "===================================================" #
      		#bash mariadb.patch				#
      		make						#
      		echo "Create mariadb container"			#
      		echo "========================"			#
      		bash mariadb.sh					#
      		echo "Create phpmyadmin container"		#
      		echo "==========================="		#
      		bash mariadbpma.pull				#
      		bash mariadbpma.sh				#
      		cd ..						#
   	else							#
      		sudo bash mariadbnet.sh				#
      		sudo bash mariadb.sh				#
      		sudo bash mariadbpma.sh				#
   	fi							#
   	bash install.portainer					#
   	if [ ! -f .DBpasswd    ]				#
   	then							#
      		echo "Type DB password ..."			#
      		read DBpasswd					#
      		echo $DBpasswd > .DBpasswd			#
   	fi							#
   	cd $SCRIPTPATH/../SARsrc				#
   	echo "Current directory: "$(pwd)			#
   	ping MARIADB -c 5					#
   	cat .DBpasswd						#
   	docker exec mariadb mariadb -e "create user if not exists root@'%' identified by '$(cat .DBpasswd)';"
   	docker exec mariadb mariadb -e "grant all privileges on *.* to root@'%' with GRANT option;"
   	sudo mysql -u root -p$(cat .DBpasswd) -h MARIADB <doc/adduser.sql	
   	echo "SET GLOBAL log_bin_trust_function_creators = 1; " | sudo mysql -u root -p$(cat .DBpasswd) -h MARIADB
   	echo "Secure the installation now ... answer the questions"  #
   fi								#
   sudo apt-get install percona-toolkit				#
   cd -								#
fi								#
cd								#
sudo apt-get -y autoremove					#
echo "__________________________________________________"       #
df -h								#
hostnamectl							#
neofetch							#
echo								#
echo " "							#
echo "=================================================="	#
echo " End of common components  ...." 				#
echo "=================================================="	#
echo " "							#
echo " "							#
echo								#
