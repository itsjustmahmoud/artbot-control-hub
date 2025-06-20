from typing import Dict, List, Optional
from datetime import datetime
import logging

from .robot_registry import RobotRegistryService
from .agent_registry import AgentRegistryService
from .command_service import CommandService
from .logging_service import LoggingService
from .health_monitoring import HealthMonitoringService

logger = logging.getLogger(__name__)

class RobotManager:
    """
    Orchestrates robot management using specialized services.
    This is the main facade that coordinates between different services.
    """
    
    def __init__(self):
        # Initialize all services
        self.robot_registry = RobotRegistryService()
        self.agent_registry = AgentRegistryService()
        self.command_service = CommandService()
        self.logging_service = LoggingService()
        self.health_service = HealthMonitoringService()
        
        # WebSocket manager reference (set by main.py)
        self.websocket_manager = None
        
        logger.info("Robot Manager initialized with modular services")
    
    # Robot Registry Methods
    def register_robot(self, robot_id: str, robot_info: dict):
        """Register a new robot"""
        robot_data = self.robot_registry.register_robot(robot_id, robot_info)
        
        # Log the registration
        self.logging_service.add_system_log({
            "level": "INFO",
            "message": f"Robot {robot_id} registered",
            "component": "robot_manager",
            "robot_id": robot_id
        })
        
        return robot_data
    
    def get_robot(self, robot_id: str) -> Optional[dict]:
        """Get specific robot information"""
        return self.robot_registry.get_robot(robot_id)
    
    def get_all_robots(self) -> Dict[str, dict]:
        """Get all registered robots"""
        return self.robot_registry.get_all_robots()
    
    def get_online_robots(self) -> List[dict]:
        """Get robots that are currently online"""
        return self.robot_registry.get_online_robots()
    
    def update_robot_status(self, robot_id: str, status_data: dict):
        """Update robot status and metrics"""
        success = self.robot_registry.update_robot_status(robot_id, status_data)
        
        if success:
            # Update health monitoring if health data is present
            if any(key in status_data for key in ['battery_level', 'cpu_usage', 'memory_usage', 'temperature']):
                self.health_service.update_robot_health(robot_id, status_data)            # Broadcast update via WebSocket
            if self.websocket_manager:
                import asyncio
                asyncio.create_task(self.websocket_manager.broadcast_to_type({
                    "type": "robot_update",
                    "robot_id": robot_id,
                    "data": status_data
                }, "dashboard"))
        
        return success
    
    def set_robot_status(self, robot_id: str, status: str, action: str = None):
        """Set robot status and current action"""
        success = self.robot_registry.set_robot_status(robot_id, status, action)
        
        if success:
            # Log the status change
            self.logging_service.add_robot_log(robot_id, {
                "level": "INFO",
                "message": f"Status changed to {status}" + (f" with action {action}" if action else ""),                "source": "robot_manager"
            })
        
        return success
    
    # Agent Registry Methods
    def register_agent(self, agent_id: str, agent_info: dict):
        """Register a new agent and create corresponding robot entry"""
        logger.info(f"Registering agent {agent_id} with info: {agent_info}")
        
        agent_data = self.agent_registry.register_agent(agent_id, agent_info)
          # Also register this agent as a robot in the robot registry
        robot_info = {
            "name": agent_info.get("hostname", f"Robot {agent_id}"),
            "hostname": agent_info.get("hostname", f"unknown-{agent_id}"),  # Pi hostname
            "ip_address": agent_info.get("ip_address", "unknown"),
            "battery_level": 100,  # Default, will be updated by heartbeat
            "cpu_usage": 0,        # Default, will be updated by heartbeat
            "memory_usage": 0,     # Default, will be updated by heartbeat
            "temperature": 25,     # Default, will be updated by heartbeat
            "location": "Museum",  # Default location
            "capabilities": agent_info.get("robot_info", {}).get("capabilities", []),
            # Initialize connectivity status
            "create3_connected": False,  # Will be updated by heartbeat
            "oak_connected": False,      # Will be updated by heartbeat
            "workspace_running": False,  # Will be updated by heartbeat
            "uptime": 0                  # Will be updated by heartbeat
        }
        
        logger.info(f"Creating robot entry for agent {agent_id} with data: {robot_info}")
        robot_data = self.register_robot(agent_id, robot_info)
        logger.info(f"Robot registered successfully: {robot_data}")
          # Log the registration
        self.logging_service.add_system_log({
            "level": "INFO",
            "message": f"Agent {agent_id} registered from {agent_info.get('ip_address', 'unknown')}",
            "component": "robot_manager"
        })
        
        return agent_data
    
    def update_agent_heartbeat(self, agent_id: str, data: dict = None):
        """Update agent heartbeat and robot status"""
        logger.debug(f"Processing heartbeat for agent {agent_id} with data: {data}")
        
        try:
            success = self.agent_registry.update_agent_heartbeat(agent_id, data)
            logger.debug(f"Agent registry update success: {success}")
            
            if success and data:
                # Extract robot metrics from heartbeat data and update robot registry
                robot_update = {}
                
                # Map agent heartbeat data to robot fields
                if "cpu_percent" in data:
                    robot_update["cpu_usage"] = data["cpu_percent"]
                if "memory_percent" in data:
                    robot_update["memory_usage"] = data["memory_percent"]
                if "temperature" in data:
                    robot_update["temperature"] = data["temperature"]
                if "battery_level" in data:
                    robot_update["battery_level"] = data["battery_level"]
                if "workspace_running" in data:
                    robot_update["current_action"] = "person_following" if data["workspace_running"] else "idle"
                    robot_update["workspace_running"] = data["workspace_running"]
                if "create3_connected" in data:
                    robot_update["create3_connected"] = data["create3_connected"]
                if "create3_status" in data:
                    robot_update["create3_status"] = data["create3_status"]
                if "oak_connected" in data:
                    robot_update["oak_connected"] = data["oak_connected"]
                if "uptime" in data:
                    robot_update["uptime"] = data["uptime"]
                    
                logger.debug(f"Robot update data: {robot_update}")
                
                # Update robot status if we have metrics
                if robot_update:
                    robot_success = self.update_robot_status(agent_id, robot_update)
                    logger.debug(f"Robot status update success: {robot_success}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error in update_agent_heartbeat for {agent_id}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    def get_agent(self, agent_id: str) -> Optional[dict]:
        """Get specific agent information"""
        return self.agent_registry.get_agent(agent_id)
    
    def get_all_agents(self) -> Dict[str, dict]:
        """Get all registered agents"""
        return self.agent_registry.get_all_agents()
    
    def remove_agent(self, agent_id: str):
        """Remove agent and mark associated robot as offline"""
        success = self.agent_registry.remove_agent(agent_id)
        
        if success:
            # Mark associated robot as offline
            self.set_robot_status(agent_id, "offline")
            
            # Log the disconnection
            self.logging_service.add_system_log({
                "level": "WARNING",
                "message": f"Agent {agent_id} disconnected",
                "component": "robot_manager"
            })
        
        return success
    
    # Command Service Methods
    async def send_command_to_robot(self, robot_id: str, action: str, parameters: dict = None) -> dict:
        """Send command to robot via WebSocket"""
        try:
            command_data = await self.command_service.send_command_to_robot(
                robot_id, action, parameters, self.websocket_manager
            )
            
            # Update robot status based on command
            if action == "start":
                self.set_robot_status(robot_id, "active", "person_following")
            elif action == "stop":
                self.set_robot_status(robot_id, "idle", "stopped")
            elif action == "restart":
                self.set_robot_status(robot_id, "restarting", "system_restart")
            elif action == "reboot":
                self.set_robot_status(robot_id, "rebooting", "system_reboot")
            
            return command_data
            
        except Exception as e:
            # Log the error
            self.logging_service.add_robot_log(robot_id, {
                "level": "ERROR",
                "message": f"Failed to send command {action}: {str(e)}",
                "source": "robot_manager"
            })
            raise
    
    def get_command_history(self, robot_id: str, limit: int = 50) -> List[dict]:
        """Get command history for a robot"""
        return self.command_service.get_command_history(robot_id, limit)
    
    # Logging Service Methods
    def add_robot_log(self, robot_id: str, log_entry: dict):
        """Add a log entry for a specific robot"""
        self.logging_service.add_robot_log(robot_id, log_entry)
    
    def get_robot_logs(self, robot_id: str, limit: int = 100) -> List[dict]:
        """Get logs for a specific robot"""
        return self.logging_service.get_robot_logs(robot_id, limit)
    
    # Health Monitoring Methods
    def get_robot_health(self, robot_id: str) -> dict:
        """Get robot health information"""
        health = self.health_service.get_robot_health(robot_id)
        if not health:
            # Return basic health info if no monitoring data
            robot = self.get_robot(robot_id)
            if robot:
                return {
                    "robot_id": robot_id,
                    "status": "unknown",
                    "battery_level": robot.get("battery_level", 0),
                    "last_update": robot.get("last_update", ""),
                    "health_score": 0
                }
        return health
    
    def get_critical_alerts(self) -> List[dict]:
        """Get critical health alerts"""
        return self.health_service.get_critical_alerts()
    
    # Exhibition Control Methods
    def get_exhibition_status(self) -> dict:
        """Get current exhibition status"""
        robots = list(self.robot_registry.get_all_robots().values())
        online_robots = self.robot_registry.get_online_robots()
        active_robots = self.robot_registry.get_active_robots()
        
        return {
            "total_robots": len(robots),
            "online_robots": len(online_robots),
            "active_robots": len(active_robots),
            "exhibition_running": len(active_robots) > 0,
            "last_update": datetime.utcnow().isoformat()
        }
    
    async def start_exhibition(self) -> dict:
        """Start all available robots"""
        online_robots = self.get_online_robots()
        results = []
        
        for robot in online_robots:
            try:
                result = await self.send_command_to_robot(robot["id"], "start")
                results.append({"robot_id": robot["id"], "status": "success", "command": result})
            except Exception as e:
                results.append({"robot_id": robot["id"], "status": "error", "error": str(e)})
        
        self.logging_service.add_system_log({
            "level": "INFO",
            "message": f"Exhibition started - {len([r for r in results if r['status'] == 'success'])} robots activated",
            "component": "robot_manager"
        })
        
        return {"results": results, "total_robots": len(online_robots)}
    
    async def stop_exhibition(self) -> dict:
        """Stop all active robots"""
        active_robots = self.robot_registry.get_active_robots()
        results = []
        
        for robot in active_robots:
            try:
                result = await self.send_command_to_robot(robot["id"], "stop")
                results.append({"robot_id": robot["id"], "status": "success", "command": result})
            except Exception as e:
                results.append({"robot_id": robot["id"], "status": "error", "error": str(e)})
        
        self.logging_service.add_system_log({
            "level": "INFO",
            "message": f"Exhibition stopped - {len([r for r in results if r['status'] == 'success'])} robots deactivated",
            "component": "robot_manager"
        })
        
        return {"results": results, "total_robots": len(active_robots)}

# Global instance
robot_manager = RobotManager()
