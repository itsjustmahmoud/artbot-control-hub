import os
import socket
import platform
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class AgentConfig:
    """Configuration for Artbot Agent"""
    
    def __init__(self):
        # Hub configuration
        self.hub_url = os.getenv("HUB_URL", "http://localhost:8000")
        self.hub_domain = os.getenv("HUB_DOMAIN", "localhost")
        
        # Agent identification
        self.agent_id = os.getenv("AGENT_ID", socket.gethostname())
        self.hostname = socket.gethostname()
        
        # Heartbeat configuration
        self.heartbeat_interval = int(os.getenv("HEARTBEAT_INTERVAL", "30"))  # seconds
        
        # ROS2 configuration
        self.ros2_workspace = os.getenv("ROS2_WORKSPACE", "/home/ubuntu/ros2_ws")
        self.ros2_package = os.getenv("ROS2_PACKAGE", "person_following_system")
        
        # System monitoring
        self.monitor_interval = int(os.getenv("MONITOR_INTERVAL", "10"))  # seconds
        
        # Logging
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
    
    def get_local_ip(self):
        """Get local IP address"""
        try:
            # Connect to a remote address to get local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"
    
    def get_system_info(self):
        """Get system information"""
        return {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "hostname": self.hostname,
            "agent_id": self.agent_id
        }
    
    def get_websocket_url(self):
        """Get WebSocket URL for agent connection"""
        ws_url = self.hub_url.replace("http://", "ws://").replace("https://", "wss://")
        return f"{ws_url}/ws/agent/{self.agent_id}"
    
    def get_registration_url(self):
        """Get registration URL"""
        return f"{self.hub_url}/api/agents/register"
    
    def get_heartbeat_url(self):
        """Get heartbeat URL"""
        return f"{self.hub_url}/api/agents/{self.agent_id}/heartbeat"
