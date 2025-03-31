#!/bin/bash
set -e

echo "Starting Railway deployment..."

# Go to the backend directory
cd backend

# Start Gunicorn server
echo "Starting Gunicorn server..."
gunicorn vendingapp.wsgi:application --workers 2 --timeout 120 --bind 0.0.0.0:$PORT --log-level debug 