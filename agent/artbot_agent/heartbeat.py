import asyncio
import aiohttp
import json
import logging
from datetime import datetime
from .system_monitor import SystemMonitor

logger = logging.getLogger(__name__)

class HeartbeatManager:
    """Manages periodic heartbeat to the control hub"""
    
    def __init__(self, config):
        self.config = config
        self.running = False
        self.system_monitor = SystemMonitor(config)
    
    async def send_heartbeat(self):
        """Send heartbeat with essential metrics to hub"""
        try:
            # Get essential metrics only
            essential_metrics = await self.system_monitor.get_essential_metrics()
            
            heartbeat_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "status": "online",
                **essential_metrics  # Flatten the essential metrics into heartbeat
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.config.get_heartbeat_url(),
                    json=heartbeat_data
                ) as response:
                    if response.status == 200:
                        logger.debug("Heartbeat sent successfully")
                    else:
                        logger.warning(f"Heartbeat failed with status {response.status}")
                        
        except Exception as e:
            logger.error(f"Heartbeat error: {e}")
    
    async def get_system_metrics(self):
        """Get current system metrics"""
        try:
            import psutil
            
            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent,
                "uptime": datetime.utcnow().isoformat()
            }
        except ImportError:
            return {
                "cpu_percent": 0,
                "memory_percent": 0,
                "disk_percent": 0,
                "uptime": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {}
    
    async def start(self):
        """Start heartbeat loop"""
        self.running = True
        logger.info(f"Starting heartbeat every {self.config.heartbeat_interval} seconds")
        
        while self.running:
            await self.send_heartbeat()
            await asyncio.sleep(self.config.heartbeat_interval)
        
        logger.info("Heartbeat stopped")
    
    def stop(self):
        """Stop heartbeat"""
        self.running = False
