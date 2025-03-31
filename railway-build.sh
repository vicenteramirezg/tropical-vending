#!/bin/bash
set -e

echo "Starting Railway build process..."

# Install frontend dependencies
echo "Installing frontend dependencies..."
cd frontend
npm install

# Build the frontend
echo "Building frontend with production configuration..."
npm run build

# Go back to the root directory
cd ..

# Install backend dependencies
echo "Installing backend dependencies..."
pip install -r requirements.txt

# Collect static files 
echo "Collecting static files..."
cd backend
python manage.py collectstatic --noinput

# Go back to the root directory
cd ..

echo "Railway build process completed successfully!" 