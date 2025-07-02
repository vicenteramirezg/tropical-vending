# Change to backend directory
Set-Location -Path "backend"

# Create and apply migrations
Write-Host "Creating migrations..."
python manage.py makemigrations

Write-Host "Applying migrations..."
python manage.py migrate

# Start development server
Write-Host "Starting backend development server..."
python manage.py runserver 0.0.0.0:8000