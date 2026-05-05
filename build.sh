#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py migrate

python manage.py collectstatic --noinput

python manage.py shell -c "
from school.models import User
print('All users:', list(User.objects.values('username', 'is_superuser', 'is_staff', 'is_active')))
u, created = User.objects.get_or_create(username='admin')
u.set_password('Admin1234!')
u.is_superuser = True
u.is_staff = True
u.is_active = True
u.save()
print('Done. Created:', created)
"