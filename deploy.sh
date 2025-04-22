#!/bin/bash

if [ ! -f ./DEPLOY_VARS.sh ]; then
    echo "File DEPLOY_VARS.sh not found, aborting.."
    exit
fi

source DEPLOY_VARS.sh

if [ -z $DEST_ADDR ] || [ -z $DEST_PATH ]; then
	echo '$DEST_ADDR or $DEST_PATH not defined in DEPLOY_VARS.sh'
	echo aborting..
	exit
fi

echo creating requeriments.txt
pipenv lock -r > caccia_server/requirements.txt

echo sending to $DEST_ADDR:$DEST_PATH
echo press a key to continue..
read -n1
rsync -e "ssh -i ../caccia_server_key.pem" \
	-av . $DEST_ADDR:$DEST_PATH\
	--exclude-from=exclude_deploy 