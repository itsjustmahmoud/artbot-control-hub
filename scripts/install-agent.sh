#!/bin/bash

# Artbot Control Hub - Agent Auto-Installer
# Usage: curl -sSL https://raw.githubusercontent.com/itsjustmahmoud/artbot-control-hub/main/scripts/install-agent.sh | bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="https://github.com/itsjustmahmoud/artbot-control-hub.git"
INSTALL_DIR="$HOME/artbot-control-hub"
AGENT_DIR="$INSTALL_DIR/agent"

echo -e "${BLUE}🤖 Artbot Control Hub - Agent Auto-Installer${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Function to print status
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if running on Raspberry Pi
if [[ $(uname -m) != "arm"* ]] && [[ $(uname -m) != "aarch64" ]]; then
    print_warning "This script is designed for Raspberry Pi, but continuing anyway..."
fi

# Get Hub IP from user
echo -e "${YELLOW}Please enter your Artbot Control Hub IP address:${NC}"
echo -e "${YELLOW}(This is the IP of the computer running the web interface)${NC}"
read -p "Hub IP: " HUB_IP

if [[ -z "$HUB_IP" ]]; then
    print_error "Hub IP is required!"
    exit 1
fi

# Validate IP format (basic check)
if [[ ! $HUB_IP =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
    print_error "Invalid IP format!"
    exit 1
fi

echo ""
print_status "Using Hub IP: $HUB_IP"
echo ""

# Update system
print_status "Updating system packages..."
sudo apt-get update -qq > /dev/null 2>&1

# Install dependencies
print_status "Installing system dependencies..."
sudo apt-get install -y git python3 python3-pip python3-venv curl > /dev/null 2>&1

# Remove existing installation if it exists
if [[ -d "$INSTALL_DIR" ]]; then
    print_warning "Removing existing installation..."
    rm -rf "$INSTALL_DIR"
fi

# Clone repository
print_status "Downloading Artbot Control Hub..."
git clone "$REPO_URL" "$INSTALL_DIR" > /dev/null 2>&1

# Navigate to agent directory
cd "$AGENT_DIR"

# Create virtual environment
print_status "Creating Python virtual environment..."
python3 -m venv venv > /dev/null 2>&1

# Activate virtual environment and install dependencies
print_status "Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1

# Create environment configuration
print_status "Configuring agent..."
cat > .env << EOF
# Artbot Control Hub Configuration
HUB_URL=http://$HUB_IP:8000
HUB_DOMAIN=$HUB_IP
AGENT_ID=$(hostname)_robot
HEARTBEAT_INTERVAL=30
LOG_LEVEL=INFO
ROS2_WORKSPACE=/home/$USER/ros2_ws
ROS2_PACKAGE=person_following_system
MONITOR_INTERVAL=10
EOF

# Create startup script
print_status "Creating startup script..."
cat > run-agent.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python3 -m artbot_agent.main
EOF

chmod +x run-agent.sh

# Create systemd service (optional)
print_status "Creating systemd service..."
sudo tee /etc/systemd/system/artbot-agent.service > /dev/null << EOF
[Unit]
Description=Artbot Control Hub Agent
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$AGENT_DIR
ExecStart=$AGENT_DIR/run-agent.sh
Restart=always
RestartSec=10
Environment=PATH=/usr/bin:/usr/local/bin
Environment=PYTHONPATH=$AGENT_DIR

[Install]
WantedBy=multi-user.target
EOF

# Enable but don't start service yet
sudo systemctl daemon-reload
sudo systemctl enable artbot-agent > /dev/null 2>&1

echo ""
echo -e "${GREEN}🎉 Installation Complete!${NC}"
echo -e "${BLUE}===========================================${NC}"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo -e "1. ${GREEN}Test the agent:${NC}"
echo -e "   cd $AGENT_DIR && ./run-agent.sh"
echo ""
echo -e "2. ${GREEN}Start as system service:${NC}"
echo -e "   sudo systemctl start artbot-agent"
echo ""
echo -e "3. ${GREEN}Check service status:${NC}"
echo -e "   sudo systemctl status artbot-agent"
echo ""
echo -e "4. ${GREEN}View logs:${NC}"
echo -e "   sudo journalctl -u artbot-agent -f"
echo ""
echo -e "${YELLOW}Configuration saved to:${NC} $AGENT_DIR/.env"
echo -e "${YELLOW}Agent directory:${NC} $AGENT_DIR"
echo ""

# Ask if user wants to start the agent now
echo -e "${YELLOW}Start the agent now? (y/n):${NC}"
read -p "> " start_now

if [[ $start_now =~ ^[Yy]$ ]]; then
    echo ""
    print_status "Starting Artbot Agent..."
    echo -e "${BLUE}Press Ctrl+C to stop the agent${NC}"
    echo ""
    cd "$AGENT_DIR"
    ./run-agent.sh
fi
