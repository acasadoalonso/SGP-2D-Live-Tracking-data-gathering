#!/bin/bash 
echo								#
echo " "							#
echo "Installing the SGP 2D live tracking interface ...." 	#
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
echo								#
echo " "							#
echo "Installing the packages required . (LAMP stack)..."	#
echo "=================================================="	#
echo " "							#
echo								#
cd /var/www/html/main						#
sudo apt-get install -y mysql-server mysql-client sqlite3	#
sudo apt-get install -y python3-dev python3-pip 		#
sudo apt-get install -y python-mysqld  				#
sudo apt-get install -y dos2unix libarchive-dev	 autoconf mc	#
sudo apt-get install -y pkg-config git	mutt npm nodejs		# 
git config --global user.email "acasadoalonso@gmail.com"        #
git config --global user.name "Angel Casado"                    #
sudo apt-get install -y apache2 php 				#
sudo apt-get install -y php-sqlite php-mcrypt php-mysql php-cli #
sudo apt-get install -y php-mbstring php-gettext php-json	#
sudo apt-get install -y php7.2					#
sudo a2enmod rewrite						#
sudo phpenmod mcrypt						#
sudo phpenmod mbstring						#
sudo cat /etc/apache2/apache2.conf html.dir 	>>temp.conf	#
sudo echo "ServerName APRSLOG " >>temp.conf			#
sudo mv temp.conf /etc/apache2/apache2.conf			#
sudo service apache2 restart					#
echo								#
echo "Installing phpmyadmin  ... "				#
echo								#
sudo apt-get install -y phpmyadmin 				#
sudo service apache2 restart					#
sudo -H python3 -m pip install --upgrade pip			#
pip3 -V
sudo -H python3 -m pip install ephem pytz geopy configparser pycountry	#
sudo apt-get install libmysqlclient-dev 			#
sudo -H pip3 install mysqlclient 				#
cd /var/www/html/						#
sudo npm install websocket socket.io request parsejson	ini	#
sudo npm install forever -g 					#
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
sudo cp config.template /etc/local/APRSconfig.ini		#
cd /var/www/html/						#
python3 genconfig.py						#
cd /var/www/html/main						#
mysqladmin -u root password ogn					#
mysql -u root -pogn <doc/adduser.sql				#
echo "CREATE DATABASE APRSLOG" | mysql -u root -pogn		#
mysql --database APRSLOG -u root -pogn < APRSLOG.template.sql	#
echo								#
echo "Optional steps ... "					#
echo								#
sudo apt-get install -y libsqlite3-dev ruby-dev			#
echo "Install MailCatcher."					#
sudo gem install mailcatcher					#
mailcatcher --http-ip=0.0.0.0					#
cd sh	 							#
crontab <crontab.data						#
crontab -l 							#
if [ ! -d ~/src  ]						#
then								#
	mkdir ~/src   						#
	mkdir ~/src/APRSsrc					#
	ln -s /var/www/html/main ~/src/APRSsrc			#
fi								#
ls  -la ~/src 							#
if [ ! -d /nfs  ]						#
then								#
	sudo mkdir /nfs						#
	sudo mkdir /nfs/OGN					#
	sudo mkdir /nfs/OGN/APRSdata				#
	sudo chown vagrant:vagrant /nfs/OGN/APRSdata		#
	sudo chmod 777 /nfs/OGN/APRSdata			#
	cd /var/www/html/					#
	sudo chown vagrant:vagrant *				# 
	sudo chmod 777 *					#
	sudo chown vagrant:vagrant */*				# 
	sudo chmod 777 */*					#
fi								#
cd								#
sudo dpkg-reconfigure tzdata					#
sudo apt-get -y dist-upgrade					#
sudo apt-get -y autoremove					#
cp /var/www/html/main/doc/aliases .bash_aliases			#
touch APRSinstallation.done					#
echo								#
echo "========================================================================================================"	#
echo "Installation done ..."					#
echo "Review the configuration file on /etc/local ..."								#
echo "Review the configuration of the crontab and the shell scripts on ~/src " 					#
echo "In order to execute the APRSLOG data crawler execute:  bash ~/src/APSRlive.sh " 				#
echo "Check the placement of the RootDocument on APACHE2 ... needs to be /var/www/html				#
echo "If running in Windows under Virtual Box, run dos2unix on /var/www/html & ./main & ~/src			#
echo "Install phpmyadmin if needed !!!                                                                          #
echo "========================================================================================================"	#
echo								#
bash
alias

