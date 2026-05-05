#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py migrate

python manage.py collectstatic --noinput

python manage.py shell -c "
from school.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'Admin1234!')
    print('Superuser created')
else:
    u = User.objects.get(username='admin')
    u.set_password('Admin1234!')
    u.is_superuser = True
    u.is_staff = True
    u.save()
    print('Superuser password reset')
"