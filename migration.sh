#!/bin/bash

find . -path "*/auth_profile/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/core/migrations/*.py" -not -name "__init__.py" -delete

rm db.sqlite3

python manage.py makemigrations

python manage.py migrate

echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('mg@gm.com', 'string12')" | python manage.py shell