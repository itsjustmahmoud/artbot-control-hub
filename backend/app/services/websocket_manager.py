from fastapi import WebSocket
from typing import Dict, List
from datetime import datetime
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages WebSocket connections for real-time communication"""
    
    def __init__(self):
        # Dictionary of connection types to list of WebSocket connections
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, connection_type: str):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        
        if connection_type not in self.active_connections:
            self.active_connections[connection_type] = []
        
        self.active_connections[connection_type].append(websocket)
        logger.info(f"New WebSocket connection: {connection_type}")
    
    def disconnect(self, websocket: WebSocket, connection_type: str):
        """Remove a WebSocket connection"""
        if connection_type in self.active_connections:
            if websocket in self.active_connections[connection_type]:
                self.active_connections[connection_type].remove(websocket)
                logger.info(f"WebSocket disconnected: {connection_type}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific WebSocket"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
    
    async def broadcast_to_type(self, message: dict, connection_type: str):
        """Broadcast a message to all connections of a specific type"""
        if connection_type not in self.active_connections:
            return
        
        message_str = json.dumps(message)
        connections = self.active_connections[connection_type].copy()
        
        for connection in connections:
            try:
                await connection.send_text(message_str)
            except Exception as e:
                logger.error(f"Error broadcasting to {connection_type}: {e}")
                # Remove failed connection
                self.disconnect(connection, connection_type)
    
    async def send_to_agent(self, agent_id: str, message: dict):
        """Send a command to a specific agent"""
        connection_type = f"agent:{agent_id}"
        if connection_type in self.active_connections:
            message_str = json.dumps(message)
            connections = self.active_connections[connection_type].copy()
            
            for connection in connections:
                try:
                    await connection.send_text(message_str)
                    logger.info(f"Command sent to agent {agent_id}: {message}")
                    return True
                except Exception as e:
                    logger.error(f"Error sending to agent {agent_id}: {e}")
                    self.disconnect(connection, connection_type)
        
        logger.warning(f"Agent {agent_id} not connected")
        return False
    
    def get_connected_agents(self) -> List[str]:
        """Get list of currently connected agent IDs"""
        agents = []
        for connection_type in self.active_connections:
            if connection_type.startswith("agent:"):
                agent_id = connection_type.replace("agent:", "")
                if self.active_connections[connection_type]:  # Has active connections
                    agents.append(agent_id)
        return agents
    
    def get_connection_stats(self) -> Dict[str, int]:
        """Get statistics about current connections"""
        stats = {}
        for connection_type, connections in self.active_connections.items():
            stats[connection_type] = len(connections)
        return stats
    
    async def broadcast_robot_update(self, robot_id: str, robot_data: dict):
        """Broadcast robot status update to dashboard clients"""
        message = {
            "type": "robot_update",
            "robot_id": robot_id,
            "data": robot_data,
            "timestamp": robot_data.get("last_update")
        }
        
        # Send to all dashboard connections
        await self.broadcast_to_type(message, "dashboard")
        logger.info(f"Robot update broadcasted for {robot_id}")
    
    async def broadcast_log_message(self, log_entry: dict):
        """Broadcast new log message to dashboard clients"""
        message = {
            "type": "log_message",
            "data": log_entry
        }
        
        await self.broadcast_to_type(message, "dashboard")
    
    async def broadcast_system_alert(self, alert_type: str, message: str, severity: str = "info"):
        """Broadcast system alert to all connected dashboards"""
        alert_message = {
            "type": "system_alert",
            "alert_type": alert_type,
            "message": message,
            "severity": severity,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.broadcast_to_type(alert_message, "dashboard")
        logger.info(f"System alert broadcasted: {alert_type}")
    
    async def handle_agent_message(self, agent_id: str, message: dict):
        """Handle incoming message from agent"""
        from app.services.robot_manager import robot_manager
        
        message_type = message.get("type")
        
        if message_type == "heartbeat":
            # Update agent heartbeat
            robot_manager.update_agent_heartbeat(agent_id, message.get("data", {}))
            
        elif message_type == "robot_status":
            # Update robot status
            robot_data = message.get("data", {})
            robot_manager.update_robot_status(agent_id, robot_data)
            
            # Broadcast to dashboards
            await self.broadcast_robot_update(agent_id, robot_data)
            
        elif message_type == "log_entry":
            # Handle log from agent
            log_data = message.get("data", {})
            robot_manager.add_robot_log(agent_id, log_data)
            
            # Broadcast to dashboards
            await self.broadcast_log_message({
                **log_data,
                "robot_id": agent_id,
                "source": "robot"
            })
            
        elif message_type == "command_response":
            # Handle command response from agent
            command_id = message.get("command_id")
            success = message.get("success", False)
            
            logger.info(f"Command {command_id} response from {agent_id}: {'success' if success else 'failed'}")
            
            # Broadcast command result
            await self.broadcast_to_type({
                "type": "command_response",
                "agent_id": agent_id,
                "command_id": command_id,                "success": success,
                "data": message.get("data", {})
            }, "dashboard")
        
        else:
            logger.warning(f"Unknown message type from agent {agent_id}: {message_type}. Full message: {message}")
