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

   or

   > docker build -t glidertracking .
		and then run it using the following command
   > docker run -d --link mysql_container:mysql -p8080:80 -p8081:81 -v my_web_dir:/var/www glidertracking
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
6. The DOCKER image does include a SSH server and most of the entrypoint script is related to that.
   If you don't need ssh, you can get rid of all these parts.
   In case you need to start other processes in the image, you can add them near the end of the entrypoint.sh file.

   Use (Dockerfile and entrypoint.sh) in your system, add the /var/www content directly in the image (in Dockerfile), 
   add a few database initialization scripts in the entry point script and your image would be complete for immediate deployment.
