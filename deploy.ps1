#!/usr/bin/env pwsh
# Deployment script for Tropical Vending project

# Stop on errors
$ErrorActionPreference = "Stop"

Write-Host "Starting deployment process..." -ForegroundColor Green

# Navigate to frontend directory and build
Write-Host "Building frontend..." -ForegroundColor Cyan
Push-Location -Path "frontend"
npm install
if ($LASTEXITCODE -ne 0) {
    Write-Host "npm install failed!" -ForegroundColor Red
    exit $LASTEXITCODE
}

npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "Frontend build failed!" -ForegroundColor Red
    exit $LASTEXITCODE
}
Pop-Location

# Copy and modify the Vite-generated index.html file to use Django template tags
Write-Host "Preparing Django template for frontend..." -ForegroundColor Cyan
$indexContent = Get-Content -Path "backend/static/index.html" -Raw
$indexContent = $indexContent -replace 'src="/assets/', 'src="{% static ''assets/'
$indexContent = $indexContent -replace 'href="/assets/', 'href="{% static ''assets/'
$indexContent = $indexContent -replace '.js"', '.js'' %}"'
$indexContent = $indexContent -replace '.css"', '.css'' %}"'
$indexContent = "{% load static %}`n" + $indexContent

# Ensure templates directory exists
if (!(Test-Path "backend/templates")) {
    New-Item -Path "backend/templates" -ItemType Directory
}

# Write the modified content to the Django template
$indexContent | Out-File -FilePath "backend/templates/index.html" -Encoding utf8

# Navigate to backend directory and collect static files
Write-Host "Collecting static files..." -ForegroundColor Cyan
Push-Location -Path "backend"
python manage.py collectstatic --noinput
if ($LASTEXITCODE -ne 0) {
    Write-Host "Collecting static files failed!" -ForegroundColor Red
    exit $LASTEXITCODE
}
Pop-Location

# Git operations
Write-Host "Committing and pushing changes..." -ForegroundColor Cyan

# Get commit message from parameter or use default
$commitMessage = if ($args[0]) { $args[0] } else { "Deployment update" }

git add .
git commit -m $commitMessage
if ($LASTEXITCODE -ne 0) {
    Write-Host "Git commit failed!" -ForegroundColor Red
    exit $LASTEXITCODE
}

git push origin main
if ($LASTEXITCODE -ne 0) {
    Write-Host "Git push failed!" -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "Deployment completed successfully!" -ForegroundColor Green 