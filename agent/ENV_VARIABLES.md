# Artbot Agent Environment Variables

This file documents the environment variables that can be used to configure the Artbot Agent.

## Required Variables

None - the agent will run with default values if no environment variables are set.

## Optional Variables

### Hub Configuration
- `HUB_URL` - URL of the control hub (default: "http://localhost:8000")
- `HUB_DOMAIN` - Domain of the control hub (default: "localhost")

### Agent Identification
- `AGENT_ID` - Unique identifier for this agent (default: hostname)

### Timing Configuration
- `HEARTBEAT_INTERVAL` - How often to send heartbeat to hub in seconds (default: 30)
- `MONITOR_INTERVAL` - How often to collect system metrics in seconds (default: 10)

### ROS2 Configuration
- `ROS2_WORKSPACE` - Path to ROS2 workspace (default: "/home/ubuntu/ros2_ws")
- `ROS2_PACKAGE` - Name of ROS2 package to monitor (default: "person_following_system")

### Robot Hardware Configuration
- `CREATE3_IP` - IP address of Create3 robot (default: "192.168.186.2")
- `WORKSPACE_DIR` - Path to workspace directory (default: "/home/artbot/workspace")
- `WORKSPACE_LOG_DIR` - Path to workspace log directory (default: "/home/artbot/workspace/logs")

### Logging
- `LOG_LEVEL` - Logging level (default: "INFO")

## Example .env file

Create a `.env` file in the agent directory with:

```
# Hub connection
HUB_URL=http://192.168.1.100:8000
HUB_DOMAIN=control-hub.local

# Agent identification
AGENT_ID=robot-001

# Timing
HEARTBEAT_INTERVAL=30
MONITOR_INTERVAL=10

# ROS2 paths
ROS2_WORKSPACE=/home/ubuntu/ros2_ws
ROS2_PACKAGE=person_following_system

# Robot hardware
CREATE3_IP=192.168.186.2
WORKSPACE_DIR=/home/artbot/workspace
WORKSPACE_LOG_DIR=/home/artbot/workspace/logs

# Logging
LOG_LEVEL=INFO
```

## Notes

- All path variables should use absolute paths
- IP addresses should be accessible from the agent's network
- The agent will attempt to auto-discover some settings if not provided
- Environment variables take precedence over default values
