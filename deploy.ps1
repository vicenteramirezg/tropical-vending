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

# Make sure we have the Vite output in the backend/static directory
Write-Host "Copying Vite assets..." -ForegroundColor Cyan 
if (!(Test-Path "backend/static/assets")) {
    Write-Host "Creating assets directory..." -ForegroundColor Yellow
    New-Item -Path "backend/static/assets" -ItemType Directory -Force
}

# Copy and modify the Vite-generated index.html file to use Django template tags
Write-Host "Preparing Django template for frontend..." -ForegroundColor Cyan
$indexContent = Get-Content -Path "backend/static/index.html" -Raw
$indexContent = $indexContent -replace 'src="/assets/', 'src="{% static ''assets/'
$indexContent = $indexContent -replace 'href="/assets/', 'href="{% static ''assets/'
$indexContent = $indexContent -replace '.js"', '.js'' %}"'
$indexContent = $indexContent -replace '.css"', '.css'' %}"'
$indexContent = $indexContent -replace 'href="/vite.svg"', 'href="{% static ''vite.svg'' %}"'
$indexContent = "{% load static %}`n" + $indexContent

# Ensure templates directory exists
if (!(Test-Path "backend/templates")) {
    New-Item -Path "backend/templates" -ItemType Directory -Force
}

# Write the modified content to the Django template
$indexContent | Out-File -FilePath "backend/templates/index.html" -Encoding utf8

# Create a custom index.html file for Railway deployment troubleshooting
$debugContent = @"
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Debug - Tropical Vending</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
    h1 { color: #333; }
    .debug-info { background: #f4f4f4; padding: 15px; border-radius: 5px; }
    pre { background: #eee; padding: 10px; overflow: auto; }
  </style>
</head>
<body>
  <h1>Tropical Vending - Debug Page</h1>
  <div class="debug-info">
    <p>If you're seeing this page, the Django server is working but might be having trouble serving the Vue.js assets.</p>
    <p>Static URL: {% verbatim %}{{ STATIC_URL }}{% endverbatim %}</p>
    <p>Available static files should be in: <code>/staticfiles/</code></p>
    <p>Try accessing: <a href="/static/assets/index-CTXLI329.js">/static/assets/index-CTXLI329.js</a></p>
  </div>
</body>
</html>
"@

$debugContent | Out-File -FilePath "backend/templates/debug.html" -Encoding utf8

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