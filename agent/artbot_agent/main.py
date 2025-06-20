import asyncio
import aiohttp
import websockets
import json
import logging
import signal
import sys
from datetime import datetime

from .config import AgentConfig
from .heartbeat import HeartbeatManager
from .command_handler import CommandHandler
from .system_monitor import SystemMonitor
from .auto_discovery import AutoDiscovery
from .create3_monitor import initialize_create3_monitoring, shutdown_create3_monitoring
from .oakd_monitor import initialize_oakd_monitoring

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ArtbotAgent:
    """Main Artbot Agent class"""
    
    def __init__(self):
        self.config = AgentConfig()
        self.heartbeat_manager = HeartbeatManager(self.config)
        self.command_handler = CommandHandler(self.config)
        self.system_monitor = SystemMonitor(self.config)
        self.auto_discovery = AutoDiscovery(self.config)
        
        self.websocket = None
        self.running = False
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    async def register_with_hub(self):
        """Register this agent with the control hub"""
        registration_data = {
            "agent_id": self.config.agent_id,
            "hostname": self.config.hostname,
            "ip_address": self.config.get_local_ip(),
            "system_info": self.config.get_system_info(),
            "robot_info": await self.auto_discovery.detect_robot_info()
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.config.get_registration_url(),
                    json=registration_data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"Successfully registered with hub: {result}")
                        return True
                    else:
                        logger.error(f"Registration failed with status {response.status}")
                        return False
        except Exception as e:
            logger.error(f"Registration failed: {e}")
            return False
    
    async def connect_websocket(self):
        """Establish WebSocket connection with hub"""
        max_retries = 5
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Connecting to WebSocket (attempt {attempt + 1}/{max_retries})")
                
                self.websocket = await websockets.connect(
                    self.config.get_websocket_url(),
                    ping_interval=20,
                    ping_timeout=10
                )
                
                logger.info("WebSocket connection established")
                return True
                
            except Exception as e:
                logger.error(f"WebSocket connection failed: {e}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
        
        return False
    
    async def handle_websocket_messages(self):
        """Handle incoming WebSocket messages from hub"""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    logger.info(f"Received command: {data}")
                    
                    # Handle the command
                    response = await self.command_handler.handle_command(data)
                    
                    # Send response back if needed
                    if response:
                        await self.websocket.send(json.dumps(response))
                        
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON received: {message}")
                except Exception as e:
                    logger.error(f"Error handling message: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.warning("WebSocket connection closed by server")
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
    
    async def start_background_tasks(self):
        """Start background tasks (heartbeat, monitoring, WebSocket heartbeat)"""
        tasks = [
            asyncio.create_task(self.heartbeat_manager.start()),
            asyncio.create_task(self.system_monitor.start()),
            asyncio.create_task(self.websocket_heartbeat_loop()),
            asyncio.create_task(self.websocket_status_loop()),
        ]
        
        logger.info("Background tasks started")
        return tasks
      
    async def send_websocket_message(self, message_type: str, data: dict):
        """Send message via WebSocket"""
        if not self.websocket:
            logger.warning(f"Cannot send {message_type}: WebSocket not connected")
            return False
            
        try:
            message = {
                "type": message_type,
                "agent_id": self.config.agent_id,
                "timestamp": datetime.utcnow().isoformat(),
                "data": data
            }
            
            await self.websocket.send(json.dumps(message))
            logger.debug(f"Sent {message_type} message via WebSocket")
            return True
            
        except Exception as e:
            logger.error(f"Error sending {message_type} via WebSocket: {e}")
            return False

    async def websocket_heartbeat_loop(self):
        """Send periodic heartbeat via WebSocket"""
        while self.running:
            try:
                # Get essential metrics for heartbeat
                essential_metrics = await self.system_monitor.get_essential_metrics()
                
                await self.send_websocket_message("heartbeat", essential_metrics)
                
                # Wait for heartbeat interval
                await asyncio.sleep(self.config.heartbeat_interval)
                
            except Exception as e:
                logger.error(f"WebSocket heartbeat error: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    async def websocket_status_loop(self):
        """Send periodic status updates via WebSocket"""
        while self.running:
            try:
                # Get robot status
                robot_status = await self.system_monitor.get_essential_metrics()
                
                await self.send_websocket_message("robot_status", robot_status)
                
                # Wait for monitor interval
                await asyncio.sleep(self.config.monitor_interval)
                
            except Exception as e:
                logger.error(f"WebSocket status update error: {e}")
                await asyncio.sleep(5)  # Wait before retrying

    async def run(self):
        """Main agent loop with reconnection support"""
        logger.info(f"Starting Artbot Agent {self.config.agent_id}")
        
        # Initialize Create3 monitoring
        logger.info("Initializing Create3 monitoring...")
        initialize_create3_monitoring()
        
        # Initialize OAK-D monitoring
        logger.info("Initializing OAK-D monitoring...")
        initialize_oakd_monitoring()
        
        # Register with hub
        if not await self.register_with_hub():
            logger.error("Failed to register with hub, exiting")
            return
        
        self.running = True
        
        # Main loop with reconnection
        while self.running:
            try:
                # Connect WebSocket
                if not await self.connect_websocket():
                    logger.error("Failed to establish WebSocket connection, retrying in 10 seconds...")
                    await asyncio.sleep(10)
                    continue
                
                # Start background tasks
                background_tasks = await self.start_background_tasks()
                
                # Handle WebSocket messages
                await self.handle_websocket_messages()
                
            except Exception as e:
                logger.error(f"Agent error: {e}")
            finally:
                # Cleanup for this iteration
                try:
                    # Cancel background tasks
                    if 'background_tasks' in locals():
                        for task in background_tasks:
                            task.cancel()
                    
                    # Close WebSocket
                    if self.websocket:
                        await self.websocket.close()
                        self.websocket = None
                        
                except Exception as e:
                    logger.error(f"Cleanup error: {e}")
                
                # If still running, wait before reconnecting
                if self.running:
                    logger.info("WebSocket disconnected, reconnecting in 5 seconds...")
                    await asyncio.sleep(5)
        
        # Final cleanup
        logger.info("Shutting down Create3 monitoring...")
        shutdown_create3_monitoring()
        logger.info("Agent stopped")

async def main():
    """Entry point for the agent"""
    agent = ArtbotAgent()
    await agent.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Agent stopped by user")
