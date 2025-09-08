@echo off
echo ============================================================
echo Boutique Work Orders - Running with Virtual Environment
echo ============================================================

echo Activating virtual environment...
call C:\Users\kvs\Desktop\venv_boutique\Scripts\activate.bat

echo.
echo Starting FastAPI server...
echo Server will be available at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.

cd /d "%~dp0"
python run_server.py

pause
