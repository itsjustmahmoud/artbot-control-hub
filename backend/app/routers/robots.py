from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Dict, Any, List
from datetime import datetime
import logging

from app.auth.middleware import require_robot_view, require_robot_control, require_exhibition_control, require_admin, require_admin
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

@router.post("/{robot_id}/workspace/start")
async def start_robot_workspace(
    robot_id: str, 
    user: Dict[str, Any] = Depends(require_robot_control)
):
    """Start workspace on robot (Museum Staff & Admin)"""
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
        result = await robot_manager.send_command_to_robot(robot_id, "start_workspace", {})
        
        logger.info(f"Workspace start command sent to robot {robot_id} by {user['role']}")
        
        return {
            "success": True,
            "message": f"Workspace started on robot {robot_id}",
            "command_id": result.get("command_id"),
            "robot_id": robot_id
        }
        
    except Exception as e:
        logger.error(f"Failed to start workspace on robot {robot_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start workspace: {str(e)}"
        )

@router.post("/{robot_id}/workspace/stop")
async def stop_robot_workspace(
    robot_id: str, 
    user: Dict[str, Any] = Depends(require_robot_control)
):
    """Stop workspace on robot (Museum Staff & Admin)"""
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
        result = await robot_manager.send_command_to_robot(robot_id, "stop_workspace", {})
        
        logger.info(f"Workspace stop command sent to robot {robot_id} by {user['role']}")
        
        return {
            "success": True,
            "message": f"Workspace stopped on robot {robot_id}",
            "command_id": result.get("command_id"),
            "robot_id": robot_id
        }
        
    except Exception as e:
        logger.error(f"Failed to stop workspace on robot {robot_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop workspace: {str(e)}"
        )

@router.post("/{robot_id}/create3/restart")
async def restart_robot_create3(
    robot_id: str, 
    user: Dict[str, Any] = Depends(require_admin)
):
    """Restart Create3 robot (Admin only)"""
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
        result = await robot_manager.send_command_to_robot(robot_id, "restart_create3", {})
        
        logger.info(f"Create3 restart command sent to robot {robot_id} by {user['role']}")
        
        return {
            "success": True,
            "message": f"Create3 restart command sent to robot {robot_id}",
            "command_id": result.get("command_id"),
            "robot_id": robot_id
        }
        
    except Exception as e:
        logger.error(f"Failed to restart Create3 on robot {robot_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to restart Create3: {str(e)}"
        )

@router.post("/{robot_id}/create3/reboot")
async def reboot_robot_create3(
    robot_id: str, 
    user: Dict[str, Any] = Depends(require_admin)
):
    """Reboot Create3 robot (Admin only)"""
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
        result = await robot_manager.send_command_to_robot(robot_id, "reboot_create3", {})
        
        logger.info(f"Create3 reboot command sent to robot {robot_id} by {user['role']}")
        
        return {
            "success": True,
            "message": f"Create3 reboot command sent to robot {robot_id}",
            "command_id": result.get("command_id"),
            "robot_id": robot_id
        }
        
    except Exception as e:
        logger.error(f"Failed to reboot Create3 on robot {robot_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reboot Create3: {str(e)}"
        )

@router.get("/{robot_id}/workspace/logs")
async def get_robot_workspace_logs(
    robot_id: str, 
    user: Dict[str, Any] = Depends(require_admin)
):
    """Get workspace logs for specific robot (Admin only)"""
    robot = robot_manager.get_robot(robot_id)
    
    if not robot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Robot {robot_id} not found"
        )
    
    try:
        result = await robot_manager.send_command_to_robot(robot_id, "get_logs", {})
        
        return {
            "success": True,
            "robot_id": robot_id,
            "logs": result.get("logs", []),
            "timestamp": result.get("timestamp")
        }
        
    except Exception as e:
        logger.error(f"Failed to get workspace logs for robot {robot_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workspace logs: {str(e)}"
        )

@router.get("/{robot_id}/metrics")
async def get_robot_metrics(robot_id: str, user: Dict[str, Any] = Depends(require_robot_view)):
    """Get detailed robot metrics for core data points validation"""
    robot = robot_manager.get_robot(robot_id)
    agent = robot_manager.get_agent(robot_id)
    
    if not robot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Robot {robot_id} not found"
        )
    
    # Core metrics as specified by user requirements
    core_metrics = {
        # Robot Identity
        "robot_id": robot.get("id"),
        "agent_id": robot.get("agent_id"),
        "robot_name": robot.get("name"),
        "pi_hostname": robot.get("hostname"),
        
        # System Metrics (from Raspberry Pi)
        "cpu_usage": robot.get("cpu_usage"),
        "temperature": robot.get("temperature"), 
        "memory_usage": robot.get("memory_usage"),        # Connectivity Status
        "oak_camera_connected": robot.get("oak_connected"),
        "create3_connected": robot.get("create3_connected"),
        "create3_status": robot.get("create3_status"),
          # Robot Status & Metrics
        "battery_level": robot.get("battery_level"),
        "is_charging": robot.get("is_charging"),
        "is_docked": robot.get("is_docked"),
        "workspace_running": robot.get("workspace_running"),
        "current_action": robot.get("current_action"),
        "uptime": robot.get("uptime"),
        
        # Network & Connection Info
        "ip_address": robot.get("ip_address"),
        "last_update": robot.get("last_update"),
        "status": robot.get("status")
    }
    
    # Agent data for additional context
    agent_data = None
    if agent:
        agent_data = {
            "hostname": agent.get("hostname"),
            "last_seen": agent.get("last_seen"),
            "system_info": agent.get("system_info")
        }
    
    return {
        "robot_id": robot_id,
        "core_metrics": core_metrics,
        "agent_data": agent_data,
        "timestamp": datetime.utcnow().isoformat()
    }
