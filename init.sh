#!/bin/sh

MYSQL_CMD='mysql -uroot -S /usr/local/var/mysql/mysql.sock '

${MYSQL_CMD} -e "drop database if exists srv"
${MYSQL_CMD} -e "create database srv"
~/.pyenv/versions/srv-3.3.3/bin/python manage.py init

# IP
${MYSQL_CMD} srv -e "insert into ip (ip, is_used) values ('192.168.1.101', 1)"
${MYSQL_CMD} srv -e "insert into ip (ip, is_used) values ('192.168.1.102', 1)"
${MYSQL_CMD} srv -e "insert into ip (ip, is_used) values ('192.168.1.103', 1)"
${MYSQL_CMD} srv -e "insert into ip (ip, is_used) values ('192.168.1.111', 1)"
${MYSQL_CMD} srv -e "insert into ip (ip, is_used) values ('192.168.1.112', 1)"
${MYSQL_CMD} srv -e "insert into ip (ip, is_used) values ('192.168.1.113', 1)"
${MYSQL_CMD} srv -e "insert into ip (ip, is_used) values ('192.168.1.121', 1)"
${MYSQL_CMD} srv -e "insert into ip (ip, is_used) values ('192.168.1.122', 0)"
${MYSQL_CMD} srv -e "insert into ip (ip, is_used) values ('192.168.1.100', 1)"

# role
${MYSQL_CMD} srv -e "insert into role (role_name) values ('web')"
${MYSQL_CMD} srv -e "insert into role (role_name) values ('app')"
${MYSQL_CMD} srv -e "insert into role (role_name) values ('db')"
${MYSQL_CMD} srv -e "insert into role (role_name) values ('session')"
${MYSQL_CMD} srv -e "insert into role (role_name) values ('cache')"
${MYSQL_CMD} srv -e "insert into role (role_name) values ('vip')"

# host
${MYSQL_CMD} srv -e "insert into host (host_name, ip, created_at, updated_at) values ('web01', '192.168.1.101', now(), now())"
${MYSQL_CMD} srv -e "insert into host (host_name, ip, created_at, updated_at) values ('web02', '192.168.1.102', now(), now())"
${MYSQL_CMD} srv -e "insert into host (host_name, ip, created_at, updated_at) values ('web03', '192.168.1.103', now(), now())"
${MYSQL_CMD} srv -e "insert into host (host_name, ip, created_at, updated_at) values ('db01', '192.168.1.111', now(), now())"
${MYSQL_CMD} srv -e "insert into host (host_name, ip, created_at, updated_at) values ('db02', '192.168.1.112', now(), now())"
${MYSQL_CMD} srv -e "insert into host (host_name, ip, created_at, updated_at) values ('db03', '192.168.1.113', now(), now())"
${MYSQL_CMD} srv -e "insert into host (host_name, ip, created_at, updated_at) values ('mem01', '192.168.1.121', now(), now())"
${MYSQL_CMD} srv -e "insert into host (host_name, ip, created_at, updated_at) values ('vip01', '192.168.1.100', now(), now())"

# role_map
${MYSQL_CMD} srv -e "insert into role_map (host_name, role_name) values ('web01', 'web')"
${MYSQL_CMD} srv -e "insert into role_map (host_name, role_name) values ('web01', 'app')"
${MYSQL_CMD} srv -e "insert into role_map (host_name, role_name) values ('web02', 'web')"
${MYSQL_CMD} srv -e "insert into role_map (host_name, role_name) values ('web02', 'app')"
${MYSQL_CMD} srv -e "insert into role_map (host_name, role_name) values ('web03', 'web')"
${MYSQL_CMD} srv -e "insert into role_map (host_name, role_name) values ('web03', 'app')"
${MYSQL_CMD} srv -e "insert into role_map (host_name, role_name) values ('db01', 'db')"
${MYSQL_CMD} srv -e "insert into role_map (host_name, role_name) values ('db02', 'db')"
${MYSQL_CMD} srv -e "insert into role_map (host_name, role_name) values ('db03', 'db')"
${MYSQL_CMD} srv -e "insert into role_map (host_name, role_name) values ('mem01', 'session')"
${MYSQL_CMD} srv -e "insert into role_map (host_name, role_name) values ('mem01', 'cache')"
${MYSQL_CMD} srv -e "insert into role_map (host_name, role_name) values ('vip01', 'vip')"

