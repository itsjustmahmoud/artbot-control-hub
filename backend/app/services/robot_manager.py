from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
import json
import uuid
import asyncio

logger = logging.getLogger(__name__)

class RobotManager:
    """Manages robot state and operations in memory"""
    
    def __init__(self):
        # In-memory robot registry
        self.robots: Dict[str, dict] = {}
        # Connected agent instances
        self.agents: Dict[str, dict] = {}
        # Command history
        self.command_history: Dict[str, List[dict]] = {}
        # Robot logs storage (in-memory for now)
        self.robot_logs: Dict[str, List[dict]] = {}
        # WebSocket manager reference (set by main.py)
        self.websocket_manager = None
        
        # Initialize demo data for testing
        self._initialize_demo_data()
    
    def _initialize_demo_data(self):
        """Initialize with demo robots for testing"""
        demo_robots = [
            {
                "id": "artbot-01",
                "name": "Gallery Guide Alpha",
                "status": "online",
                "current_action": "idle",
                "battery_level": 85,
                "cpu_usage": 25,
                "memory_usage": 45,
                "temperature": 42,
                "ip_address": "192.168.1.101",
                "last_update": datetime.utcnow().isoformat()
            },
            {
                "id": "artbot-02", 
                "name": "Exhibition Beta",
                "status": "active",
                "current_action": "person_following",
                "battery_level": 72,
                "cpu_usage": 45,
                "memory_usage": 62,
                "temperature": 38,
                "ip_address": "192.168.1.102",
                "last_update": datetime.utcnow().isoformat()
            },
            {
                "id": "artbot-03",
                "name": "Museum Helper Gamma", 
                "status": "offline",
                "current_action": "maintenance",
                "battery_level": 12,
                "cpu_usage": 0,
                "memory_usage": 0,
                "temperature": 25,
                "ip_address": "192.168.1.103",
                "last_update": (datetime.utcnow() - timedelta(minutes=15)).isoformat()
            }
        ]
        
        for robot_data in demo_robots:
            self.robots[robot_data["id"]] = robot_data
            
            # Create corresponding agent entries
            self.agents[robot_data["id"]] = {
                "agent_id": robot_data["id"],
                "hostname": f"pi-{robot_data['id']}",
                "ip_address": robot_data["ip_address"],
                "status": "online" if robot_data["status"] != "offline" else "offline",
                "last_seen": datetime.fromisoformat(robot_data["last_update"]),
                "registered_at": datetime.utcnow() - timedelta(hours=2),
                "system_info": {
                    "os": "Raspberry Pi OS",
                    "python_version": "3.9.2",
                    "ros_version": "ROS2 Humble"
                }
            }
            
            # Add some demo logs
            self.robot_logs[robot_data["id"]] = [
                {
                    "timestamp": (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
                    "level": "INFO",
                    "message": "Person detection initialized",
                    "source": "oakd_perception"
                },
                {
                    "timestamp": (datetime.utcnow() - timedelta(minutes=3)).isoformat(),
                    "level": "INFO", 
                    "message": "Navigation system ready",
                    "source": "navigation"
                },
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "level": "INFO",
                    "message": f"Robot {robot_data['id']} status: {robot_data['status']}",
                    "source": "system"
                }
            ]
        
        logger.info(f"Demo data initialized with {len(demo_robots)} robots")

    async def send_command_to_robot(self, robot_id: str, action: str, parameters: dict = None) -> dict:
        """Send command to robot via WebSocket"""
        if not self.websocket_manager:
            raise Exception("WebSocket manager not initialized")
            
        command_id = str(uuid.uuid4())
        command_data = {
            "command_id": command_id,
            "type": "robot_command",
            "action": action,
            "parameters": parameters or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Store command in history
        if robot_id not in self.command_history:
            self.command_history[robot_id] = []
        
        self.command_history[robot_id].append({
            **command_data,
            "status": "sent"
        })
        
        # Send via WebSocket
        success = await self.websocket_manager.send_to_agent(robot_id, command_data)
        
        if not success:
            # Update command status
            self.command_history[robot_id][-1]["status"] = "failed"
            raise Exception(f"Failed to send command to robot {robot_id}")
        
        # Update robot status based on command
        if action == "start":
            self.set_robot_status(robot_id, "active", "person_following")
        elif action == "stop":
            self.set_robot_status(robot_id, "idle", "stopped")
        elif action == "restart":
            self.set_robot_status(robot_id, "restarting", "system_restart")
        elif action == "reboot":
            self.set_robot_status(robot_id, "rebooting", "system_reboot")
        
        return {"command_id": command_id}
    
    def get_robot_logs(self, robot_id: str, limit: int = 100) -> List[dict]:
        """Get logs for a specific robot"""
        if robot_id not in self.robot_logs:
            return []
        
        logs = self.robot_logs[robot_id]
        return logs[-limit:] if len(logs) > limit else logs
    
    def add_robot_log(self, robot_id: str, log_entry: dict):
        """Add a log entry for a robot"""
        if robot_id not in self.robot_logs:
            self.robot_logs[robot_id] = []
        
        log_entry["timestamp"] = datetime.utcnow().isoformat()
        self.robot_logs[robot_id].append(log_entry)
        
        # Keep only last 1000 logs per robot to prevent memory issues
        if len(self.robot_logs[robot_id]) > 1000:
            self.robot_logs[robot_id] = self.robot_logs[robot_id][-1000:]
    
    def get_robot_health(self, robot_id: str) -> dict:
        """Get robot health information"""
        robot = self.get_robot(robot_id)
        if not robot:
            return {"status": "unknown", "message": "Robot not found"}
        
        agent = self.get_agent(robot_id)
        current_time = datetime.utcnow()
        
        health_status = {
            "status": "healthy",
            "battery_level": robot.get("battery_level", 0),
            "cpu_usage": robot.get("cpu_usage", 0),
            "memory_usage": robot.get("memory_usage", 0),
            "disk_usage": robot.get("disk_usage", 0),
            "temperature": robot.get("temperature", 0),
            "uptime": robot.get("uptime", 0),
            "network_status": "connected" if agent and agent.get("status") == "online" else "disconnected",
            "last_seen": agent.get("last_seen").isoformat() if agent and agent.get("last_seen") else None
        }
        
        # Determine overall health status
        if not agent or agent.get("status") != "online":
            health_status["status"] = "offline"
        elif robot.get("battery_level", 100) < 20:
            health_status["status"] = "low_battery"
        elif robot.get("cpu_usage", 0) > 90 or robot.get("memory_usage", 0) > 90:
            health_status["status"] = "high_load"
        elif robot.get("temperature", 0) > 80:
            health_status["status"] = "overheating"
        
        return health_status
    
    def get_command_history(self, robot_id: str, limit: int = 50) -> List[dict]:
        """Get command history for a robot"""
        if robot_id not in self.command_history:
            return []
        
        commands = self.command_history[robot_id]
        return commands[-limit:] if len(commands) > limit else commands
    
    def register_agent(self, agent_id: str, agent_info: dict):
        """Register a new agent when it connects"""
        self.agents[agent_id] = {
            **agent_info,
            "last_seen": datetime.utcnow(),
            "status": "online",
            "registered_at": datetime.utcnow()
        }
        
        # If agent has robot info, register the robot too
        if "robot_info" in agent_info:
            self.register_robot(agent_id, agent_info["robot_info"])
        
        logger.info(f"Agent {agent_id} registered successfully")
    
    def register_robot(self, robot_id: str, robot_info: dict):
        """Register a robot with the system"""
        self.robots[robot_id] = {
            **robot_info,
            "id": robot_id,
            "status": "idle",
            "last_update": datetime.utcnow(),
            "agent_id": robot_id,  # Assuming robot_id == agent_id
            "battery_level": 0,
            "current_action": "idle"
        }
        logger.info(f"Robot {robot_id} registered")
    
    def update_agent_heartbeat(self, agent_id: str, data: dict = None):
        """Update agent last seen time and optional data"""
        if agent_id in self.agents:
            self.agents[agent_id]["last_seen"] = datetime.utcnow()
            self.agents[agent_id]["status"] = "online"
            
            if data:
                self.agents[agent_id].update(data)
            
            # Update associated robot status
            if agent_id in self.robots:
                self.robots[agent_id]["last_update"] = datetime.utcnow()
                if data and "robot_status" in data:
                    self.robots[agent_id].update(data["robot_status"])
    
    def update_robot_status(self, robot_id: str, status: dict):
        """Update robot status from agent"""
        if robot_id in self.robots:
            self.robots[robot_id].update(status)
            self.robots[robot_id]["last_update"] = datetime.utcnow()
            logger.info(f"Robot {robot_id} status updated: {status}")
    
    def get_robot(self, robot_id: str) -> Optional[dict]:
        """Get specific robot information"""
        return self.robots.get(robot_id)
    
    def get_all_robots(self) -> Dict[str, dict]:
        """Get all robots with their current status"""
        return self.robots.copy()
    
    def get_agent(self, agent_id: str) -> Optional[dict]:
        """Get specific agent information"""
        return self.agents.get(agent_id)
    
    def get_all_agents(self) -> Dict[str, dict]:
        """Get all agents with their status"""
        return self.agents.copy()
    
    def get_online_robots(self) -> List[dict]:
        """Get list of currently online robots"""
        online_robots = []
        current_time = datetime.utcnow()
        
        for robot_id, robot in self.robots.items():
            agent = self.agents.get(robot_id)
            if agent and agent.get("status") == "online":
                # Check if last seen was within reasonable time (e.g., 2 minutes)
                time_diff = (current_time - agent["last_seen"]).total_seconds()
                if time_diff < 120: # 2 minutes
                    online_robots.append(robot)
                else:
                    # Mark as offline
                    self.agents[robot_id]["status"] = "offline"
                    if robot_id in self.robots:
                        self.robots[robot_id]["status"] = "offline"
        
        return online_robots
    
    def get_exhibition_status(self) -> dict:
        """Get overall exhibition status"""
        total_robots = len(self.robots)
        online_robots = len(self.get_online_robots())
        active_robots = len([r for r in self.robots.values() if r.get("status") == "active"])
        
        return {
            "total_robots": total_robots,
            "online_robots": online_robots,
            "active_robots": active_robots,
            "exhibition_running": active_robots > 0,
            "last_update": datetime.utcnow().isoformat()
        }
    
    def set_robot_status(self, robot_id: str, status: str, action: str = None):
        """Set robot status (idle, active, stopped, error)"""
        if robot_id in self.robots:
            self.robots[robot_id]["status"] = status
            self.robots[robot_id]["last_update"] = datetime.utcnow()
            
            if action:
                self.robots[robot_id]["current_action"] = action
            
            logger.info(f"Robot {robot_id} status set to: {status}")
            return True
        return False
    
    def remove_agent(self, agent_id: str):
        """Remove agent and associated robot when disconnected"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            logger.info(f"Agent {agent_id} removed")
        
        if agent_id in self.robots:
            self.robots[agent_id]["status"] = "offline"
            logger.info(f"Robot {agent_id} marked offline")

# Global instance
robot_manager = RobotManager()
