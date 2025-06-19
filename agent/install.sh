#!/bin/bash

# Artbot Agent Installation Script
# This script installs the Artbot agent on a Raspberry Pi

set -e  # Exit on any error

echo "🤖 Artbot Agent Installation Script"
echo "=================================="

# Configuration
HUB_URL="${HUB_URL:-http://localhost:8000}"
AGENT_ID="${AGENT_ID:-$(hostname)}"
INSTALL_DIR="/opt/artbot-agent"
SERVICE_NAME="artbot-agent"

echo "Hub URL: $HUB_URL"
echo "Agent ID: $AGENT_ID"
echo "Install Directory: $INSTALL_DIR"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run as root (use sudo)"
    exit 1
fi

# Detect system
echo "🔍 Detecting system..."
OS=$(uname -s)
ARCH=$(uname -m)
echo "OS: $OS, Architecture: $ARCH"

# Check if this is a Raspberry Pi
if grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "✅ Raspberry Pi detected"
else
    echo "⚠️  Warning: Not running on Raspberry Pi"
fi

# Update system packages
echo "📦 Updating system packages..."
apt-get update

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
apt-get install -y python3 python3-pip python3-venv

# Create installation directory
echo "📁 Creating installation directory..."
mkdir -p $INSTALL_DIR
cd $INSTALL_DIR

# Download agent code (in production, this would download from GitHub releases)
echo "⬇️  Downloading agent software..."

# For now, we'll create the agent structure
# In production: curl -L -o artbot-agent.tar.gz https://github.com/your-repo/releases/latest/artbot-agent.tar.gz
# tar -xzf artbot-agent.tar.gz

# Create Python virtual environment
echo "🏗️  Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install --upgrade pip
pip install aiohttp websockets psutil

# Create agent configuration
echo "⚙️  Creating agent configuration..."
cat > config.env << EOF
# Artbot Agent Configuration
HUB_URL=$HUB_URL
AGENT_ID=$AGENT_ID
HEARTBEAT_INTERVAL=30
MONITOR_INTERVAL=10
LOG_LEVEL=INFO

# ROS2 Configuration (adjust as needed)
ROS2_WORKSPACE=/home/ubuntu/ros2_ws
ROS2_PACKAGE=person_following_system
EOF

# Create systemd service file
echo "🔧 Creating systemd service..."
cat > /etc/systemd/system/$SERVICE_NAME.service << EOF
[Unit]
Description=Artbot Agent
After=network.target
Wants=network.target

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=$INSTALL_DIR
Environment=PATH=$INSTALL_DIR/venv/bin
EnvironmentFile=$INSTALL_DIR/config.env
ExecStart=$INSTALL_DIR/venv/bin/python -m artbot_agent.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Set permissions
echo "🔐 Setting permissions..."
chown -R ubuntu:ubuntu $INSTALL_DIR
chmod +x $INSTALL_DIR/venv/bin/python

# Enable and start service
echo "🚀 Enabling and starting service..."
systemctl daemon-reload
systemctl enable $SERVICE_NAME

# Test connection to hub
echo "🔌 Testing connection to hub..."
if curl -f -s "$HUB_URL/api/system/health" > /dev/null; then
    echo "✅ Hub connection successful"
else
    echo "⚠️  Warning: Cannot connect to hub at $HUB_URL"
    echo "   Make sure the hub is running and accessible"
fi

# Start the service
echo "▶️  Starting agent service..."
systemctl start $SERVICE_NAME

# Check service status
sleep 2
if systemctl is-active --quiet $SERVICE_NAME; then
    echo "✅ Agent service started successfully"
else
    echo "❌ Agent service failed to start"
    echo "Check logs with: journalctl -u $SERVICE_NAME -f"
    exit 1
fi

echo ""
echo "🎉 Installation Complete!"
echo "========================"
echo ""
echo "The Artbot agent has been installed and started as a system service."
echo ""
echo "Useful commands:"
echo "  • Check status:  systemctl status $SERVICE_NAME"
echo "  • View logs:     journalctl -u $SERVICE_NAME -f"
echo "  • Restart:       systemctl restart $SERVICE_NAME"
echo "  • Stop:          systemctl stop $SERVICE_NAME"
echo ""
echo "Configuration file: $INSTALL_DIR/config.env"
echo "Agent ID: $AGENT_ID"
echo "Hub URL: $HUB_URL"
echo ""
echo "The agent should now be visible in your Artbot Control Hub dashboard."
