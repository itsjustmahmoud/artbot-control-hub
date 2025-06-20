from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class RobotRegistryService:
    """Manages robot registration and basic CRUD operations"""
    
    def __init__(self):
        self.robots: Dict[str, dict] = {}
    
    def register_robot(self, robot_id: str, robot_info: dict):
        """Register a new robot"""
        robot_data = {
            "id": robot_id,
            "agent_id": robot_id,  # Explicitly expose agent_id as robot_id
            "name": robot_info.get("name", f"Robot {robot_id}"),
            "hostname": robot_info.get("hostname", f"unknown-{robot_id}"),  # Pi hostname
            "status": "online",
            "current_action": "idle",
            "battery_level": robot_info.get("battery_level", 100),
            "cpu_usage": robot_info.get("cpu_usage", 0),
            "memory_usage": robot_info.get("memory_usage", 0),
            "temperature": robot_info.get("temperature", 25),
            "ip_address": robot_info.get("ip_address", "unknown"),
            "location": robot_info.get("location", "Unknown"),
            "capabilities": robot_info.get("capabilities", []),            # Connectivity status
            "create3_connected": robot_info.get("create3_connected", False),
            "create3_status": robot_info.get("create3_status", "unknown"),
            "oak_connected": robot_info.get("oak_connected", False),
            # Workspace status
            "workspace_running": robot_info.get("workspace_running", False),
            # System metrics
            "uptime": robot_info.get("uptime", 0),
            "last_update": datetime.utcnow().isoformat(),
            "registered_at": datetime.utcnow().isoformat()
        }
        
        self.robots[robot_id] = robot_data
        logger.info(f"Robot {robot_id} registered: {robot_data['name']}")
        return robot_data
    
    def update_robot_status(self, robot_id: str, status_data: dict):
        """Update robot status and metrics"""
        if robot_id not in self.robots:
            logger.warning(f"Attempted to update unknown robot {robot_id}")
            return False
            
        robot = self.robots[robot_id]
        robot.update(status_data)
        robot["last_update"] = datetime.utcnow().isoformat()
        
        logger.debug(f"Robot {robot_id} status updated")
        return True
        
    def set_robot_status(self, robot_id: str, status: str, action: str = None):
        """Set robot status and current action"""
        if robot_id not in self.robots:
            return False
            
        self.robots[robot_id]["status"] = status
        if action:
            self.robots[robot_id]["current_action"] = action
        self.robots[robot_id]["last_update"] = datetime.utcnow().isoformat()
        
        logger.info(f"Robot {robot_id} status set to {status} with action {action}")
        return True
        
    def get_robot(self, robot_id: str) -> Optional[dict]:
        """Get specific robot information"""
        return self.robots.get(robot_id)
        
    def get_all_robots(self) -> Dict[str, dict]:
        """Get all registered robots"""
        return self.robots.copy()
        
    def get_online_robots(self) -> List[dict]:
        """Get robots that are currently online"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=5)
        online_robots = []
        
        for robot in self.robots.values():
            last_update = datetime.fromisoformat(robot["last_update"])
            if last_update > cutoff_time and robot["status"] != "offline":
                online_robots.append(robot)
                
        return online_robots
        
    def get_active_robots(self) -> List[dict]:
        """Get robots that are currently active"""
        return [robot for robot in self.robots.values() 
                if robot["status"] == "active"]
        
    def remove_robot(self, robot_id: str) -> bool:
        """Remove a robot from registry"""
        if robot_id in self.robots:
            del self.robots[robot_id]
            logger.info(f"Robot {robot_id} removed from registry")
            return True
        return False
        
    def get_robot_count_by_status(self) -> Dict[str, int]:
        """Get count of robots by status"""
        status_counts = {}
        for robot in self.robots.values():
            status = robot["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        return status_counts
