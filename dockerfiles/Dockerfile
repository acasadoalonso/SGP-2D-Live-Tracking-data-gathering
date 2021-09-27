FROM debian
ENV DEBIAN_FRONTEND=noninteractive 
RUN apt-get update && apt-get -y upgrade 
RUN apt-get install -y apt-utils software-properties-common python3-software-properties	 build-essential 
RUN export LC_ALL=en_US.UTF-8 && export LANG=en_US.UTF-8	
RUN apt-get install -y python3 python3-pymysql python3-mysqldb python3-openssl python3-dev python3-pip mutt wget python3-rsa python3-psutil iproute2 systemd git libarchive-dev  autoconf mc pkg-config vim inetutils-ping figlet ntpdate ssh sudo openssh-server sqlite3 libsqlite3-dev mariadb-client percona-toolkit				
RUN git config --global user.email "acasadoalonso@gmail.com" 
RUN git config --global user.name "Angel Casado"     
RUN set -x \
    && pip3 install --upgrade pip \
    && pip3 install --upgrade setuptools \
    && pip3 install ephem pytz geopy configparser pycountry \
    && pip3 install requests mysql-connector-python beeprint ogn.client \
    && pip3 install tqdm psutil rsa mysqlclient

WORKDIR /var/www/

RUN git clone https://github.com/acasadoalonso/SGP-2D-Live-Tracking-data-gathering.git	main
RUN mkdir -p /var/www/public
RUN mkdir -p /nfs
RUN mkdir -p /nfs/OGN/
RUN mkdir -p /nfs/OGN/SWdata
RUN mkdir -p /etc/local
VOLUME /var/www/public/
VOLUME /etc/local
VOLUME /nfs
COPY config.docker /etc/local/APRSconfig.ini

ENV TZ=Europe/Madrid
RUN dpkg-reconfigure tzdata                             
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone  
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

RUN  service ssh start 
RUN chmod 0755 /var/run/sshd

RUN echo "Welcome to the SWS application container" > /etc/motd \
    && cp -a /root /root.orig


# Clean up APT when done.

RUN apt-get clean && rm -rf /var/lib/apt/lists/* 


#ENTRYPOINT  service ssh start && service apache2 start &&  /bin/bash
RUN  service ssh start 
WORKDIR /var/www/main/
CMD ["/usr/bin/python3", "aprslog.py", "--MEM","TRUE","--STATIONS","TRUE","--LASTFIX","TRUE" ] 

