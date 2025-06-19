from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class AgentRegistryService:
    """Manages agent registration and status tracking"""
    
    def __init__(self):
        self.agents: Dict[str, dict] = {}
        
    def register_agent(self, agent_id: str, agent_info: dict):
        """Register a new agent"""
        agent_data = {
            "agent_id": agent_id,
            "hostname": agent_info.get("hostname", f"unknown-{agent_id}"),
            "ip_address": agent_info.get("ip_address", "unknown"),
            "port": agent_info.get("port", 8080),
            "status": "online",
            "last_seen": datetime.utcnow(),
            "registered_at": datetime.utcnow(),
            "system_info": agent_info.get("system_info", {}),
            "capabilities": agent_info.get("capabilities", []),
            "version": agent_info.get("version", "unknown")
        }
        
        self.agents[agent_id] = agent_data
        logger.info(f"Agent {agent_id} registered from {agent_data['ip_address']}")
        return agent_data
        
    def update_agent_heartbeat(self, agent_id: str, data: dict = None):
        """Update agent heartbeat and optional data"""
        if agent_id not in self.agents:
            logger.warning(f"Heartbeat from unknown agent {agent_id}")
            return False
            
        agent = self.agents[agent_id]
        agent["last_seen"] = datetime.utcnow()
        agent["status"] = "online"
        
        if data:
            # Update system metrics if provided
            if "system_metrics" in data:
                agent["system_metrics"] = data["system_metrics"]
            if "robot_status" in data:
                agent["robot_status"] = data["robot_status"]
                
        logger.debug(f"Agent {agent_id} heartbeat updated")
        return True
        
    def get_agent(self, agent_id: str) -> Optional[dict]:
        """Get specific agent information"""
        return self.agents.get(agent_id)
        
    def get_all_agents(self) -> Dict[str, dict]:
        """Get all registered agents"""
        return self.agents.copy()
        
    def get_online_agents(self) -> List[dict]:
        """Get agents that are currently online (heartbeat within 2 minutes)"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=2)
        online_agents = []
        
        for agent in self.agents.values():
            if agent["last_seen"] > cutoff_time:
                online_agents.append(agent)
            else:
                # Mark as offline if heartbeat is stale
                agent["status"] = "offline"
                
        return online_agents
        
    def remove_agent(self, agent_id: str):
        """Remove agent from registry"""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            del self.agents[agent_id]
            logger.info(f"Agent {agent_id} removed from registry (was at {agent.get('ip_address', 'unknown')})")
            return True
        return False
        
    def set_agent_offline(self, agent_id: str):
        """Mark agent as offline"""
        if agent_id in self.agents:
            self.agents[agent_id]["status"] = "offline"
            logger.info(f"Agent {agent_id} marked as offline")
            return True
        return False
        
    def get_agent_statistics(self) -> dict:
        """Get statistics about registered agents"""
        total_agents = len(self.agents)
        online_agents = len(self.get_online_agents())
        
        return {
            "total_agents": total_agents,
            "online_agents": online_agents,
            "offline_agents": total_agents - online_agents,
            "last_updated": datetime.utcnow().isoformat()
        }
