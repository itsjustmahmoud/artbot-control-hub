import asyncio
import subprocess
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class CommandHandler:
    """Handles commands received from the control hub"""
    
    def __init__(self, config):
        self.config = config
    
    async def handle_command(self, command_data):
        """Process incoming command from hub"""
        command_type = command_data.get("type")
        action = command_data.get("action")
        parameters = command_data.get("parameters", {})
        
        logger.info(f"Handling command: {command_type} - {action}")
        
        try:
            if command_type == "robot_command":
                return await self.handle_robot_command(action, parameters)
            elif command_type == "system_command":
                return await self.handle_system_command(action, parameters)
            else:
                logger.warning(f"Unknown command type: {command_type}")
                return {"status": "error", "message": f"Unknown command type: {command_type}"}
                
        except Exception as e:
            logger.error(f"Command handling error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def handle_robot_command(self, action, parameters):
        """Handle robot-specific commands"""
        if action == "start":
            return await self.start_robot()
        elif action == "stop":
            return await self.stop_robot()
        elif action == "restart":
            return await self.restart_robot()
        elif action == "status":
            return await self.get_robot_status()
        else:
            return {"status": "error", "message": f"Unknown robot action: {action}"}
    
    async def handle_system_command(self, action, parameters):
        """Handle system-level commands"""
        if action == "reboot":
            return await self.reboot_system()
        elif action == "update":
            return await self.update_agent()
        elif action == "logs":
            return await self.get_logs()
        else:
            return {"status": "error", "message": f"Unknown system action: {action}"}
    
    async def start_robot(self):
        """Start the robot person following system"""
        try:
            # Command to start ROS2 person following system
            cmd = [
                "bash", "-c",
                f"source {self.config.ros2_workspace}/install/setup.bash && "
                f"ros2 launch {self.config.ros2_package} person_following_launch.py"
            ]
            
            # Start process in background
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            logger.info("Robot start command executed")
            
            return {
                "status": "success",
                "message": "Robot start command sent",
                "process_id": process.pid,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to start robot: {e}")
            return {"status": "error", "message": f"Failed to start robot: {str(e)}"}
    
    async def stop_robot(self):
        """Stop the robot person following system"""
        try:
            # Kill all ROS2 processes related to person following
            cmd = ["pkill", "-f", self.config.ros2_package]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.wait()
            
            logger.info("Robot stop command executed")
            
            return {
                "status": "success",
                "message": "Robot stopped",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to stop robot: {e}")
            return {"status": "error", "message": f"Failed to stop robot: {str(e)}"}
    
    async def restart_robot(self):
        """Restart the robot system"""
        try:
            # Stop first
            await self.stop_robot()
            
            # Wait a moment
            await asyncio.sleep(2)
            
            # Start again
            result = await self.start_robot()
            
            if result["status"] == "success":
                result["message"] = "Robot restarted successfully"
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to restart robot: {e}")
            return {"status": "error", "message": f"Failed to restart robot: {str(e)}"}
    
    async def get_robot_status(self):
        """Get current robot status"""
        try:
            # Check if ROS2 processes are running
            cmd = ["pgrep", "-f", self.config.ros2_package]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            is_running = len(stdout.decode().strip()) > 0
            
            return {
                "status": "success",
                "robot_status": {
                    "running": is_running,
                    "processes": stdout.decode().strip().split('\n') if is_running else [],
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get robot status: {e}")
            return {"status": "error", "message": f"Failed to get robot status: {str(e)}"}
    
    async def reboot_system(self):
        """Reboot the entire system"""
        try:
            logger.warning("System reboot requested")
            
            # Schedule reboot in 10 seconds to allow response to be sent
            await asyncio.create_subprocess_exec("sudo", "shutdown", "-r", "+1")
            
            return {
                "status": "success",
                "message": "System reboot scheduled in 1 minute",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to reboot system: {e}")
            return {"status": "error", "message": f"Failed to reboot system: {str(e)}"}
    
    async def update_agent(self):
        """Update the agent software"""
        # Placeholder for agent update logic
        return {
            "status": "success", 
            "message": "Agent update not implemented yet",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_logs(self):
        """Get recent system logs"""
        try:
            # Get last 50 lines of system log
            process = await asyncio.create_subprocess_exec(
                "journalctl", "-n", "50", "--no-pager",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            return {
                "status": "success",
                "logs": stdout.decode(),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get logs: {e}")
            return {"status": "error", "message": f"Failed to get logs: {str(e)}"}
