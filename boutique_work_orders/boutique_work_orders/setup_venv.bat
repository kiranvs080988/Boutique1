@echo off
echo ============================================================
echo Boutique Work Orders - Virtual Environment Setup
echo ============================================================

echo Creating virtual environment at C:\Users\kvs\Desktop\venv_boutique...
python -m venv C:\Users\kvs\Desktop\venv_boutique

echo.
echo Activating virtual environment...
call C:\Users\kvs\Desktop\venv_boutique\Scripts\activate.bat

echo.
echo Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Installing required packages...
pip install fastapi>=0.100.0
pip install uvicorn[standard]>=0.20.0
pip install sqlalchemy>=2.0.0
pip install pydantic>=2.0.0
pip install python-multipart>=0.0.5
pip install email-validator>=2.0.0
pip install python-dateutil>=2.8.0
pip install requests>=2.25.0

echo.
echo ============================================================
echo Virtual Environment Setup Complete!
echo ============================================================
echo.
echo Virtual environment location: C:\Users\kvs\Desktop\venv_boutique
echo.
echo To activate the virtual environment:
echo   C:\Users\kvs\Desktop\venv_boutique\Scripts\activate
echo.
echo To run the server with virtual environment:
echo   C:\Users\kvs\Desktop\venv_boutique\Scripts\activate
echo   cd boutique_work_orders
echo   python run_server.py
echo.
echo ============================================================

pause
