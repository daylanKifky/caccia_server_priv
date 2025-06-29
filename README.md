# CACCIA app server v1.0.0
Tested and running in VPS with Ubuntu Server 18.04 LTS

## System Dependencies

Install required system packages for Cairo:
```bash
sudo apt install libapr1 libaprutil1 libxcb-cursor0 libxcb-damage0
```

## Installation

Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:
```bash
pip install -e .
```

## Configuration

- Place `firebase.json` in `instance` folder, rename `FIREBASE_CONF` value in `__init__.py`
- Place `firebaseConfig.js` in `caccia_server/static` folder

## Initialize Database

```bash
export FLASK_APP=caccia_server
export FLASK_ENV=development
flask init-db
```

## Development Server

Local server (port 5000):
```bash
export FLASK_APP=caccia_server
export FLASK_ENV=development
flask run
```

Remote server (port 5001):
```bash
export FLASK_APP=caccia_server
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5001 --no-reload
```