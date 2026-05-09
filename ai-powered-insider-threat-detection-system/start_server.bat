@echo off
echo ==========================================
echo  SentinelAI - Insider Threat Detection
echo ==========================================
echo.

:: Check if we're in the right directory
if not exist "backend\app.py" (
    echo Error: backend\app.py not found!
    echo Please run this script from the project root directory.
    pause
    exit /b 1
)

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo Python detected:
python --version
echo.

:: Install dependencies if needed
echo Checking dependencies...
python -c "import flask, flask_jwt_extended, pandas, sklearn" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Error installing dependencies!
        pause
        exit /b 1
    )
)

echo Dependencies OK
echo.

:: Change to backend directory and start server
cd backend
echo Starting Flask server...
echo.
echo ==========================================
echo  Server will be available at:
echo  http://localhost:5000
echo.
echo  Demo Accounts:
echo    admin / admin123
echo    analyst / analyst123
echo    soc / soc123
echo ==========================================
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py

:: If we get here, the server stopped
cd ..
echo.
echo Server stopped.
pause
