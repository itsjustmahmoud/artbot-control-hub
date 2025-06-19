"""
Domain models for robots and agents.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class RobotStatus(str, Enum):
    """Robot status enumeration."""
    ONLINE = "online"
    OFFLINE = "offline"
    ACTIVE = "active"
    IDLE = "idle"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class RobotAction(str, Enum):
    """Robot action enumeration."""
    IDLE = "idle"
    PERSON_FOLLOWING = "person_following"
    NAVIGATION = "navigation"
    CHARGING = "charging"
    SYSTEM_RESTART = "system_restart"
    STOPPED = "stopped"


class SystemInfo(BaseModel):
    """System information model."""
    cpu_usage: float = Field(..., ge=0, le=100, description="CPU usage percentage")
    memory_usage: float = Field(..., ge=0, le=100, description="Memory usage percentage")
    temperature: float = Field(..., description="System temperature in Celsius")
    disk_usage: Optional[float] = Field(None, ge=0, le=100, description="Disk usage percentage")
    uptime: Optional[int] = Field(None, description="System uptime in seconds")


class RobotHealth(BaseModel):
    """Robot health metrics."""
    battery_level: int = Field(..., ge=0, le=100, description="Battery percentage")
    system_info: SystemInfo
    last_heartbeat: datetime = Field(..., description="Last heartbeat timestamp")
    network_latency: Optional[float] = Field(None, description="Network latency in ms")
    connection_quality: Optional[str] = Field(None, description="Connection quality rating")


class Robot(BaseModel):
    """Robot domain model."""
    id: str = Field(..., description="Unique robot identifier")
    name: str = Field(..., description="Human-readable robot name")
    status: RobotStatus = Field(default=RobotStatus.OFFLINE, description="Current robot status")
    current_action: RobotAction = Field(default=RobotAction.IDLE, description="Current robot action")
    location: Optional[str] = Field(None, description="Current robot location")
    ip_address: Optional[str] = Field(None, description="Robot IP address")
    agent_id: Optional[str] = Field(None, description="Associated agent ID")
    health: Optional[RobotHealth] = Field(None, description="Robot health metrics")
    capabilities: List[str] = Field(default_factory=list, description="Robot capabilities")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional robot metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    last_update: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    class Config:
        use_enum_values = True


class Agent(BaseModel):
    """Agent domain model."""
    id: str = Field(..., description="Unique agent identifier")
    hostname: str = Field(..., description="Agent hostname")
    ip_address: str = Field(..., description="Agent IP address")
    status: str = Field(default="online", description="Agent status")
    system_info: SystemInfo
    robot_info: Dict[str, Any] = Field(default_factory=dict, description="Associated robot information")
    last_heartbeat: datetime = Field(default_factory=datetime.utcnow, description="Last heartbeat timestamp")
    connected_at: datetime = Field(default_factory=datetime.utcnow, description="Connection timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional agent metadata")


class CommandHistory(BaseModel):
    """Command history entry."""
    id: str = Field(..., description="Unique command ID")
    robot_id: str = Field(..., description="Target robot ID")
    command: str = Field(..., description="Command name")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Command parameters")
    status: str = Field(..., description="Command execution status")
    issued_by: str = Field(..., description="User who issued the command")
    issued_at: datetime = Field(default_factory=datetime.utcnow, description="Command issue timestamp")
    completed_at: Optional[datetime] = Field(None, description="Command completion timestamp")
    result: Optional[Dict[str, Any]] = Field(None, description="Command execution result")
    error_message: Optional[str] = Field(None, description="Error message if command failed")


class LogEntry(BaseModel):
    """Log entry model."""
    id: str = Field(..., description="Unique log entry ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Log timestamp")
    level: str = Field(..., description="Log level (INFO, WARNING, ERROR)")
    message: str = Field(..., description="Log message")
    source: str = Field(default="system", description="Log source")
    robot_id: Optional[str] = Field(None, description="Associated robot ID")
    agent_id: Optional[str] = Field(None, description="Associated agent ID")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional log metadata")
