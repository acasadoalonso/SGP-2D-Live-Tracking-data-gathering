docker run --net mynetsql --ip 172.18.0.3 --name phpmyadmin -d --link mariadb -e PMA_HOST=mariadb -p 8082:80 --restart unless-stopped phpmyadmin/phpmyadmin 

