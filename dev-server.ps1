# PowerShell script to start development servers for Tropical Vending

# Set error action preference
$ErrorActionPreference = "Stop"

# Add error handling function
function Write-ErrorLog {
    param (
        [string]$Message,
        [System.Management.Automation.ErrorRecord]$ErrorRecord = $null
    )
    
    Write-Host "ERROR: $Message" -ForegroundColor Red
    
    if ($ErrorRecord) {
        Write-Host "Exception Type: $($ErrorRecord.Exception.GetType().FullName)" -ForegroundColor Red
        Write-Host "Exception Message: $($ErrorRecord.Exception.Message)" -ForegroundColor Red
        Write-Host "Stack Trace: $($ErrorRecord.ScriptStackTrace)" -ForegroundColor Red
    }
}

Write-Host "Starting Tropical Vending Development Environment" -ForegroundColor Green
Write-Host "------------------------------------------------" -ForegroundColor Green

# Check if Python virtual environment exists, create if it doesn't
if (-Not (Test-Path ".\venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    if (-Not $?) {
        Write-ErrorLog "Failed to create virtual environment. Make sure Python is installed."
        exit 1
    }
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
try {
    & .\venv\Scripts\Activate.ps1
} catch {
    Write-ErrorLog "Failed to activate virtual environment: $_" $_
    exit 1
}

# Check if pip is available and upgrade it
Write-Host "Ensuring pip is up-to-date..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install Python dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install --prefer-binary -r requirements.txt
if (-Not $?) {
    Write-ErrorLog "Failed to install dependencies. Please check requirements.txt for issues."
    exit 1
}

# Verify Django is installed
$djangoInstalled = python -c "import django; print('Django installed')" 2>$null
if (-Not $djangoInstalled) {
    Write-Host "Django was not installed properly. Trying to install it directly..." -ForegroundColor Yellow
    pip install django==4.2
    if (-Not $?) {
        Write-ErrorLog "Failed to install Django. Please try installing it manually."
        exit 1
    }
}

# Fix imports in the project
Write-Host "Fixing import paths in Python files..." -ForegroundColor Yellow
try {
    python fix_imports.py
} catch {
    Write-ErrorLog "Error running fix_imports.py" $_
    # Continue anyway
    Write-Host "Continuing despite error in fix_imports.py" -ForegroundColor Yellow
}

# Create necessary directories
Write-Host "Creating static and media directories..." -ForegroundColor Yellow
if (-Not (Test-Path ".\backend\static")) {
    New-Item -Path ".\backend\static" -ItemType Directory -Force | Out-Null
}
if (-Not (Test-Path ".\backend\staticfiles")) {
    New-Item -Path ".\backend\staticfiles" -ItemType Directory -Force | Out-Null
}
if (-Not (Test-Path ".\backend\media")) {
    New-Item -Path ".\backend\media" -ItemType Directory -Force | Out-Null
}
if (-Not (Test-Path ".\backend\templates")) {
    New-Item -Path ".\backend\templates" -ItemType Directory -Force | Out-Null
}

# Migrate database if needed
Write-Host "Running database migrations..." -ForegroundColor Yellow
cd backend

# Fix python path issue
$env:PYTHONPATH = (Resolve-Path "..").Path

# Update settings module
$settingsModule = "vendingapp.settings"
$env:DJANGO_SETTINGS_MODULE = $settingsModule

# Fix the manage.py file if needed
$managePyPath = "manage.py"
$managePyContent = Get-Content $managePyPath -Raw
if ($managePyContent -match "backend\.vendingapp\.settings") {
    Write-Host "Updating Django settings path in manage.py..." -ForegroundColor Yellow
    $managePyContent = $managePyContent -replace "backend\.vendingapp\.settings", $settingsModule
    Set-Content -Path $managePyPath -Value $managePyContent
}

try {
    $migrateResult = python manage.py migrate
    if (-Not $?) {
        Write-ErrorLog "Failed to run migrations: $migrateResult"
        cd ..
        exit 1
    }
} catch {
    Write-ErrorLog "Error running migrations" $_
    cd ..
    exit 1
}

# Start Django in background job
Write-Host "Starting Django backend server..." -ForegroundColor Green
$djangoPath = Resolve-Path "..\venv\Scripts\python.exe"
$djangoJob = Start-Job -ScriptBlock {
    try {
        cd $using:PWD
        $env:PYTHONPATH = $using:env:PYTHONPATH
        $env:DJANGO_SETTINGS_MODULE = $using:settingsModule
        & "$using:djangoPath" manage.py runserver
        if (-Not $?) {
            Write-Output "ERROR: Django server failed to start"
        }
    } catch {
        Write-Output "ERROR in Django job: $_"
    }
}

# Go back to root and start frontend
cd ..

# Check if node_modules exists, install if it doesn't
if (-Not (Test-Path ".\frontend\node_modules")) {
    Write-Host "Installing npm dependencies..." -ForegroundColor Yellow
    cd frontend
    npm install
    if (-Not $?) {
        Write-ErrorLog "Failed to install npm dependencies."
        exit 1
    }
    cd ..
}

# Start frontend development server
Write-Host "Starting Vue frontend server..." -ForegroundColor Green
cd frontend
$viteJob = Start-Job -ScriptBlock {
    try {
        cd $using:PWD
        npm run dev
        if (-Not $?) {
            Write-Output "ERROR: Vue server failed to start"
        }
    } catch {
        Write-Output "ERROR in Vue job: $_"
    }
}
cd ..

Write-Host "`nAll servers started!" -ForegroundColor Cyan
Write-Host "- Backend running at: http://localhost:8000/" -ForegroundColor Cyan
Write-Host "- Frontend running at: http://localhost:5173/" -ForegroundColor Cyan
Write-Host "`nPress Ctrl+C to stop all servers" -ForegroundColor Yellow

# Display job output in real-time
try {
    # Wait a moment for jobs to initialize
    Start-Sleep -Seconds 2
    
    # Check if jobs are still running
    $djangoState = Get-Job -Id $djangoJob.Id | Select-Object -ExpandProperty State
    $viteState = Get-Job -Id $viteJob.Id | Select-Object -ExpandProperty State
    
    Write-Host "Django job state: $djangoState" -ForegroundColor Yellow
    Write-Host "Vue job state: $viteState" -ForegroundColor Yellow
    
    # Get any immediate output
    Write-Host "Django server output:" -ForegroundColor Yellow
    Receive-Job $djangoJob
    
    Write-Host "Vue server output:" -ForegroundColor Yellow
    Receive-Job $viteJob
    
    # Main loop to keep script running and show output
    while ($true) {
        # Check job status
        $djangoState = Get-Job -Id $djangoJob.Id | Select-Object -ExpandProperty State
        $viteState = Get-Job -Id $viteJob.Id | Select-Object -ExpandProperty State
        
        if ($djangoState -eq "Completed" -or $djangoState -eq "Failed") {
            Write-Host "Django server job ended with state: $djangoState" -ForegroundColor Red
            Write-Host "Django job output:" -ForegroundColor Yellow
            Receive-Job $djangoJob
        }
        
        if ($viteState -eq "Completed" -or $viteState -eq "Failed") {
            Write-Host "Vue server job ended with state: $viteState" -ForegroundColor Red
            Write-Host "Vue job output:" -ForegroundColor Yellow
            Receive-Job $viteJob
        }
        
        # If both jobs have ended, break the loop
        if (($djangoState -eq "Completed" -or $djangoState -eq "Failed") -and
            ($viteState -eq "Completed" -or $viteState -eq "Failed")) {
            Write-Host "Both server jobs have ended. Exiting." -ForegroundColor Red
            break
        }
        
        # Get any new output
        Receive-Job $djangoJob
        Receive-Job $viteJob
        
        Start-Sleep -Seconds 1
    }
}
catch {
    Write-ErrorLog "Error in main loop" $_
}
finally {
    # Clean up jobs on exit
    Write-Host "`nStopping servers..." -ForegroundColor Yellow
    Stop-Job $djangoJob -ErrorAction SilentlyContinue
    Remove-Job $djangoJob -Force -ErrorAction SilentlyContinue
    Stop-Job $viteJob -ErrorAction SilentlyContinue
    Remove-Job $viteJob -Force -ErrorAction SilentlyContinue
    
    # Deactivate virtual environment (if we're in one)
    if ($env:VIRTUAL_ENV) {
        deactivate
    }
    
    Write-Host "Development servers stopped" -ForegroundColor Green
} 