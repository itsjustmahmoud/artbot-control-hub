from fastapi import APIRouter, Depends
from typing import Dict, Any
import psutil
import platform
from datetime import datetime

from app.auth.middleware import require_robot_view

router = APIRouter()

@router.get("/health")
async def system_health(user: Dict[str, Any] = Depends(require_robot_view)):
    """Get overall system health"""
    try:
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "system": {
                "cpu_percent": cpu_percent,
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent
                },
                "disk": {
                    "total": disk.total,
                    "free": disk.free,
                    "percent": (disk.used / disk.total) * 100
                },
                "platform": platform.platform(),
                "python_version": platform.python_version()
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/status")
async def system_status(user: Dict[str, Any] = Depends(require_robot_view)):
    """Get system status summary"""
    from app.services.robot_manager import robot_manager
    
    exhibition_status = robot_manager.get_exhibition_status()
    
    return {
        "hub_status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "exhibition": exhibition_status,
        "agents": {
            "total": len(robot_manager.get_all_agents()),
            "online": len([a for a in robot_manager.get_all_agents().values() if a.get("status") == "online"])
        }
    }

@router.get("/info")
async def system_info(user: Dict[str, Any] = Depends(require_robot_view)):
    """Get detailed system information"""
    from app.services.robot_manager import robot_manager
    from app.config import settings
    
    # Network interfaces
    network_info = []
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == 2:  # IPv4
                network_info.append({
                    "interface": interface,
                    "ip": addr.address,
                    "netmask": addr.netmask
                })
    
    return {
        "version": "1.0.0",
        "build_date": "2025-06-19",
        "system": {
            "platform": platform.platform(),
            "architecture": platform.architecture(),
            "processor": platform.processor(),
            "hostname": platform.node(),
            "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
            "uptime_seconds": (datetime.now() - datetime.fromtimestamp(psutil.boot_time())).total_seconds()
        },
        "network": network_info,
        "environment": {
            "debug": settings.DEBUG,
            "websocket_host": settings.WEBSOCKET_HOST,
            "websocket_port": settings.WEBSOCKET_PORT
        },
        "statistics": {
            "total_robots": len(robot_manager.get_all_robots()),
            "total_agents": len(robot_manager.get_all_agents()),
            "system_uptime": datetime.utcnow().isoformat()
        }
    }

@router.get("/logs/summary")
async def system_log_summary(user: Dict[str, Any] = Depends(require_robot_view)):
    """Get system log summary"""
    from app.routers.logs import system_logs
    from collections import Counter
    
    # Recent logs (last 24 hours)
    twenty_four_hours_ago = datetime.utcnow().replace(hour=datetime.utcnow().hour - 24)
    recent_logs = [
        log for log in system_logs 
        if datetime.fromisoformat(log["timestamp"]) > twenty_four_hours_ago
    ]
    
    return {
        "total_logs": len(system_logs),
        "recent_logs_24h": len(recent_logs),
        "log_levels": dict(Counter(log["level"] for log in system_logs)),
        "recent_log_levels": dict(Counter(log["level"] for log in recent_logs)),
        "last_log_time": system_logs[-1]["timestamp"] if system_logs else None,
        "timestamp": datetime.utcnow().isoformat()
    }
