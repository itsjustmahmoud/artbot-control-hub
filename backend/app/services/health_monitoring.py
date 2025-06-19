from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class HealthMonitoringService:
    """Monitors robot and system health"""
    
    def __init__(self):
        self.health_checks: Dict[str, dict] = {}
        
    def update_robot_health(self, robot_id: str, health_data: dict):
        """Update health metrics for a robot"""
        timestamp = datetime.utcnow()
        
        health_entry = {
            "robot_id": robot_id,
            "timestamp": timestamp.isoformat(),
            "battery_level": health_data.get("battery_level", 0),
            "cpu_usage": health_data.get("cpu_usage", 0),
            "memory_usage": health_data.get("memory_usage", 0),
            "temperature": health_data.get("temperature", 0),
            "disk_usage": health_data.get("disk_usage", 0),
            "network_latency": health_data.get("network_latency", 0),
            "errors_count": health_data.get("errors_count", 0),
            "uptime": health_data.get("uptime", 0)
        }
        
        # Calculate health score
        health_entry["health_score"] = self._calculate_health_score(health_entry)
        health_entry["status"] = self._determine_health_status(health_entry)
        
        self.health_checks[robot_id] = health_entry
        logger.debug(f"Health updated for robot {robot_id}: {health_entry['status']}")
        
    def get_robot_health(self, robot_id: str) -> Optional[dict]:
        """Get current health status for a robot"""
        health = self.health_checks.get(robot_id)
        if not health:
            return None
            
        # Check if health data is stale (older than 5 minutes)
        timestamp = datetime.fromisoformat(health["timestamp"])
        if datetime.utcnow() - timestamp > timedelta(minutes=5):
            health["status"] = "stale"
            health["health_score"] = 0
            
        return health
        
    def get_all_health_status(self) -> Dict[str, dict]:
        """Get health status for all robots"""
        return {robot_id: self.get_robot_health(robot_id) 
                for robot_id in self.health_checks.keys()}
        
    def get_unhealthy_robots(self, threshold: float = 70.0) -> List[dict]:
        """Get robots with health score below threshold"""
        unhealthy = []
        for robot_id, health in self.health_checks.items():
            current_health = self.get_robot_health(robot_id)
            if current_health and current_health["health_score"] < threshold:
                unhealthy.append(current_health)
        return unhealthy
        
    def get_critical_alerts(self) -> List[dict]:
        """Get critical health alerts"""
        alerts = []
        current_time = datetime.utcnow()
        
        for robot_id, health in self.health_checks.items():
            current_health = self.get_robot_health(robot_id)
            if not current_health:
                continue
                
            # Critical battery level
            if current_health["battery_level"] < 15:
                alerts.append({
                    "robot_id": robot_id,
                    "type": "critical_battery",
                    "message": f"Robot {robot_id} battery critically low: {current_health['battery_level']}%",
                    "timestamp": current_time.isoformat(),
                    "severity": "critical"
                })
                
            # High temperature
            if current_health["temperature"] > 70:
                alerts.append({
                    "robot_id": robot_id,
                    "type": "high_temperature",
                    "message": f"Robot {robot_id} temperature high: {current_health['temperature']}°C",
                    "timestamp": current_time.isoformat(),
                    "severity": "warning"
                })
                
            # High CPU usage
            if current_health["cpu_usage"] > 90:
                alerts.append({
                    "robot_id": robot_id,
                    "type": "high_cpu",
                    "message": f"Robot {robot_id} CPU usage high: {current_health['cpu_usage']}%",
                    "timestamp": current_time.isoformat(),
                    "severity": "warning"
                })
                
            # Stale health data
            if current_health["status"] == "stale":
                alerts.append({
                    "robot_id": robot_id,
                    "type": "stale_data",
                    "message": f"Robot {robot_id} health data is stale",
                    "timestamp": current_time.isoformat(),
                    "severity": "warning"
                })
                
        return alerts
        
    def _calculate_health_score(self, health_data: dict) -> float:
        """Calculate overall health score (0-100)"""
        scores = []
        
        # Battery score (critical component)
        battery = health_data["battery_level"]
        if battery > 50:
            battery_score = 100
        elif battery > 20:
            battery_score = 50 + (battery - 20) * (50 / 30)
        else:
            battery_score = battery * (50 / 20)
        scores.append(battery_score * 0.3)  # 30% weight
        
        # CPU score
        cpu = health_data["cpu_usage"]
        cpu_score = max(0, 100 - cpu)
        scores.append(cpu_score * 0.2)  # 20% weight
        
        # Memory score
        memory = health_data["memory_usage"]
        memory_score = max(0, 100 - memory)
        scores.append(memory_score * 0.2)  # 20% weight
        
        # Temperature score
        temp = health_data["temperature"]
        if temp < 50:
            temp_score = 100
        elif temp < 70:
            temp_score = 100 - (temp - 50) * 2
        else:
            temp_score = max(0, 60 - (temp - 70) * 3)
        scores.append(temp_score * 0.15)  # 15% weight
        
        # Network latency score
        latency = health_data["network_latency"]
        if latency < 50:
            latency_score = 100
        elif latency < 200:
            latency_score = 100 - (latency - 50) * 0.5
        else:
            latency_score = max(0, 25 - (latency - 200) * 0.1)
        scores.append(latency_score * 0.15)  # 15% weight
        
        return sum(scores)
        
    def _determine_health_status(self, health_data: dict) -> str:
        """Determine health status based on health score"""
        score = health_data["health_score"]
        
        if score >= 80:
            return "healthy"
        elif score >= 60:
            return "good"
        elif score >= 40:
            return "warning"
        elif score >= 20:
            return "poor"
        else:
            return "critical"
            
    def get_system_health_overview(self) -> dict:
        """Get overall system health overview"""
        all_health = list(self.health_checks.values())
        
        if not all_health:
            return {
                "status": "unknown",
                "total_robots": 0,
                "healthy_robots": 0,
                "warning_robots": 0,
                "critical_robots": 0,
                "average_health_score": 0
            }
            
        healthy = len([h for h in all_health if self._determine_health_status(h) in ["healthy", "good"]])
        warning = len([h for h in all_health if self._determine_health_status(h) == "warning"])
        critical = len([h for h in all_health if self._determine_health_status(h) in ["poor", "critical"]])
        
        avg_score = sum(h["health_score"] for h in all_health) / len(all_health)
        
        # Determine overall system status
        if critical > 0:
            system_status = "critical"
        elif warning > len(all_health) * 0.3:  # More than 30% in warning
            system_status = "warning"
        elif healthy > len(all_health) * 0.8:  # More than 80% healthy
            system_status = "healthy"
        else:
            system_status = "degraded"
            
        return {
            "status": system_status,
            "total_robots": len(all_health),
            "healthy_robots": healthy,
            "warning_robots": warning,
            "critical_robots": critical,
            "average_health_score": round(avg_score, 1),
            "last_updated": datetime.utcnow().isoformat()
        }
