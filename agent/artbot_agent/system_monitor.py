import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class SystemMonitor:
    """Monitors system metrics and robot status"""
    
    def __init__(self, config):
        self.config = config
        self.running = False
    
    async def get_system_metrics(self):
        """Get comprehensive system metrics"""
        try:
            import psutil
            
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Get network info
            network = psutil.net_io_counters()
            
            # Get temperature if available (Raspberry Pi)
            temperature = None
            try:
                with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                    temp_raw = int(f.read().strip())
                    temperature = temp_raw / 1000.0  # Convert to Celsius
            except:
                pass
            
            metrics = {
                "timestamp": datetime.utcnow().isoformat(),
                "cpu": {
                    "percent": cpu_percent,
                    "count": psutil.cpu_count()
                },
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used
                },
                "disk": {
                    "total": disk.total,
                    "free": disk.free,
                    "used": disk.used,
                    "percent": (disk.used / disk.total) * 100
                },
                "network": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv
                }
            }
            
            if temperature is not None:
                metrics["temperature"] = {
                    "celsius": temperature,
                    "fahrenheit": (temperature * 9/5) + 32
                }
            
            return metrics
            
        except ImportError:
            logger.warning("psutil not available, returning basic metrics")
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "cpu": {"percent": 0, "count": 1},
                "memory": {"total": 0, "available": 0, "percent": 0, "used": 0},
                "disk": {"total": 0, "free": 0, "used": 0, "percent": 0},
                "network": {"bytes_sent": 0, "bytes_recv": 0}
            }
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {"error": str(e), "timestamp": datetime.utcnow().isoformat()}
    
    async def get_robot_metrics(self):
        """Get robot-specific metrics"""
        try:
            # Check if ROS2 processes are running
            import subprocess
            
            result = subprocess.run(
                ["pgrep", "-f", self.config.ros2_package],
                capture_output=True,
                text=True
            )
            
            is_running = result.returncode == 0
            processes = result.stdout.strip().split('\n') if is_running else []
            
            # Get robot battery level if available (placeholder)
            battery_level = None
            try:
                # This would be robot-specific implementation
                # For now, we'll simulate or read from a file
                pass
            except:
                pass
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "ros2": {
                    "running": is_running,
                    "processes": processes,
                    "package": self.config.ros2_package
                },
                "battery": {
                    "level": battery_level,
                    "status": "unknown"
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting robot metrics: {e}")
            return {"error": str(e), "timestamp": datetime.utcnow().isoformat()}
    
    async def monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                # Get system metrics
                system_metrics = await self.get_system_metrics()
                
                # Get robot metrics
                robot_metrics = await self.get_robot_metrics()
                
                # Log interesting data
                if "cpu" in system_metrics:
                    cpu_percent = system_metrics["cpu"]["percent"]
                    memory_percent = system_metrics["memory"]["percent"]
                    
                    if cpu_percent > 80:
                        logger.warning(f"High CPU usage: {cpu_percent}%")
                    
                    if memory_percent > 80:
                        logger.warning(f"High memory usage: {memory_percent}%")
                
                # Check robot status
                if "ros2" in robot_metrics and not robot_metrics["ros2"]["running"]:
                    logger.info("Robot processes not running")
                
                # Store metrics for reporting (could send to hub periodically)
                self.last_metrics = {
                    "system": system_metrics,
                    "robot": robot_metrics
                }
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
            
            await asyncio.sleep(self.config.monitor_interval)
    
    async def start(self):
        """Start system monitoring"""
        self.running = True
        self.last_metrics = {}
        
        logger.info(f"Starting system monitoring every {self.config.monitor_interval} seconds")
        await self.monitor_loop()
    
    def stop(self):
        """Stop monitoring"""
        self.running = False
    
    def get_last_metrics(self):
        """Get the last collected metrics"""
        return getattr(self, 'last_metrics', {})
