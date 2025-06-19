#!/bin/bash

# Artbot Control Hub - Main Startup Script
# This script starts both backend and frontend for development

echo "🤖 Starting Artbot Control Hub..."
echo "================================="

# Check if we're on Windows (for WSL/Git Bash)
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    echo "⚠️  Windows detected. Please use scripts/start-local.ps1 instead"
    echo "   PowerShell: .\\scripts\\start-local.ps1"
    exit 1
fi

# Check dependencies
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 16+"
    exit 1
fi

echo "✅ Dependencies check passed"

# Start backend in background
echo "🚀 Starting backend..."
cd backend
if [[ ! -d "venv" ]]; then
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Start frontend in background
echo "🎨 Starting frontend..."
cd frontend
if [[ ! -d "node_modules" ]]; then
    npm install
fi
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "🎉 Artbot Control Hub is starting!"
echo "================================="
echo "📍 Backend:  http://localhost:8000"
echo "📍 Frontend: http://localhost:5173"
echo "🔐 Admin:    password 'admin123'"
echo "🏛️  Museum:   password 'museum123'"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for Ctrl+C
trap 'echo ""; echo "🛑 Stopping services..."; kill $BACKEND_PID $FRONTEND_PID; exit' INT
wait
