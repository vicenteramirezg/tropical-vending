#!/bin/bash

# Change to backend directory
cd backend

# Create and apply migrations
echo "Creating migrations..."
python manage.py makemigrations

echo "Applying migrations..."
python manage.py migrate

# Start development server
echo "Starting backend development server..."
python manage.py runserver 