from fastapi import APIRouter, Depends
from typing import Dict, Any, List
from datetime import datetime
import logging

from app.auth.middleware import require_robot_view

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory log storage (simple implementation)
system_logs: List[Dict[str, Any]] = []

def add_log(level: str, message: str, source: str = "system", robot_id: str = None):
    """Add a log entry"""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "level": level,
        "message": message,
        "source": source,
        "robot_id": robot_id
    }
    
    system_logs.append(log_entry)
    
    # Keep only last 1000 logs to prevent memory issues
    if len(system_logs) > 1000:
        system_logs.pop(0)
    
    logger.info(f"Log added: {log_entry}")

@router.get("/")
async def get_logs(
    user: Dict[str, Any] = Depends(require_robot_view),
    limit: int = 100,
    level: str = None,
    robot_id: str = None
):
    """Get system logs with optional filtering"""
    from app.services.robot_manager import robot_manager
    
    # Get system logs
    filtered_logs = system_logs.copy()
    
    # Filter by level if specified
    if level:
        filtered_logs = [log for log in filtered_logs if log["level"].lower() == level.lower()]
    
    # Filter by robot_id if specified
    if robot_id:
        filtered_logs = [log for log in filtered_logs if log.get("robot_id") == robot_id]
        
        # Also include robot-specific logs from robot_manager
        robot_logs = robot_manager.get_robot_logs(robot_id, limit)
        filtered_logs.extend(robot_logs)
    
    # Sort by timestamp and limit
    filtered_logs.sort(key=lambda x: x["timestamp"], reverse=True)
    filtered_logs = filtered_logs[:limit]
    
    return {
        "logs": filtered_logs,
        "total": len(filtered_logs),
        "filters": {
            "level": level,
            "robot_id": robot_id,
            "limit": limit
        }
    }

@router.get("/live")
async def get_live_logs(user: Dict[str, Any] = Depends(require_robot_view)):
    """Get recent logs for live monitoring"""
    recent_logs = system_logs[-50:] if len(system_logs) > 50 else system_logs
    
    return {
        "logs": recent_logs,
        "count": len(recent_logs),
        "last_update": datetime.utcnow().isoformat()
    }

@router.get("/stats")
async def get_log_stats(user: Dict[str, Any] = Depends(require_robot_view)):
    """Get log statistics"""
    from collections import Counter
    
    # Count logs by level
    level_counts = Counter(log["level"] for log in system_logs)
    
    # Count logs by robot
    robot_counts = Counter(log.get("robot_id", "system") for log in system_logs)
    
    # Recent activity (last hour)
    one_hour_ago = datetime.utcnow().replace(microsecond=0)
    one_hour_ago = one_hour_ago.replace(hour=one_hour_ago.hour - 1)
    recent_logs = [
        log for log in system_logs 
        if datetime.fromisoformat(log["timestamp"]) > one_hour_ago
    ]
    
    return {
        "total_logs": len(system_logs),
        "level_breakdown": dict(level_counts),
        "robot_breakdown": dict(robot_counts),
        "recent_activity": {
            "last_hour": len(recent_logs),
            "levels": dict(Counter(log["level"] for log in recent_logs))
        },
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Sort by timestamp (newest first) and limit
    filtered_logs.sort(key=lambda x: x["timestamp"], reverse=True)
    filtered_logs = filtered_logs[:limit]
    
    return {
        "logs": filtered_logs,
        "total": len(filtered_logs),
        "filters": {
            "level": level,
            "robot_id": robot_id,
            "limit": limit
        }
    }

@router.get("/recent")
async def get_recent_logs(user: Dict[str, Any] = Depends(require_robot_view)):
    """Get most recent 50 logs"""
    recent_logs = system_logs[-50:] if len(system_logs) >= 50 else system_logs
    recent_logs.reverse()  # Newest first
    
    return {
        "logs": recent_logs,
        "total": len(recent_logs)
    }

@router.post("/clear")
async def clear_logs(user: Dict[str, Any] = Depends(require_robot_view)):
    """Clear all logs (if user has permission)"""
    global system_logs
    system_logs.clear()
    
    add_log("info", f"Logs cleared by {user.get('access_level')} user", "system")
    
    return {
        "message": "Logs cleared successfully",
        "timestamp": datetime.utcnow().isoformat()
    }

# Add some initial logs
add_log("info", "Artbot Control Hub started", "system")
add_log("info", "WebSocket manager initialized", "system")
