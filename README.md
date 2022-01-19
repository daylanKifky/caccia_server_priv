# CACCIA app server v1.0.0
Tested and running in VPS with Ubuntu Server 18.04 LTS

## WSGI with apache

- Send project to VPS, after setting DEPLOY_VARS.sh
`./deploy.sh`

- Connect with ssh to server and..
`~/install_caccia_apache.sh`

see [here](https://medium.com/@prithvishetty/deploying-a-python-3-flask-app-into-aws-using-apache2-wsgi-1b26ed29c6c2) for more info. 

## Dev installation:

- `pipenv install`

- place firebase.json in `instance` folder

- `pipenv run init`

## Dev sever:

Only local version in port 5000:
- `pipenv run dev_server`

Remote with no reloads in port 5001
- `pipenv run dev_server_remote`