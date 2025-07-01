#!/bin/bash
echo "Running migrations..."
cd /app/backend
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Post-deployment tasks completed successfully." 