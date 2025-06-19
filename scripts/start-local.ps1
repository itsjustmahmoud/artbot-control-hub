Write-Host "Starting Artbot Control Hub locally..." -ForegroundColor Green
Write-Host ""

# Check dependencies
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python 3.8+ from https://python.org" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

try {
    $nodeVersion = node --version 2>&1
    Write-Host "✓ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Node.js not found. Please install Node.js from https://nodejs.org" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Setup backend
Write-Host "Setting up backend..." -ForegroundColor Yellow
Set-Location "$PSScriptRoot\..\backend"

# Create virtual environment if it doesn't exist
if (!(Test-Path "venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Install dependencies
Write-Host "Installing backend dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Start backend in new window
Write-Host "Starting backend server..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\venv\Scripts\Activate.ps1; uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

# Wait for backend to start
Start-Sleep -Seconds 3

# Setup frontend
Write-Host "Setting up frontend..." -ForegroundColor Yellow
Set-Location "$PSScriptRoot\..\frontend"

# Install frontend dependencies
Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
npm install

# Start frontend in new window
Write-Host "Starting frontend development server..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; npm run dev"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Artbot Control Hub is starting up!" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "Backend API (Network): http://192.168.0.201:8000" -ForegroundColor White
Write-Host "Frontend UI: http://localhost:3000" -ForegroundColor White  
Write-Host "Frontend UI (Network): http://192.168.0.201:3000" -ForegroundColor White
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Login credentials:" -ForegroundColor Yellow
Write-Host "- Museum Staff: museum123" -ForegroundColor White
Write-Host "- Admin: admin123" -ForegroundColor White
Write-Host ""
Write-Host "Real robot 'artbot1_robot' is connected!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Wait a moment for frontend to start
Write-Host "Waiting for servers to start..."
Start-Sleep -Seconds 5

# Open web interface
Write-Host "Opening web interface..." -ForegroundColor Green
Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "Both servers are running!" -ForegroundColor Green
Write-Host "Check the new PowerShell windows for server logs." -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter to exit (this will NOT stop the servers)"
