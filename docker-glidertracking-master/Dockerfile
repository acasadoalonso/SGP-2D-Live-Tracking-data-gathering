FROM docker-registry.azuris.ch:5000/azuris/azphpapp:7.4

RUN apt-get update && apt-get install -y python3 python3-pymysql python3-openssl python3-dev python3-pip libmariadbclient-dev mutt wget python3-rsa python3-psutil

RUN set -x \
    && pip3 install --upgrade pip \
    && pip3 install --upgrade setuptools \
    && pip3 install ephem pytz geopy configparser pycountry \
    && pip3 install mysqlclient requests mysql-connector-python beeprint ogn.client \
    && npm install websocket socket.io request parsejson ini \
    && npm install forever -g 

WORKDIR /var/www/

RUN git clone https://github.com/acasadoalonso/SGP-2D-Live-Tracking.git 					public
VOLUME /var/www/public/
RUN cd /var/www/public && git clone https://github.com/acasadoalonso/SGP-2D-Live-Tracking-data-gathering.git 	main
VOLUME /var/www/public/main
RUN ls -la /var/www/public/main
