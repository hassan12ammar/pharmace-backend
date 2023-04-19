#!/bin/bash

# remove old migrations
find . -path "*/auth_profile/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/core/migrations/*.py" -not -name "__init__.py" -delete

# remove old DataBase
rm db.sqlite3

# Activate the virtual environment
source pharmace_venv/bin/activate

# make & apply new migrations
python manage.py makemigrations
python manage.py migrate

# create superuser
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('mg@gm.com', 'string12')" | python manage.py shell

# crate seed
curl -X 'POST' \
  'http://127.0.0.1:8000/api/draft/create_seed' \
  -H 'accept: application/json' \
  -d ''