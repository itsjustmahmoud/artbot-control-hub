# 🤖 Artbot Control Hub

A modern, real-time, web-based control system for managing museum exhibition robots. Built with Vue 3, FastAPI, and agent-based architecture.

## ✨ Features

- 🎛️ **Real-time Dashboard**: Live monitoring of robot fleet status
- 👥 **Multi-level Access**: Admin and Museum Staff roles  
- 🔄 **Live Data Streaming**: WebSocket-based real-time updates
- 🤖 **Agent Architecture**: Distributed robot management
- 📱 **Responsive Design**: Modern glass-morphism UI
- 🔐 **Secure Authentication**: JWT-based access control
- 📊 **System Monitoring**: Performance metrics and health status

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │     Agent       │
│   (Vue 3)       │◄──►│   (FastAPI)     │◄──►│   (Python)      │
│                 │    │                 │    │                 │
│ • Admin Portal  │    │ • REST APIs     │    │ • Robot Control │
│ • Museum Portal │    │ • WebSockets    │    │ • Health Monitor│
│ • Real-time UI  │    │ • Auth System   │    │ • Data Collection│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Git

### Local Development
```bash
# Clone the repository
git clone https://github.com/yourusername/artbot-control-hub.git
cd artbot-control-hub

# Windows: Start the full stack
.\scripts\start-local.ps1

# Linux/Mac: Start the full stack
./start.sh
```

### Agent Deployment (Raspberry Pi)

#### 🚀 One-Liner Installation (Recommended)
```bash
# Replace YOUR_HUB_IP with your control hub computer's IP address
curl -sSL https://raw.githubusercontent.com/yourusername/artbot-control-hub/main/scripts/install-agent.sh | bash
```

#### ⚡ Quick Test Installation
```bash
# Replace 192.168.0.201 with your hub IP
curl -sSL https://raw.githubusercontent.com/yourusername/artbot-control-hub/main/scripts/quick-install.sh | bash -s 192.168.0.201
```

#### 🔍 Finding Your Hub IP Address

**On Windows:**
```powershell
ipconfig | findstr "IPv4"
```

**On Mac/Linux:**
```bash
hostname -I | awk '{print $1}'
```

#### 📋 Manual Installation
```bash
# On your robot/Pi
git clone https://github.com/yourusername/artbot-control-hub.git
cd artbot-control-hub/agent

# Configure environment
cp .env.example .env
# Edit .env with your hub URL

# Install and run
pip install -r requirements.txt
python -m artbot_agent.main
```

## 🔧 Configuration

### Backend (.env)
```env
SECRET_KEY=your-secret-key
ADMIN_PASSWORD=admin123
MUSEUM_PASSWORD=museum123
```

### Agent (.env)
```env
HUB_URL=http://your-hub-ip:8000
AGENT_ID=robot_01
HEARTBEAT_INTERVAL=30
```

## 📁 Project Structure

```
artbot-control-hub/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── routers/      # API endpoints
│   │   ├── services/     # Business logic
│   │   └── auth/         # Authentication
│   └── requirements.txt
├── frontend/             # Vue 3 frontend
│   ├── src/
│   │   ├── views/        # Dashboard pages
│   │   ├── stores/       # State management
│   │   └── services/     # API clients
│   └── package.json
├── agent/                # Robot agent
│   ├── artbot_agent/
│   │   ├── main.py       # Agent entry point
│   │   └── services/     # Agent services
│   └── requirements.txt
├── scripts/              # Installation & startup scripts
│   ├── install-agent.sh  # Pi agent installer
│   ├── quick-install.sh  # Quick Pi setup
│   └── start-local.ps1   # Windows development
├── docs/                 # Documentation
│   ├── API.md           # API reference
│   └── DEPLOYMENT.md    # Deployment guide
├── deployment/           # Docker configurations
└── start.sh             # Linux/Mac development
```

## 🎯 Access Levels

- **Administrator**: Full system control, analytics, bulk operations
- **Museum Staff**: Robot monitoring, basic operations

Default passwords:
- Admin: `admin123`
- Museum: `museum123`

## 🛠️ Development

### Backend Development
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate  # On Windows
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0
```

### Frontend Development  
```bash
cd frontend
npm install
npm run dev
```

### Agent Development
```bash
cd agent
pip install -r requirements.txt
python -m artbot_agent.main
```

## 📖 Documentation

- [API Documentation](docs/API.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Local Setup Guide](docs/LOCAL_SETUP.md)
- [Implementation Status](docs/IMPLEMENTATION_STATUS.md)
- [PowerShell Troubleshooting](docs/POWERSHELL_FIX.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🏛️ Museum Robotics

Built for modern museum exhibition management and robot fleet coordination.
