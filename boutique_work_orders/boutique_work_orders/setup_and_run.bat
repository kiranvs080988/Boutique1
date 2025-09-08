@echo off
echo ============================================================
echo Boutique Work Orders Management System - Windows Setup
echo ============================================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://python.org
    pause
    exit /b 1
)

echo Python detected successfully

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Setup completed successfully!
echo ============================================================
echo.
echo Starting the Boutique Work Orders Management System...
echo.
echo API will be available at:
echo   - Documentation: http://localhost:8000/docs
echo   - ReDoc: http://localhost:8000/redoc
echo   - API Base: http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

REM Start the server
python run_server.py

pause
