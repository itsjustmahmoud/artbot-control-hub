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

# Start the full stack
.\start-local.ps1
```

### Agent Deployment (Raspberry Pi)
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
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── routers/   # API endpoints
│   │   ├── services/  # Business logic
│   │   └── auth/      # Authentication
│   └── requirements.txt
├── frontend/          # Vue 3 frontend
│   ├── src/
│   │   ├── views/     # Dashboard pages
│   │   ├── stores/    # State management
│   │   └── services/  # API clients
│   └── package.json
├── agent/             # Robot agent
│   ├── artbot_agent/
│   │   ├── main.py    # Agent entry point
│   │   └── services/  # Agent services
│   └── requirements.txt
└── docs/              # Documentation
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

- [Installation Guide](docs/INSTALLATION.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [API Documentation](docs/API.md)
- [Local Setup](docs/LOCAL_SETUP.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🏛️ Museum Robotics

Built for modern museum exhibition management and robot fleet coordination.
