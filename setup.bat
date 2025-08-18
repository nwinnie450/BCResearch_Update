@echo off
echo ===============================================
echo  BlockChain Research AI Agent - Setup
echo ===============================================
echo.

REM Change to project directory
cd /d "%~dp0"

echo Checking Python installation...
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://python.org
    pause
    exit /b 1
)

python --version
echo Python found successfully!
echo.

echo Creating virtual environment...
if exist venv (
    echo Virtual environment already exists. Removing old version...
    rmdir /s /q venv
)

python -m venv venv
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo Virtual environment created successfully!
echo.

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing dependencies...
pip install -r requirements.txt

if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ===============================================
echo  SETUP COMPLETE!
echo ===============================================
echo.
echo Next steps:
echo 1. (Optional) Configure API keys in .env file for enhanced accuracy
echo 2. Run 'run_app.bat' to start the application
echo 3. Open http://localhost:8501 in your browser
echo.
echo For API key setup, see API_KEYS_SETUP.md
echo.
pause