# host-management-app

This is a IP address and host administration tool using flask and angular.js.
This project is created for my angular.js study :)

* Python 3.3
* Flask
* SQLAlchemy
* MySQL
* Angular.js

## Installation

### This application

```
git clone https://github.com/hiroakis/host-management-app.git
cd host-management-app
pip install -r requirements.txt
cd view
bower install
```

### httpd

Move view directory to document root on your httpd and edit view/static/js/app.js following line.

```
var api = 'http://localhost:8080';
```

* nginx.conf

view/nginx.conf.example

### MySQL

Install MySQL and edit srvadm/config.py

```
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://srv:srv@localhost/srv?charset=utf8'
```

Create database schema and user to connect.

```
/etc/init.d/mysql start
mysql -uroot -e "create database srv"
mysql -uroot -e "grant all privileges on srv.* to 'srv'@'localhost' identified by 'srv';
```

### start application

```
python manage.py run
```

### insert sample data

```
sh init.sh
```

## screen shot

![](screenshot.png?raw=true)

## License

MIT.

