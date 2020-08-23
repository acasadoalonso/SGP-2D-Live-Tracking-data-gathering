FROM docker-registry.azuris.ch:5000/azuris/azphpapp:7.4

RUN apt-get update && apt-get install -y python3 python3-pymysql python3-openssl python3-dev python3-pip libmariadbclient-dev mutt wget python3-rsa python3-psutil

ENV LIBFAP_DOWNLOAD http://www.pakettiradio.net/downloads/libfap/1.5/libfap-1.5.tar.gz
ENV LIBFAP_FILENAME libfap-1.5-tar-gz

RUN set -x \
    && pip3 install --upgrade pip \
    && pip3 install --upgrade setuptools \
    && pip3 install ephem pytz geopy configparser pycountry \
    && pip3 install mysqlclient requests mysql-connector-python beeprint ogn.client \
    && npm install websocket socket.io request parsejson ini \
    && npm install forever -g \
    && curl -fSL "$LIBFAP_DOWNLOAD" -o "$LIBFAP_FILENAME" \
    && mkdir -p /usr/src/libfap \
    && tar -xf "$LIBFAP_FILENAME" -C /usr/src/libfap --strip-components=1 \
    && rm $LIBFAP_FILENAME \
    && cd /usr/src/libfap \
    && ./configure --prefix=/usr \
    && make -j2 \
    && make install \
    && rm -rf /usr/src/libfap

WORKDIR /var/www/

RUN mkdir -p /var/www/public/goaccess
VOLUME /var/www/public/goaccess

