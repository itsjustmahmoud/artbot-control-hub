# Local Development Setup Guide

## Quick Start (Test the UI Locally)

### Option 1: Using Python Virtual Environment

#### 1. Set up Backend
```powershell
# Navigate to backend directory
cd "c:\Work\Artbot\Artbot Control Hub\artbot-control-hub\backend"

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Start the backend server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 2. Set up Frontend (in a new terminal)
```powershell
# Navigate to frontend directory
cd "c:\Work\Artbot\Artbot Control Hub\artbot-control-hub\frontend"

# Install dependencies
npm install

# Start the development server
npm run dev
```

#### 3. Access the Interface
- Open your browser to http://localhost:5173
- Use these credentials to test:
  - **Museum Staff**: Password: `museum123`
  - **Admin**: Password: `admin456`

### Option 2: Using Docker (Recommended for full experience)

```powershell
# Navigate to project root
cd "c:\Work\Artbot\Artbot Control Hub\artbot-control-hub"

# Build and start all services
docker-compose -f deployment/docker/docker-compose.yml up --build
```

Then access: http://localhost:3000

## What You'll See

### Without Real Robots Connected:
- **Login screen** with password authentication
- **Museum dashboard** with exhibition controls (START/STOP buttons)
- **Robot status area** showing "No robots connected"
- **System status** showing 0 robots online
- **WebSocket connection indicators**

### Demo Data (Optional)
To see the interface with sample robot data, I can add a demo mode that creates mock robots.

## Testing the Interface

### Museum Staff Dashboard Features:
1. **Exhibition Control**
   - Large green "START EXHIBITION" button
   - Large red "STOP EXHIBITION" button
   - Status indicators showing current state

2. **System Overview**
   - Total robots count
   - Online robots count
   - Active robots count
   - Exhibition running status

3. **Real-time Updates**
   - WebSocket connection status
   - Automatic refresh of robot states
   - Live system health monitoring

### Admin Dashboard Features:
1. **Individual Robot Control**
   - Start/stop specific robots
   - View detailed robot information
   - Monitor robot health metrics

2. **System Management**
   - View system logs
   - Monitor agent connections
   - System health metrics

3. **Advanced Monitoring**
   - Log filtering and search
   - Connection statistics
   - Agent management

## Development Features

### Hot Reload
- Frontend: Changes to Vue files automatically reload the page
- Backend: Changes to Python files automatically restart the server

### API Testing
You can test the API directly:
- API docs: http://localhost:8000/docs
- Raw API: http://localhost:8000/api/robots

### WebSocket Testing
- WebSocket endpoints are available at ws://localhost:8000/ws/dashboard
- Real-time updates work even without robots connected

## Next Steps

Once you see the interface working:
1. **Test authentication** with both user types
2. **Try the exhibition controls** (they'll work but show no robots)
3. **Check the admin interface** for advanced features
4. **Test WebSocket connections** (status indicators should show connected)

When ready to connect real robots:
1. Install the agent software on Raspberry Pi robots
2. Configure network settings for robot discovery
3. Watch as robots automatically appear in the interface!
