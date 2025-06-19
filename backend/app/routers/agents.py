from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Dict, Any, List
from datetime import datetime
import logging

from app.auth.middleware import require_admin
from app.services.robot_manager import robot_manager

logger = logging.getLogger(__name__)

router = APIRouter()

class AgentRegistration(BaseModel):
    agent_id: str
    hostname: str
    ip_address: str
    system_info: Dict[str, Any]
    robot_info: Dict[str, Any] = {}

@router.post("/register")
async def register_agent(agent_data: AgentRegistration):
    """Register a new agent (called by Pi agents)"""
    try:
        # Register the agent
        robot_manager.register_agent(
            agent_data.agent_id,
            {
                "hostname": agent_data.hostname,
                "ip_address": agent_data.ip_address,
                "system_info": agent_data.system_info,
                "robot_info": agent_data.robot_info
            }
        )
        
        logger.info(f"Agent {agent_data.agent_id} registered successfully")
        
        return {
            "message": f"Agent {agent_data.agent_id} registered successfully",
            "agent_id": agent_data.agent_id,
            "status": "registered"
        }
    
    except Exception as e:
        logger.error(f"Failed to register agent {agent_data.agent_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register agent: {str(e)}"
        )

@router.post("/{agent_id}/heartbeat")
async def agent_heartbeat(agent_id: str, data: Dict[str, Any] = {}):
    """Update agent heartbeat and status"""
    try:
        logger.debug(f"Received heartbeat from {agent_id}: {data}")
        robot_manager.update_agent_heartbeat(agent_id, data)
        
        return {
            "message": "Heartbeat received",
            "agent_id": agent_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Heartbeat error for agent {agent_id}: {e}")
        logger.error(f"Heartbeat data: {data}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Heartbeat processing failed: {str(e)}"
        )

@router.get("/")
async def get_all_agents(user: Dict[str, Any] = Depends(require_admin)):
    """Get all agents (admin only)"""
    agents = robot_manager.get_all_agents()
    
    return {
        "agents": list(agents.values()),
        "total": len(agents),
        "online": len([a for a in agents.values() if a.get("status") == "online"])
    }

@router.get("/{agent_id}")
async def get_agent(agent_id: str, user: Dict[str, Any] = Depends(require_admin)):
    """Get specific agent information (admin only)"""
    agent = robot_manager.get_agent(agent_id)
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )
    
    return agent

@router.delete("/{agent_id}")
async def remove_agent(agent_id: str, user: Dict[str, Any] = Depends(require_admin)):
    """Remove agent from system (admin only)"""
    agent = robot_manager.get_agent(agent_id)
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )
    
    robot_manager.remove_agent(agent_id)
    
    logger.info(f"Agent {agent_id} removed by admin")
    
    return {
        "message": f"Agent {agent_id} removed successfully",
        "agent_id": agent_id
    }

@router.get("/stats/connections")
async def get_connection_stats(user: Dict[str, Any] = Depends(require_admin)):
    """Get WebSocket connection statistics (admin only)"""
    from app.main import manager
    
    return {
        "connections": manager.get_connection_stats(),
        "connected_agents": manager.get_connected_agents(),
        "timestamp": datetime.utcnow().isoformat()
    }
