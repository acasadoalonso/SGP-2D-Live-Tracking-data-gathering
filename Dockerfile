FROM alpine:edge

RUN echo http://nl.alpinelinux.org/alpine/edge/testing >> /etc/apk/repositories

RUN apk add --no-cache coreutils mysql-client sqlite py2-pip py-mysqldb python2-dev libarchive-dev pkgconf git apache2 php7 php7-mcrypt php7-mysqli php7-mysqlnd php7-apache2 php7-mbstring php7-gettext php7-json nodejs-npm busybox-initscripts openssh-server bash exim exim-dbmdb shadow mutt dos2unix mc openssh rsync
ENV COMPILE_DEPS autoconf file g++ gcc libc-dev make pkgconf curl

ENV LIBFAP_DOWNLOAD http://www.pakettiradio.net/downloads/libfap/1.5/libfap-1.5.tar.gz
ENV LIBFAP_FILENAME libfap-1.5-tar-gz

RUN set -x \
    && apk add --no-cache --virtual .build-deps $COMPILE_DEPS \
    && pip install ephem pytz geopy configparser pycountry \
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
    && rm -rf /usr/src/libfap \
    && apk del .build-deps

RUN mkdir /run/apache2 \
    && chown apache /run/apache2 \
    && echo "ServerName localhost" >> /etc/apache2/httpd.conf \
    && sed -i 's/#LoadModule rewrite_module/LoadModule rewrite_module/' /etc/apache2/httpd.conf \
    && sed -i 's/www\/localhost\/htdocs/www\/public/g' /etc/apache2/httpd.conf  \
    && sed -i 's/ScriptAlias \/cgi-bin/#ScriptAlias \/cgi-bin/' /etc/apache2/httpd.conf \
    && sed -i 's/ServerRoot \/var\/www/ServerRoot \/etc\/apache2/' /etc/apache2/httpd.conf \
    && ln -s /var/log/apache2 /etc/apache2/logs && rm /var/www/logs \
    && ln -s /usr/lib/apache2 /etc/apache2/modules && rm /var/www/modules \
    && ln -s /run/apache2 /etc/apache2/run && rm /var/www/run \
    && mv /var/www/localhost/htdocs /var/www/public \
    && rm -rf /var/www/localhost \
    && cp -a /etc/php7/conf.d /etc/php7/conf.d.orig
    
RUN echo "Welcome to the glidertraking application container" > /etc/motd \
    && cp -a /root /root.orig

RUN mkdir /var/log/exim \
    && chown exim /var/log/exim

WORKDIR /var/www/

EXPOSE 80
EXPOSE 81
EXPOSE 22

COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
