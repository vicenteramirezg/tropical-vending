#!/bin/bash

# Apply database migrations
echo "Applying database migrations..."
cd /app/backend
python manage.py migrate --noinput

# Start server
echo "Starting server..."
gunicorn vendingapp.wsgi --bind 0.0.0.0:$PORT --log-file - 