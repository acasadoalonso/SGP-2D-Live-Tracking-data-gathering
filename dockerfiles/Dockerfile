#FROM docker-registry.azuris.ch:5000/azuris/azphpapp:7.4
FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive 
RUN apt-get update && apt-get -y upgrade 
RUN apt-get install -y apt-utils
RUN apt-get install -y software-properties-common 		
RUN apt-get install -y python3-software-properties 		
RUN apt-get install -y build-essential 			
RUN apt-get install -y language-pack-en-base 
RUN export LC_ALL=en_US.UTF-8 && export LANG=en_US.UTF-8	
RUN apt-get install -y python3 python3-pymysql python3-openssl python3-dev python3-pip 
RUN apt-get install -y libmariadbclient-dev mutt wget 
RUN apt-get install -y python3-rsa python3-psutil iproute2 systemd npm git
RUN apt-get install -y dos2unix libarchive-dev  autoconf mc    
RUN apt-get install -y pkg-config nodejs vim inetutils-ping 
RUN apt-get install -y figlet 
RUN apt-get install -y apache2 php 				
RUN apt-get install -y php-sqlite3 php-mysql php-cli 	
RUN apt-get install -y php-mbstring php-json	
RUN apt-get install -y php7.4					
RUN apt-get install -y ntpdate				
RUN apt-get install -y ssh sudo				
RUN apt-get install -y libmysqlclient-dev 			
RUN apt-get install -y sqlite3 libsqlite3-dev mysql-client 
RUN a2enmod rewrite						
RUN phpenmod mbstring		
RUN git config --global user.email "acasadoalonso@gmail.com" 
RUN git config --global user.name "Angel Casado"     
RUN set -x \
    && pip3 install --upgrade pip \
    && pip3 install --upgrade setuptools \
    && pip3 install ephem pytz geopy configparser pycountry \
    && pip3 install mysqlclient requests mysql-connector-python beeprint ogn.client \
    && pip3 install tqdm psutil rsa				\
    && pip3 install --force-reinstall --no-binary mysqlclient mysqlclient        \ 
    && npm install websocket socket.io request parsejson ini    \
    && npm install forever -g 

WORKDIR /var/www/

RUN git clone https://github.com/acasadoalonso/SGP-2D-Live-Tracking.git 	public
RUN git clone https://github.com/acasadoalonso/SGP-2D-Live-Tracking-data-gathering.git	public/main
RUN mkdir -p /var/www/public
RUN mkdir -p /var/www/public/main
RUN mkdir -p /var/www/data
RUN mkdir -p /var/www/local
RUN mkdir -p /var/www/src
VOLUME /var/www/public/
VOLUME /var/www/local/
VOLUME /var/www/data/
VOLUME /var/www/src/
RUN ln -s /var/www/public /var/www/html/node
RUN apt-get install -y percona-toolkit				
RUN dpkg-reconfigure tzdata					
RUN echo "ServerName APRSLOG" >> /etc/apache2/apache2.conf
RUN apt-get -y dist-upgrade					
RUN apt-get -y autoremove	
ARG USER=angel
ARG UID=1000
ARG GID=1000
# default password for user
ARG PW=docker
# Option1: Using unencrypted password/ specifying password
RUN useradd -m ${USER} --uid=${UID} --shell=/bin/bash && echo "${USER}:${PW}" | \
      chpasswd
RUN echo "Welcome to the APRSLOG application container" > /etc/motd \
    && cp -a /root /root.orig
EXPOSE 80
EXPOSE 81
EXPOSE 22
RUN touch APRSinstallation.done	
ENTRYPOINT  service ssh start && service apache2 start &&  /bin/bash
