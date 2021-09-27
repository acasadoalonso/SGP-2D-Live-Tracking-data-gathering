FROM debian
RUN apt update -y && apt install mariadb-server -y
RUN sed -i 's/bind-address/bind-address = 0.0.0.0 #/i' /etc/mysql/mariadb.conf.d/50-server.cnf
RUN mkdir /mysql_scripts
COPY mySqlScript.sql /mysql_scripts/
RUN /etc/init.d/mariadb start && mysql -uroot --password="" -e "source /mysql_scripts/mySqlScript.sql"
CMD /etc/init.d/mariadb start && tail -f /dev/null

