from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Dict, Any, List
from datetime import datetime
import logging

from app.auth.middleware import require_robot_view, require_robot_control, require_exhibition_control
from app.services.robot_manager import robot_manager

logger = logging.getLogger(__name__)

router = APIRouter()

class RobotCommand(BaseModel):
    action: str  # start, stop, restart, reboot
    parameters: Dict[str, Any] = {}

class ExhibitionCommand(BaseModel):
    action: str  # start_all, stop_all

@router.get("/")
async def get_all_robots(user: Dict[str, Any] = Depends(require_robot_view)):
    """Get all robots with their current status"""
    robots = robot_manager.get_all_robots()
    return {
        "robots": list(robots.values()),
        "total": len(robots),
        "online": len(robot_manager.get_online_robots())
    }

@router.get("/{robot_id}")
async def get_robot(robot_id: str, user: Dict[str, Any] = Depends(require_robot_view)):
    """Get specific robot information"""
    robot = robot_manager.get_robot(robot_id)
    
    if not robot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Robot {robot_id} not found"
        )
    
    return robot

@router.post("/{robot_id}/command")
async def send_robot_command(
    robot_id: str, 
    command: RobotCommand, 
    user: Dict[str, Any] = Depends(require_robot_control)
):
    """Send command to specific robot"""
    robot = robot_manager.get_robot(robot_id)
    
    if not robot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Robot {robot_id} not found"
        )
    
    if robot.get('status') != 'online':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Robot {robot_id} is not online"
        )
    
    try:
        # Send command through WebSocket or agent communication
        result = await robot_manager.send_command_to_robot(robot_id, command.action, command.parameters)
        
        logger.info(f"Command {command.action} sent to robot {robot_id} by {user['role']}")
        
        return {
            "success": True,
            "message": f"Command {command.action} sent to robot {robot_id}",
            "command_id": result.get("command_id"),
            "robot_id": robot_id
        }
        
    except Exception as e:
        logger.error(f"Failed to send command to robot {robot_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send command: {str(e)}"
        )

@router.get("/{robot_id}/logs")
async def get_robot_logs(
    robot_id: str, 
    limit: int = 100,
    user: Dict[str, Any] = Depends(require_robot_view)
):
    """Get logs for specific robot"""
    robot = robot_manager.get_robot(robot_id)
    
    if not robot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Robot {robot_id} not found"
        )
    
    # Get logs from robot manager
    logs = robot_manager.get_robot_logs(robot_id, limit)
    
    return {
        "robot_id": robot_id,
        "logs": logs,
        "total": len(logs)
    }

@router.post("/exhibition/command")
async def exhibition_command(
    command: ExhibitionCommand,
    user: Dict[str, Any] = Depends(require_exhibition_control)
):
    """Control entire exhibition (start/stop all robots)"""
    robots = robot_manager.get_all_robots()
    results = []
    
    for robot_id, robot in robots.items():
        if robot.get('status') != 'online':
            continue
            
        try:
            if command.action == "start_all":
                action = "start"
            elif command.action == "stop_all":
                action = "stop"
            else:
                continue
                
            # Send command to robot
            result = await robot_manager.send_command_to_robot(robot_id, action, {})
            
            results.append({
                "robot_id": robot_id,
                "success": True,
                "action": action,
                "command_id": result.get("command_id")
            })
            
        except Exception as e:
            results.append({
                "robot_id": robot_id,
                "success": False,
                "error": str(e),
                "action": action if 'action' in locals() else "unknown"
            })
    
    logger.info(f"Exhibition command {command.action} executed by {user['role']}")
    
    return {
        "message": f"Exhibition command {command.action} executed",
        "results": results,
        "total_robots": len(robots),
        "processed": len(results)
    }

@router.get("/{robot_id}/health")
async def get_robot_health(robot_id: str, user: Dict[str, Any] = Depends(require_robot_view)):
    """Get robot health information"""
    robot = robot_manager.get_robot(robot_id)
    
    if not robot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Robot {robot_id} not found"
        )
    
    health_info = robot_manager.get_robot_health(robot_id)
    
    return {
        "robot_id": robot_id,
        "health": health_info,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/exhibition/status")
async def get_exhibition_status(user: Dict[str, Any] = Depends(require_robot_view)):
    """Get overall exhibition status"""
    return robot_manager.get_exhibition_status()
