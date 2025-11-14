#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "Waiting for postgres..."

# Wait for database to be ready
while ! nc -z ${DB_HOST:-db} ${DB_PORT:-5432}; do
  sleep 0.1
done

echo "PostgreSQL started"

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Create superuser if it doesn't exist (optional)
echo "Creating superuser if needed..."
python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', '${DJANGO_SUPERUSER_PASSWORD:-admin123}')
    print('Superuser created')
else:
    print('Superuser already exists')
END

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start server
echo "Starting server..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3