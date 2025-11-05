@echo off
echo ========================================
echo   Attendance System Server Manager
echo ========================================
echo.

cd /d "%~dp0"

echo Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo.
echo Checking required packages...
python -c "import flask, flask_cors, supabase, mtcnn, deepface, psutil" 2>nul
if %errorlevel% neq 0 (
    echo Installing required packages...
    pip install flask flask-cors supabase mtcnn deepface psutil python-dotenv pillow scipy numpy
)

echo.
echo Starting server with monitoring...
echo Press Ctrl+C to stop the server
echo.

python start_server.py

pause