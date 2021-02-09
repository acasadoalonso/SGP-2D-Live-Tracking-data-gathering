#!/bin/bash 
echo " "							#
echo "Install APRSLOG  ...." 					#
echo "=================================================="	#
echo " "							#
if [ $# = 0 ]; then						#
	sql='NO'						#
        server=mariadb						#
else								#
	sql=$1						        #
        server=localhost					#
fi								#
if [ ! -f /tmp/commoninstall.sh ]				#
then								#
   echo "=============================="			#
   echo "Installing the common software"			#
   echo "=============================="			#
   bash commoninstall.sh $sql					#
fi								#
echo " "							#
echo "Restart APACHE2  ...." 					#
echo "=================================================="	#
echo " "							#
cd /var/www/html/main						#
sudo cat /etc/apache2/apache2.conf html.dir 	>>temp.conf	#
sudo echo "ServerName APRSLOG " >>temp.conf			#
sudo mv temp.conf /etc/apache2/apache2.conf			#
sudo service apache2 restart					#
echo "=================================================="	#
cd /var/www/html/						#
echo " "							#
echo "=================================================="	#
echo "Install npm modules ...." 				#
echo "=================================================="	#
echo " "							#
sudo apt-get -y install npm nodejs                              #
sudo npm install -g npm 					#
sudo npm install websocket socket.io request parsejson	ini	#
sudo npm install forever -g 					#
echo "=================================================="	#
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
echo "=================================================="	#
echo "Installing the templates needed  ...." 			#
echo "=================================================="	#
echo " "							#
echo								#
cd /var/www/html/main						#
sudo cp config.template /etc/local/APRSconfig.ini		#
echo "=================================================="	#
cd /var/www/html/						#
python3 genconfig.py						#
if [ ! -f /tmp/GLIDERS.sql ]					#
then								#
	cd /tmp							#
	wget acasado.es:60080/files/GLIDERS.sql			#
fi								#
cd /var/www/html/main						#
if [ $sql = 'MySQL' ]						#
then			
        sudo service mysql start				#
        echo "================================================"	#
        echo "Running msqladmin .... assign root password ... "	#
        echo "================================================"	#
        sudo mysqladmin -u root password ogn			#
        echo "Create the APRSogn login-path: Type assigned password"	
	mysql_config_editor set --login-path=APRSogn --user=ogn --password
        sudo service mysql start				#
else								#
        echo "================================================"	#
        echo "Running mariadb .... ... "	 		#
        echo "================================================"	#
        sudo apt install -y mariadb-server			#
        sudo service mariadb start				#
fi								#
cp doc/.my.cnf ~/						#
echo "Create database APRSLOG ..."				#
if [ $sql = 'MySQL' ]						#
then								#
    echo "Create DB user ogn ..."				#
    sudo mysql  <doc/adduser.sql				#
    echo "CREATE DATABASE if not exists APRSLOG" | mysql --login-path=APRSogn	#
    mysql --login-path=APRSogn --database APRSLOG < APRSLOG.template.sql #
    mysql --login-path=APRSogn --database APRSLOG </tmp/GLIDERS.sql
else								#
    echo "Create DB user ogn ..."				#
    sudo mysql -u root -pogn -h $server <doc/adduser.sql	#
    echo "CREATE DATABASE if not exists APRSLOG" | mysql -u ogn -pogn -h $server
    mysql -u ogn -pogn -h $server --database APRSLOG < APRSLOG.template.sql  #
    mysql -u ogn -pogn -h $server --database APRSLOG </tmp/GLIDERS.sql
fi								#
cd /var/www/html/main						#
if [ $sql = 'docker' ]						#
then								#
   echo "CREATE DATABASE if not exists APRSLOG" | sudo mysql -u ogn -pogn -h MARIADB
   echo "SET GLOBAL log_bin_trust_function_creators = 1; " | sudo mysql -u ogn -pogn -h MARIADB
   sudo mysql -u ogn -pogn -h MARIADB --database APRSLOG < APRSLOG.template.sql  
   sudo mysql -u ogn -pogn -h MARIADB --database APRSLOG </tmp/GLIDERS.sql
fi								#
sudo rm -f /tmp/GLIDERS.sql*					#
echo								#
echo "==================="					#
echo "Optional steps ... "					#
echo "==================="					#
echo								#
cd sh	 							#
if [ -f crontab.data ]						#
then 								#
     	echo							#
     	echo "Set the crontab ... "				#
     	echo							#
     	crontab -u vagrant crontab.data				#
     	crontab -u vagrant -l 					#
fi								#
if [ ! -d ~/src  ]						#
then								#
     	echo							#
     	echo "Set the src dir ... "				#
     	echo							#
	mkdir ~/src   						#
	mkdir ~/src/APRSsrc					#
	ln -s /var/www/html/main ~/src/APRSsrc			#
fi								#
ls  -la ~/src 							#
if [ ! -d /nfs  ]						#
then								#
     	echo							#
     	echo "Set the NFS dir ... "				#
     	echo							#
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
echo ""								#
echo "========================================================================================================"	#
echo ""								#
cd /var/www/html/main						#
if [ ! -d opensky-api ]						#
then								#
   git clone https://github.com/openskynetwork/opensky-api.git  #
   cd opensky-api						#
   sudo -H pip3 install -e python/.                             #
fi								#
cd ..								#
touch APRSinstallation.done					#
echo ""								#
echo "========================================================================================================"	#
echo "Installation done ..."											#
echo "Review the configuration file on /etc/local ..."								#
echo "Review the configuration of the crontab and the shell scripts on ~/src " 					#
echo "In order to execute the APRSLOG data crawler execute:  bash ~/src/APSRlive.sh " 				#
echo "Check the placement of the RootDocument on APACHE2 ... needs to be /var/www/html	"			#
echo "If running in Windows under Virtual Box, run dos2unix on /var/www/html  main  src		"		#
echo "Install phpmyadmin if needed !!!                                                           "              #
echo "========================================================================================================"	#
echo ""								#
echo ""								#
echo ""								#
bash
alias

