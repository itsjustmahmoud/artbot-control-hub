import asyncio
import subprocess
import json
import logging
import os
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
        if action == "start_workspace":
            return await self.start_workspace()
        elif action == "stop_workspace":
            return await self.stop_workspace()
        elif action == "restart_create3":
            return await self.restart_create3()
        elif action == "reboot_create3":
            return await self.reboot_create3()
        elif action == "status":
            return await self.get_robot_status()
        elif action == "get_logs":
            return await self.get_workspace_logs()
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
    
    async def start_workspace(self):
        """Start the workspace run command"""
        try:
            # Navigate to workspace directory and run ./workspace run
            workspace_dir = os.getenv("WORKSPACE_DIR", "/home/artbot/workspace")
            cmd = ["./workspace", "run"]
            
            # Check if workspace directory exists
            if not os.path.exists(workspace_dir):
                return {"status": "error", "message": "Workspace directory not found"}
            
            # Start process in background
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=workspace_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            logger.info("Workspace start command executed")
            
            return {
                "status": "success",
                "message": "Workspace started successfully",
                "process_id": process.pid,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to start workspace: {e}")
            return {"status": "error", "message": f"Failed to start workspace: {str(e)}"}
    
    async def stop_workspace(self):
        """Stop the workspace run command"""
        try:
            # Kill processes related to workspace run
            cmd = ["pkill", "-f", "workspace run"]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.wait()
            
            logger.info("Workspace stop command executed")
            
            return {
                "status": "success",
                "message": "Workspace stopped successfully",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to stop workspace: {e}")
            return {"status": "error", "message": f"Failed to stop workspace: {str(e)}"}
    
    async def restart_create3(self):
        """Restart Create3 robot software"""
        try:
            # Send restart command to Create3 via its API
            import aiohttp
            
            # Get Create3 IP from environment or use default
            create3_ip = os.getenv("CREATE3_IP", "192.168.186.2")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"http://{create3_ip}/api/restart",
                    timeout=5
                ) as response:
                    if response.status == 200:
                        logger.info("Create3 restart command sent")
                        return {
                            "status": "success",
                            "message": "Create3 restart command sent",
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    else:
                        return {"status": "error", "message": f"Create3 restart failed: HTTP {response.status}"}
                        
        except Exception as e:
            logger.error(f"Failed to restart Create3: {e}")
            return {"status": "error", "message": f"Failed to restart Create3: {str(e)}"}
    
    async def reboot_create3(self):
        """Reboot Create3 robot hardware"""
        try:
            # Send reboot command to Create3 via its API
            import aiohttp
            
            # Get Create3 IP from environment or use default
            create3_ip = os.getenv("CREATE3_IP", "192.168.186.2")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"http://{create3_ip}/api/reboot",
                    timeout=5
                ) as response:
                    if response.status == 200:
                        logger.info("Create3 reboot command sent")
                        return {
                            "status": "success",
                            "message": "Create3 reboot command sent",
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    else:
                        return {"status": "error", "message": f"Create3 reboot failed: HTTP {response.status}"}
                        
        except Exception as e:
            logger.error(f"Failed to reboot Create3: {e}")
            return {"status": "error", "message": f"Failed to reboot Create3: {str(e)}"}
    
    async def get_workspace_logs(self):
        """Get workspace logs"""
        try:
            # Read workspace log files
            log_dir = os.getenv("WORKSPACE_LOG_DIR", "/home/artbot/workspace/logs")
            logs = []
            
            if os.path.exists(log_dir):
                for log_file in os.listdir(log_dir):
                    if log_file.endswith('.log'):
                        log_path = os.path.join(log_dir, log_file)
                        try:
                            with open(log_path, 'r') as f:
                                # Read last 50 lines
                                lines = f.readlines()
                                logs.extend(lines[-50:])
                        except Exception as e:
                            logger.warning(f"Could not read log file {log_path}: {e}")
            
            return {
                "status": "success",
                "logs": logs[-100:],  # Return last 100 lines
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get workspace logs: {e}")
            return {"status": "error", "message": f"Failed to get logs: {str(e)}"}
    
    async def get_robot_status(self):
        """Get current robot status"""
        try:
            # Check if workspace is running
            workspace_running = False
            try:
                result = subprocess.run(
                    ["pgrep", "-f", "workspace run"],
                    capture_output=True,
                    text=True
                )
                workspace_running = result.returncode == 0
            except:
                pass
            
            # Check Create3 connectivity
            create3_connected = False
            create3_ip = os.getenv("CREATE3_IP", "192.168.186.2")
            try:
                result = subprocess.run(
                    ["ping", "-c", "1", "-W", "1", create3_ip],
                    capture_output=True,
                    timeout=2
                )
                create3_connected = result.returncode == 0
            except:
                pass
            
            return {
                "status": "success",
                "robot_status": {
                    "workspace_running": workspace_running,
                    "create3_connected": create3_connected,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get robot status: {e}")
            return {"status": "error", "message": f"Failed to get status: {str(e)}"}
    
    async def reboot_system(self):
        """Reboot the Raspberry Pi system"""
        try:
            logger.warning("System reboot command received")
            
            # Schedule reboot in 1 minute to allow response to be sent
            cmd = ["sudo", "shutdown", "-r", "+1"]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            return {
                "status": "success",
                "message": "System reboot scheduled in 1 minute",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to reboot system: {e}")
            return {"status": "error", "message": f"Failed to reboot: {str(e)}"}
    
    async def update_agent(self):
        """Update the agent software"""
        try:
            # Get the current working directory (should be the agent directory)
            agent_dir = os.path.dirname(os.path.abspath(__file__))
            repo_dir = os.path.abspath(os.path.join(agent_dir, "../../"))
            
            # Pull latest changes from git
            cmd = ["git", "pull", "origin", "main"]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=repo_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return {
                    "status": "success",
                    "message": "Agent update completed",
                    "output": stdout.decode(),
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "status": "error",
                    "message": "Agent update failed",
                    "error": stderr.decode(),
                    "timestamp": datetime.utcnow().isoformat()
                }
            
        except Exception as e:
            logger.error(f"Failed to update agent: {e}")
            return {"status": "error", "message": f"Failed to update: {str(e)}"}
    
    async def get_logs(self):
        """Get system logs"""
        try:
            # Get recent system logs
            cmd = ["journalctl", "-n", "50", "--no-pager"]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return {
                    "status": "success",
                    "logs": stdout.decode().split('\n'),
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "status": "error",
                    "message": "Failed to get system logs",
                    "error": stderr.decode(),
                    "timestamp": datetime.utcnow().isoformat()
                }
            
        except Exception as e:
            logger.error(f"Failed to get system logs: {e}")
            return {"status": "error", "message": f"Failed to get logs: {str(e)}"}
