# PowerShell script to start development servers for Tropical Vending

# Set error action preference
$ErrorActionPreference = "Stop"

Write-Host "Starting Tropical Vending Development Environment" -ForegroundColor Green
Write-Host "------------------------------------------------" -ForegroundColor Green

# Activate virtual environment
if (Test-Path ".\venv") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    try {
        & .\venv\Scripts\Activate.ps1
    } catch {
        Write-Host "Failed to activate virtual environment: $_" -ForegroundColor Red
        exit 1
    }
}

# Make sure we're in the right directory
$rootDir = Get-Location

# Start Django server in a new PowerShell window
Write-Host "Starting Django backend server..." -ForegroundColor Green
$djangoCommand = "cd '$rootDir\backend'; ..\venv\Scripts\Activate.ps1; python manage.py runserver; Read-Host 'Press Enter to close'"
Start-Process powershell.exe -ArgumentList "-NoExit", "-Command", $djangoCommand

# Start frontend development server in a new PowerShell window
Write-Host "Starting Vue frontend server..." -ForegroundColor Green
$vueCommand = "cd '$rootDir\frontend'; npm run dev; Read-Host 'Press Enter to close'"
Start-Process powershell.exe -ArgumentList "-NoExit", "-Command", $vueCommand

Write-Host "`nAll servers started in separate windows!" -ForegroundColor Cyan
Write-Host "- Backend running at: http://localhost:8000/" -ForegroundColor Cyan
Write-Host "- Frontend running at: http://localhost:5173/" -ForegroundColor Cyan
Write-Host "`nClose the server windows when you're done." -ForegroundColor Yellow 