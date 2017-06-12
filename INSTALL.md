## Development Setup
1. Install [VirtualBox](https://www.virtualbox.org/wiki/Downloads) and [Vagrant](https://www.vagrantup.com/)

2. Clone and run [Scotch Box](https://box.scotch.io/), a full-featured development environment for php
   ```
   git clone https://github.com/scotch-io/scotch-box.git APRS
   cd SWIFACE
   vagrant up

   or

   mkdir APRS
   cd    APRS
   vagrant init ubuntu/xenial64
   vagrant up
   ```

3. Clone APRS repository into the webroot of the Scotch Box
   ```
   rm ./public/index.php
   mkdir public
   cd public
   git clone https://github.com/acasadoalonso/SGP-2D-Live-Tracking 			node
   git clone https://github.com/acasadoalonso/SGP-2D-Live-Tracking-data-gathering     	node/main
   ln -s public html
   vagrant ssh
   # The following commands get executed in the vm
   do-release-upgrade
   cd /var/www/public/node/main
   bash install.sh
   cd ~/src
   bash APRSlive
   ```

4. Access your local APRSLOG instance at [192.168.33.10](http://192.168.33.10)

5. (optional, for email debugging) Run [MailCatcher](http://mailcatcher.me/), accessible at [192.168.33.10](http://192.168.33.10:1080)
   ```
   vagrant@scotchbox:~$ mailcatcher --http-ip=0.0.0.0
   composer update
   ```

