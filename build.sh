#!/usr/bin/env bash
# build.sh - Render runs this on every deploy

set -o errexit  # exit on error

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run database migrations
python manage.py migrate

# Create superuser if it doesn't exist (optional)
python manage.py shell << 'EOF'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@brightpath.com', 'Admin@1234!')
    print('Superuser created.')
else:
    print('Superuser already exists.')
EOF