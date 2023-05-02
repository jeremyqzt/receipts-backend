# receipts

This project is intended to read and store receipts.

## Building the project
Use following commands to build

### Docker
```
./buildBE.sh 
./buildFE.sh
```

### Docker using arm

```
./buildBE.sh arm
```

## Running the project

### create a venv and running the backend
```
python3 -m venv ./.venv
source .venv/bin/activate
pip install -r requirements.txt
cd receipts
python manage.py runserver 0.0.0.0:8000
```

Set up the front-end by checking out this repo: https://github.com/jeremyqzt/ribbon-ui

### Connecting to GCP

You will need a environment file consisting of the following items (it has to be sourced before running the backend):
```
export USE_GS="FALSE"
export USE_CLOUD_SQL="FALSE"

export GS_SECRET="..."
export GS_ACCESS_KEY="..."

export GOOGLE_APPLICATION_CREDENTIALS="....../receipts/ribbon-receipts-*.json"

export DATABASE_NAME="receiptsdb"
export DATABASE_USER="ribbon-receipts-db"
export DATABASE_PASSWORD="...."

export SECRET_KEY="ANY THING HERE IS GOOD"
```

Create a service account to get the `GOOGLE_APPLICATION_CREDENTIALS` and check the other fields inside GCP

## Commands
Run this command before starting the app.

```
cloud_sql_proxy -instances="ribbon-receipts:us-east4:ribbon-receipts-db"=tcp:5432
```

## Running the backend
Assuming you're in the django directory
```
source ../.venv/bin/activate
python manage.py runserver
```

## Running the front end
Assuming you're in front-end directory
```
nvm i
npm start
```
