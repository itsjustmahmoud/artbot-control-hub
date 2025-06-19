from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class LoggingService:
    """Manages robot logs and system logging"""
    
    def __init__(self):
        self.robot_logs: Dict[str, List[dict]] = {}
        self.system_logs: List[dict] = []
        
    def add_robot_log(self, robot_id: str, log_entry: dict):
        """Add a log entry for a specific robot"""
        if robot_id not in self.robot_logs:
            self.robot_logs[robot_id] = []
            
        # Ensure required fields
        log_data = {
            "timestamp": log_entry.get("timestamp", datetime.utcnow().isoformat()),
            "level": log_entry.get("level", "INFO"),
            "message": log_entry.get("message", ""),
            "source": log_entry.get("source", "system"),
            "robot_id": robot_id
        }
        
        # Add additional fields if present
        for field in ["details", "error_code", "stack_trace"]:
            if field in log_entry:
                log_data[field] = log_entry[field]
                
        self.robot_logs[robot_id].append(log_data)
        
        # Keep only last 1000 logs per robot to prevent memory issues
        if len(self.robot_logs[robot_id]) > 1000:
            self.robot_logs[robot_id] = self.robot_logs[robot_id][-1000:]
            
        logger.debug(f"Log added for robot {robot_id}: {log_data['level']} - {log_data['message']}")
        
    def add_system_log(self, log_entry: dict):
        """Add a system-wide log entry"""
        log_data = {
            "timestamp": log_entry.get("timestamp", datetime.utcnow().isoformat()),
            "level": log_entry.get("level", "INFO"),
            "message": log_entry.get("message", ""),
            "source": log_entry.get("source", "system"),
            "component": log_entry.get("component", "core")
        }
        
        # Add additional fields if present
        for field in ["details", "error_code", "user_id", "robot_id"]:
            if field in log_entry:
                log_data[field] = log_entry[field]
                
        self.system_logs.append(log_data)
        
        # Keep only last 5000 system logs
        if len(self.system_logs) > 5000:
            self.system_logs = self.system_logs[-5000:]
            
        logger.debug(f"System log added: {log_data['level']} - {log_data['message']}")
        
    def get_robot_logs(self, robot_id: str, limit: int = 100, level: str = None) -> List[dict]:
        """Get logs for a specific robot"""
        logs = self.robot_logs.get(robot_id, [])
        
        # Filter by level if specified
        if level:
            logs = [log for log in logs if log["level"] == level.upper()]
            
        # Sort by timestamp (newest first) and limit
        sorted_logs = sorted(logs, key=lambda x: x["timestamp"], reverse=True)
        return sorted_logs[:limit]
        
    def get_system_logs(self, limit: int = 100, level: str = None, component: str = None) -> List[dict]:
        """Get system logs with optional filtering"""
        logs = self.system_logs.copy()
        
        # Filter by level if specified
        if level:
            logs = [log for log in logs if log["level"] == level.upper()]
            
        # Filter by component if specified
        if component:
            logs = [log for log in logs if log.get("component") == component]
            
        # Sort by timestamp (newest first) and limit
        sorted_logs = sorted(logs, key=lambda x: x["timestamp"], reverse=True)
        return sorted_logs[:limit]
        
    def get_all_logs(self, limit: int = 100, level: str = None) -> List[dict]:
        """Get all logs (robot + system) merged and sorted"""
        all_logs = self.system_logs.copy()
        
        # Add all robot logs
        for robot_logs in self.robot_logs.values():
            all_logs.extend(robot_logs)
            
        # Filter by level if specified
        if level:
            all_logs = [log for log in all_logs if log["level"] == level.upper()]
            
        # Sort by timestamp (newest first) and limit
        sorted_logs = sorted(all_logs, key=lambda x: x["timestamp"], reverse=True)
        return sorted_logs[:limit]
        
    def get_log_statistics(self, robot_id: str = None) -> dict:
        """Get logging statistics"""
        if robot_id:
            logs = self.robot_logs.get(robot_id, [])
        else:
            logs = []
            for robot_logs in self.robot_logs.values():
                logs.extend(robot_logs)
            logs.extend(self.system_logs)
            
        level_counts = {}
        for log in logs:
            level = log["level"]
            level_counts[level] = level_counts.get(level, 0) + 1
            
        return {
            "total_logs": len(logs),
            "level_breakdown": level_counts,
            "robots_with_logs": len(self.robot_logs),
            "system_logs": len(self.system_logs)
        }
        
    def clear_robot_logs(self, robot_id: str) -> bool:
        """Clear logs for a specific robot"""
        if robot_id in self.robot_logs:
            self.robot_logs[robot_id] = []
            logger.info(f"Cleared logs for robot {robot_id}")
            return True
        return False
        
    def clear_system_logs(self):
        """Clear all system logs"""
        self.system_logs = []
        logger.info("Cleared all system logs")
        
    def clear_all_logs(self):
        """Clear all logs (robot + system)"""
        self.robot_logs = {}
        self.system_logs = []
        logger.info("Cleared all logs")
