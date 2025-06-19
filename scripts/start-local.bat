@echo off
echo Starting Artbot Control Hub locally...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Check if Node.js is available
node --version >nul 2>&1
if errorlevel 1 (
    echo Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org
    pause
    exit /b 1
)

echo Setting up backend...
cd /d "%~dp0backend"

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install backend dependencies
echo Installing backend dependencies...
pip install -r requirements.txt

echo.
echo Starting backend server...
start "Artbot Backend" cmd /k "python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

echo Setting up frontend...
cd /d "%~dp0frontend"

REM Install frontend dependencies
echo Installing frontend dependencies...
call npm install

echo.
echo Starting frontend development server...
start "Artbot Frontend" cmd /k "npm run dev"

echo.
echo ============================================
echo Artbot Control Hub is starting up!
echo.
echo Backend API: http://localhost:8000
echo Frontend UI: http://localhost:5173
echo API Docs: http://localhost:8000/docs
echo.
echo Login credentials:
echo - Museum Staff: museum123
echo - Admin: admin456
echo.
echo The interface will open with demo robots.
echo ============================================
echo.

REM Wait for user input
echo Press any key to open the web interface...
pause >nul

REM Open the web interface
start http://localhost:5173

echo.
echo Both servers are running!
echo Close this window to stop the servers.
pause
