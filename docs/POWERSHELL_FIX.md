# Quick Fix for PowerShell Execution Policy Issue

## The Issue
Windows blocked the virtual environment activation due to execution policy restrictions.

## Quick Solutions:

### Option 1: Use Command Prompt Instead
```cmd
cd "c:\Work\Artbot\Artbot Control Hub\artbot-control-hub\backend"
python -m venv venv
venv\Scripts\activate.bat
pip install PyJWT==2.8.0
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Option 2: Enable PowerShell Scripts (Run as Administrator)
```powershell
# Run PowerShell as Administrator and execute:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then retry the original commands
```

### Option 3: Bypass for This Session Only
```powershell
# Run this first, then retry:
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process

cd "c:\Work\Artbot\Artbot Control Hub\artbot-control-hub\backend"
.\venv\Scripts\Activate.ps1
pip install PyJWT==2.8.0
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Option 4: Direct Python Without venv (Simplest)
```powershell
cd "c:\Work\Artbot\Artbot Control Hub\artbot-control-hub\backend"
pip install PyJWT==2.8.0 fastapi uvicorn[standard] websockets pydantic pydantic-settings python-jose[cryptography] python-multipart aiofiles aiohttp redis psutil
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## What Should Happen Next:
After installing PyJWT and starting the server, you should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using WatchFiles
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

Then the backend will be ready at http://localhost:8000
