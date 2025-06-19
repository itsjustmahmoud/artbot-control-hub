#!/bin/bash

# Quick Artbot Agent Setup (No systemd service)
# Usage: curl -sSL https://raw.githubusercontent.com/itsjustmahmoud/artbot-control-hub/main/scripts/quick-install.sh | bash -s YOUR_HUB_IP

set -e

HUB_IP="$1"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Artbot Agent Quick Setup${NC}"

if [[ -z "$HUB_IP" ]]; then
    echo -e "${YELLOW}Usage: curl -sSL https://raw.githubusercontent.com/itsjustmahmoud/artbot-control-hub/main/scripts/quick-install.sh | bash -s YOUR_HUB_IP${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Using Hub IP: $HUB_IP"

# Update and install
sudo apt-get update -qq && sudo apt-get install -y git python3 python3-pip > /dev/null 2>&1

# Remove existing
rm -rf ~/artbot-control-hub

# Clone and setup
git clone https://github.com/itsjustmahmoud/artbot-control-hub.git ~/artbot-control-hub > /dev/null 2>&1
cd ~/artbot-control-hub/agent

# Install deps
pip3 install -r requirements.txt > /dev/null 2>&1

# Configure
cat > .env << EOF
HUB_URL=http://$HUB_IP:8000
HUB_DOMAIN=$HUB_IP
AGENT_ID=$(hostname)_robot
HEARTBEAT_INTERVAL=30
LOG_LEVEL=INFO
EOF

echo -e "${GREEN}✓${NC} Setup complete!"
echo -e "${YELLOW}Starting agent...${NC}"

# Run agent
python3 -m artbot_agent.main
