@echo off
echo Starting Tropical Vending Development Environment
echo ------------------------------------------------

REM Check if Python virtual environment exists, create if it doesn't
if not exist ".\venv" (
    echo Creating Python virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Failed to create virtual environment. Make sure Python is installed.
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call .\venv\Scripts\activate.bat
if errorlevel 1 (
    echo Failed to activate virtual environment.
    exit /b 1
)

REM Check if pip is available and upgrade it
echo Ensuring pip is up-to-date...
python -m pip install --upgrade pip

REM First try to install Pillow separately using wheels
echo Installing Pillow separately with wheels...
pip install --only-binary :all: pillow==9.5.0
if errorlevel 1 (
    echo Failed to install Pillow. Trying an alternative approach...
    pip install --upgrade setuptools wheel
    pip install pillow==8.4.0 --no-deps
    if errorlevel 1 (
        echo Warning: Pillow installation failed. Some image features may not work.
    )
)

REM Install Python dependencies
echo Installing Python dependencies...
pip install --prefer-binary -r requirements.txt
if errorlevel 1 (
    echo Failed to install dependencies. Please check requirements.txt for issues.
    exit /b 1
)

REM Verify Django is installed
python -c "import django; print('Django installed')" 2>nul
if errorlevel 1 (
    echo Django was not installed properly. Trying to install it directly...
    pip install django==4.2
    if errorlevel 1 (
        echo Failed to install Django. Please try installing it manually.
        exit /b 1
    )
)

REM Verify Pillow is installed
python -c "import PIL; print('Pillow installed')" 2>nul
if errorlevel 1 (
    echo Pillow was not installed properly. Trying to install it directly...
    pip uninstall -y pillow
    pip install --no-cache-dir pillow==8.4.0
)

REM Fix imports in the project
echo Fixing import paths in Python files...
python fix_imports.py

REM Create necessary directories
echo Creating static and media directories...
if not exist ".\backend\static" mkdir ".\backend\static" 
if not exist ".\backend\staticfiles" mkdir ".\backend\staticfiles"
if not exist ".\backend\media" mkdir ".\backend\media"
if not exist ".\backend\templates" mkdir ".\backend\templates"

REM Migrate database if needed
echo Running database migrations...
cd backend

REM Fix python path issue
set PYTHONPATH=%CD%\..

REM Update settings module
set DJANGO_SETTINGS_MODULE=vendingapp.settings

REM Fix the manage.py file if needed
python -c "content = open('manage.py').read(); open('manage.py', 'w').write(content.replace('backend.vendingapp.settings', 'vendingapp.settings'))" 2>nul

python manage.py migrate
if errorlevel 1 (
    echo Failed to run migrations.
    cd ..
    exit /b 1
)

REM Start Django in background
echo Starting Django backend server...
start cmd /k "set PYTHONPATH=%PYTHONPATH% && set DJANGO_SETTINGS_MODULE=%DJANGO_SETTINGS_MODULE% && python manage.py runserver"

REM Go back to root and start frontend
cd ..

REM Check if node_modules exists, install if it doesn't
if not exist ".\frontend\node_modules" (
    echo Installing npm dependencies...
    cd frontend
    npm install
    if errorlevel 1 (
        echo Failed to install npm dependencies.
        exit /b 1
    )
    cd ..
)

REM Start frontend development server
echo Starting Vue frontend server...
cd frontend
start cmd /k npm run dev
cd ..

echo.
echo All servers started!
echo - Backend running at: http://localhost:8000/
echo - Frontend running at: http://localhost:5173/
echo.
echo Close the command windows to stop the servers
echo.
pause 