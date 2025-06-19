from typing import Dict, List, Optional
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

class CommandService:
    """Handles robot command creation, tracking and execution"""
    
    def __init__(self):
        self.command_history: Dict[str, List[dict]] = {}
        self.pending_commands: Dict[str, dict] = {}
        
    async def send_command_to_robot(self, robot_id: str, action: str, parameters: dict = None, websocket_manager=None) -> dict:
        """Create and send command to robot via WebSocket"""
        if not websocket_manager:
            raise Exception("WebSocket manager not provided")
            
        command_id = str(uuid.uuid4())
        command_data = {
            "command_id": command_id,
            "robot_id": robot_id,
            "type": "robot_command",
            "action": action,
            "parameters": parameters or {},
            "timestamp": datetime.utcnow().isoformat(),
            "status": "pending"
        }
        
        # Store command in history
        if robot_id not in self.command_history:
            self.command_history[robot_id] = []
            
        self.command_history[robot_id].append(command_data.copy())
        self.pending_commands[command_id] = command_data.copy()
        
        # Send via WebSocket
        success = await websocket_manager.send_to_agent(robot_id, command_data)
        
        if not success:
            # Update command status to failed
            command_data["status"] = "failed"
            command_data["error"] = f"Failed to send command to robot {robot_id}"
            self._update_command_status(command_id, "failed", error="WebSocket send failed")
            raise Exception(f"Failed to send command to robot {robot_id}")
        
        # Update status to sent
        self._update_command_status(command_id, "sent")
        
        logger.info(f"Command {command_id} sent to robot {robot_id}: {action}")
        return command_data
        
    def handle_command_response(self, command_id: str, response_data: dict):
        """Handle response from robot for a command"""
        if command_id not in self.pending_commands:
            logger.warning(f"Received response for unknown command {command_id}")
            return
            
        command = self.pending_commands[command_id]
        status = response_data.get("status", "completed")
        error = response_data.get("error")
        
        self._update_command_status(command_id, status, response_data, error)
        
        # Remove from pending if completed or failed
        if status in ["completed", "failed"]:
            del self.pending_commands[command_id]
            
        logger.info(f"Command {command_id} response: {status}")
        
    def _update_command_status(self, command_id: str, status: str, response_data: dict = None, error: str = None):
        """Update command status in history"""
        command = self.pending_commands.get(command_id)
        if not command:
            return
            
        robot_id = command["robot_id"]
        
        # Update in history
        for cmd in self.command_history.get(robot_id, []):
            if cmd["command_id"] == command_id:
                cmd["status"] = status
                cmd["completed_at"] = datetime.utcnow().isoformat()
                if response_data:
                    cmd["response"] = response_data
                if error:
                    cmd["error"] = error
                break
                
        # Update pending command
        if command_id in self.pending_commands:
            self.pending_commands[command_id]["status"] = status
            if error:
                self.pending_commands[command_id]["error"] = error
                
    def get_command_history(self, robot_id: str, limit: int = 50) -> List[dict]:
        """Get command history for a robot"""
        history = self.command_history.get(robot_id, [])
        return sorted(history, key=lambda x: x["timestamp"], reverse=True)[:limit]
        
    def get_pending_commands(self, robot_id: str = None) -> List[dict]:
        """Get pending commands, optionally filtered by robot_id"""
        if robot_id:
            return [cmd for cmd in self.pending_commands.values() 
                   if cmd["robot_id"] == robot_id]
        return list(self.pending_commands.values())
        
    def cancel_command(self, command_id: str) -> bool:
        """Cancel a pending command"""
        if command_id in self.pending_commands:
            self._update_command_status(command_id, "cancelled")
            del self.pending_commands[command_id]
            logger.info(f"Command {command_id} cancelled")
            return True
        return False
        
    def get_command_statistics(self, robot_id: str = None) -> dict:
        """Get command execution statistics"""
        if robot_id:
            commands = self.command_history.get(robot_id, [])
        else:
            commands = []
            for robot_commands in self.command_history.values():
                commands.extend(robot_commands)
                
        total_commands = len(commands)
        completed = len([cmd for cmd in commands if cmd["status"] == "completed"])
        failed = len([cmd for cmd in commands if cmd["status"] == "failed"])
        pending = len(self.get_pending_commands(robot_id))
        
        return {
            "total_commands": total_commands,
            "completed": completed,
            "failed": failed,
            "pending": pending,
            "success_rate": (completed / total_commands * 100) if total_commands > 0 else 0
        }
