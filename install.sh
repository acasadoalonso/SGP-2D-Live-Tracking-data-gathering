#!/bin/bash 
echo								#
echo "Installing the SGP 2D live tracking interface ...." 	#
echo								#
export LC_ALL=en_US.UTF-8 && export LANG=en_US.UTF-8		#
sudo apt-get install -y software-properties-common python-software-properties #
#sudo rm /etc/apt/sources.list.d/ondre*				#
#sudo add-apt-repository ppa:ondrej/php				#
echo								#
echo " lets update the operating system libraries  ...." 	#
echo								#
sudo apt-get update						#
sudo apt-get install -y language-pack-en-base 			# 
export LC_ALL=en_US.UTF-8 && export LANG=en_US.UTF-8		#
echo "export LC_ALL=en_US.UTF-8 && export LANG=en_US.UTF-8 " >>~/.profile #
echo "export LD_LIBRARY_PATH=/usr/local/lib" >>~/.profile 	#
sudo apt-get -y upgrade						#
cd /var/www/html/node/main/libfap-1.5/deb			#
sudo dpkg -i lib*amd64.deb					#
echo								#
echo "Installing the packages required . (LAMP stack)..."	#
echo								#
cd /var/www/html/node/main					#
sudo apt-get install -y mysql-server mysql-client sqlite3	#
sudo apt-get install -y python-dev python-pip python-mysqldb    #
sudo apt-get install -y dos2unix libarchive-dev	 autoconf mc	#
sudo apt-get install -y pkg-config git	mutt npm nodejs		# 
sudo apt-get install -y apache2 php php-mcrypt php-mysql php-cli #
sudo apt-get install -y php-mbstring php-gettext php-json	#
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
sudo pip install ephem pytz geopy configparser			#
cd /var/www/html/						#
sudo npm install websocket socket.io request parsejson	ini	#
sudo npm install forever -g 					#
if [ ! -d /etc/local ]						#
then								#
    sudo mkdir /etc/local					#
fi								#
echo								#
if [ ! -d /var/www/data ]					#
then								#
    sudo mkdir /var/www/data					#
fi								#
if [ ! -d /var/www/html/cuc ]					#
then								#
    sudo mkdir /var/www/html/cuc				#
fi								#
echo								#
if [ ! -f /var/www/html/index.php ]				#
then								#
    sudo ln /var/www/html/node/index.php /var/www/html/index.php #
fi								#
echo "Installing the templates needed  ...." 			#
echo								#
cd /var/www/html/node/main					#
sudo cp config.template /etc/local/APRSconfig.ini		#
cd /var/www/html/node/						#
python genconfig.py						#
mysqladmin -u root password ogn					#
echo "CREATE DATABASE APRSLOG" | mysql -u root -pogn		#
mysql --database APRSLOG -u root -pogn < main/APRSLOG.template.sql	#
echo								#
echo "Optional steps ... "					#
echo								#
cd main								#
mailcatcher --http-ip=0.0.0.0					#
cd sh	 							#
crontab <crontab.data						#
crontab -l 							#
if [ ! -d ~/src  ]						#
then								#
	mkdir ~/src   						#
	mkdir ~/src/APRSsrc					#
	ln -s /var/www/html/node/main ~/src/APRSsrc		#
fi								#
cp *.sh ~/src  							#
cd ..								#
cp *.py ~/src/APRSsrc						#
ls  -la ~/src 							#
if [ ! -d /nfs  ]						#
then								#
	sudo mkdir /nfs						#
	sudo mkdir /nfs/OGN					#
	sudo mkdir /nfs/OGN/APRSdata				#
	sudo chown vagrant:vagrant /nfs/OGN/APRSdata		#
	sudo chmod 777 /nfs/OGN/APRSdata			#
	cd /var/www/html/node/				#
	sudo chown vagrant:vagrant *				# 
	sudo chmod 777 *					#
	sudo chown vagrant:vagrant */*				# 
	sudo chmod 777 */*					#
fi								#
cd								#
sudo dpkg-reconfigure tzdata					#
sudo apt-get -y dist-upgrade					#
sudo apt-get -y autoremove					#
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

