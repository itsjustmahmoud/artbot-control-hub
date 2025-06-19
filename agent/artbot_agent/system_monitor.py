import asyncio
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class SystemMonitor:
    """Monitors system metrics and robot status"""
    
    def __init__(self, config):
        self.config = config
        self.running = False
        self.start_time = datetime.utcnow()
        self.last_metrics = {}
    
    async def get_essential_metrics(self):
        """Get only the essential metrics requested by user"""
        try:
            import psutil
            import subprocess
            
            # 1. CPU usage and temperature
            cpu_percent = psutil.cpu_percent(interval=1)
            
            temperature = None
            try:
                with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                    temp_raw = int(f.read().strip())
                    temperature = temp_raw / 1000.0  # Convert to Celsius
            except:
                temperature = 40  # Default fallback
            
            # 2. Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # 3. OAK camera connectivity check
            oak_connected = False
            try:
                # Check if camera device exists or depthai processes
                oak_connected = (
                    os.path.exists('/dev/video0') or 
                    os.path.exists('/dev/dri/card0') or
                    len(subprocess.run(["pgrep", "-f", "depthai"], capture_output=True).stdout) > 0
                )
            except:
                pass
            
            # 4. Create3 connectivity and battery
            create3_connected = False
            battery_level = 0
            try:
                # Try to ping Create3 IP
                create3_ip = os.getenv("CREATE3_IP", "192.168.186.2")
                result = subprocess.run(
                    ["ping", "-c", "1", "-W", "1", create3_ip],
                    capture_output=True,
                    timeout=2
                )
                create3_connected = result.returncode == 0
                
                # Get battery level if connected
                if create3_connected:
                    try:
                        import requests
                        response = requests.get(f'http://{create3_ip}/api/battery', timeout=2)
                        if response.status_code == 200:
                            battery_data = response.json()
                            battery_level = battery_data.get('level', 0)
                    except:
                        battery_level = 85  # Default fallback
            except:
                pass
            
            # 5. Workspace run status
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
            
            # 6. Robot uptime (time since agent started)
            uptime_seconds = (datetime.utcnow() - self.start_time).total_seconds()
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "cpu_percent": round(cpu_percent, 1),
                "temperature": round(temperature, 1),
                "memory_percent": round(memory_percent, 1),
                "oak_connected": oak_connected,
                "create3_connected": create3_connected,
                "battery_level": battery_level,
                "workspace_running": workspace_running,
                "uptime": int(uptime_seconds)
            }
            
        except Exception as e:
            logger.error(f"Error getting essential metrics: {e}")
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "cpu_percent": 0,
                "temperature": 40,
                "memory_percent": 0,
                "oak_connected": False,
                "create3_connected": False,
                "battery_level": 0,
                "workspace_running": False,
                "uptime": 0,
                "error": str(e)
            }

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
            
            # Get robot battery level if available
            battery_level = None
            try:
                # First check if Create3 is connected
                create3_ip = os.getenv("CREATE3_IP", "192.168.186.2")
                ping_result = subprocess.run(
                    ["ping", "-c", "1", "-W", "1", create3_ip],
                    capture_output=True,
                    timeout=2
                )
                create3_connected = ping_result.returncode == 0
                
                # Try to get battery level from Create3 API if connected
                if create3_connected:
                    import requests
                    response = requests.get(f'http://{create3_ip}/api/battery', timeout=2)
                    if response.status_code == 200:
                        battery_data = response.json()
                        battery_level = battery_data.get('level', None)
            except:
                pass
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "ros2": {
                    "package": self.config.ros2_package,
                    "running": is_running,
                    "processes": len(processes),
                    "process_ids": processes
                },
                "battery": {
                    "level": battery_level
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting robot metrics: {e}")
            return {"error": str(e), "timestamp": datetime.utcnow().isoformat()}

    async def collect_metrics(self):
        """Collect all metrics"""
        try:
            system_metrics = await self.get_system_metrics()
            robot_metrics = await self.get_robot_metrics()
            essential_metrics = await self.get_essential_metrics()
            
            combined_metrics = {
                "timestamp": datetime.utcnow().isoformat(),
                "agent_id": self.config.agent_id,
                "hostname": self.config.hostname,
                "system": system_metrics,
                "robot": robot_metrics,
                "essential": essential_metrics
            }
            
            self.last_metrics = combined_metrics
            return combined_metrics
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            return {"error": str(e), "timestamp": datetime.utcnow().isoformat()}

    async def monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                metrics = await self.collect_metrics()
                logger.debug(f"Collected metrics: {metrics}")
                
                # Wait for next collection interval
                await asyncio.sleep(self.config.monitor_interval)
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(self.config.monitor_interval)

    async def start(self):
        """Start monitoring loop"""
        self.running = True
        logger.info(f"Starting system monitoring every {self.config.monitor_interval} seconds")
        
        while self.running:
            try:
                # Collect essential metrics and store them
                self.last_metrics = await self.get_essential_metrics()
                
                # Wait for next collection interval
                await asyncio.sleep(self.config.monitor_interval)
                
            except Exception as e:
                logger.error(f"System monitoring error: {e}")
                await asyncio.sleep(self.config.monitor_interval)
        
        logger.info("System monitoring stopped")
    
    def stop(self):
        """Stop monitoring"""
        self.running = False
    
    def get_last_metrics(self):
        """Get the last collected metrics"""
        return getattr(self, 'last_metrics', {})
