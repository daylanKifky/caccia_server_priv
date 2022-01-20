#!/bin/bash

set -eu 
echo "= Installing deps"

sudo apt update
sudo apt install -y  apache2 libapache2-mod-wsgi-py3 python3-venv sqlite3 unzip lib32ncurses5 lib32z1

echo "= Upgrading SQLITE3"
wget -q -O tmp.zip https://sqlite.org/2020/sqlite-tools-linux-x86-3330000.zip && unzip tmp.zip && rm tmp.zip
DIRNAME=$(which sqlite3)
DIRNAME=$(dirname $DIRNAME)
sudo mv sqlite-tools-linux-*/* $DIRNAME
echo SQLITE3 upgraded to version: $(sqlite3 --version)
rm -rf sqlite-tools-linux-*

# UPGRADING python sqlite3 with custom pre-compiled shared libraries
# The installation dir is determinated by running:
# > PYSQLITE=$(python3 -c "import _sqlite3; print(_sqlite3.__file__)")
# > readelf -d $PYSQLITE
# > objdump -x $PYSQLITE | grep PATH
# Search for the .so in the sytem or shared library RPATH
# Normally is in /usr/lib/x86_64-linux-gnu/libsqlite3.so.0

SHLIBDIR=/usr/lib/x86_64-linux-gnu
sudo cp sqlite_3-34-0/libsqlite3.* $SHLIBDIR

echo "= Creating folders"
INSTALL_DIR=/var/www/flask_sites
mkdir -p $INSTALL_DIR
sudo chown -R $USER:$USER /var/www
rm -rf $INSTALL_DIR/*
cp -r ~/caccia_server $INSTALL_DIR

echo "= Creating convenience VARS"
echo "alias cp-caccia='sudo cp -r ~/caccia_server $INSTALL_DIR'" >> ~/.bashrc

echo "= Init venv"
cd $INSTALL_DIR
echo creating virtual env in: $PWD
python3 -m venv venv
venv/bin/pip install --upgrade pip
venv/bin/pip install -r caccia_server/requirements.txt

echo "= Init DB"
echo "Instance folder in $PWD"
export FLASK_APP=caccia_server
rm -rf instance *.sqlite
cp -r ~/instance $INSTALL_DIR
venv/bin/flask init-db

#comment-out these lines for production!
echo "= Creating fake users"
venv/bin/flask create-fake-users 100
echo 'DEBUG=True' > $INSTALL_DIR/instance/config.py

echo "= Configure Apache"
sudo a2enmod rewrite
sudo a2enmod ssl
cd $INSTALL_DIR/caccia_server
mv server_conf/caccia_server.wsgi $INSTALL_DIR
sudo mv server_conf/001-caccia_server.conf /etc/apache2/sites-available/000-default.conf
sudo mv server_conf/001-caccia_server-ssl.conf /etc/apache2/sites-available/000-default-ssl.conf
sudo a2ensite 000-default-ssl.conf
sudo service apache2 restart

echo "= Cleanup"
sudo chown -R www-data:www-data /var/www
rm -rf ~/caccia_server
rm -rf ~/instance

echo "= Installation Done"
echo "== NOTE =="
echo "The SSL certificates and configuration were not automatically installed."
echo "They should be placed in:"
echo "/etc/letsencrypt/options-ssl-apache.conf"
echo "/etc/letsencrypt/live/api.######.com/fullchain.pem"
echo "/etc/letsencrypt/live/api.######.com/privkey.pem"
echo "and automatic renew should be configured using certbot"
echo "run \`systemctl list-timers | grep certbot\` to confirm auto-renew is set"
