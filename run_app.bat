@echo off
echo ===============================================
echo  BlockChain Research AI Agent - Startup
echo ===============================================
echo.

REM Change to project directory
cd /d "%~dp0"

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if activation was successful
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to activate virtual environment
    echo Please make sure the virtual environment exists in the venv folder
    pause
    exit /b 1
)

echo Virtual environment activated successfully!
echo.

REM Start the Streamlit application
echo Starting Streamlit application...
echo Open your browser to http://localhost:8501
echo.
echo Press Ctrl+C to stop the application
echo.

streamlit run app.py

REM Keep command prompt open if there's an error
if %ERRORLEVEL% neq 0 (
    echo.
    echo ERROR: Application failed to start
    pause
)