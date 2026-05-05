#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py migrate

python manage.py collectstatic --noinput

python manage.py shell -c "
from school.models import User
if not User.objects.filter(username='flash').exists():
    User.objects.create_superuser('flash', 'flash@example.com', '48rewc23')
    print('Superuser created')
else:
    print('Superuser already exists')
"