#!/bin/bash

# remove old migrations
find . -path "*/auth_profile/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/core/migrations/*.py" -not -name "__init__.py" -delete

# remove old DataBase
rm db.sqlite3

# Create virtual environment if not created 
if [ ! -d "pharmace_venv" ]; then
    python -m venv pharmace_venv
fi

# Activate the virtual environment
source pharmace_venv/bin/activate

# Install requirements packages
pip install -r requirements.txt

# make & apply new migrations
python manage.py makemigrations
python manage.py migrate

# create superuser
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('mg@gm.com', 'string12')" | python manage.py shell

# Define a function to stop the server processes
function stop_server() {
    echo "Stopping server..."
    # Find all processes listening on port 8000
    pids=$(lsof -i :8000 | awk 'NR>1 {print $2}')
    # Kill each process
    for pid in $pids; do
      echo "Killing process $pid..."
      kill $pid
    done
    exit
}

# Run Django development server
python manage.py runserver &

# Wait for the server to start
sleep 8

# crate seed
curl -X 'POST' \
  'http://127.0.0.1:8000/api/draft/create_seed' \
  -H 'accept: application/json'y

# Stop the server process on Ctrl+C
trap stop_server SIGINT

# Wait for the server to be stopped
wait