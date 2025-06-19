"""
Application dependencies and dependency injection setup.
"""
from typing import Annotated
from fastapi import Depends
from app.core.config import Settings, get_settings
from app.services.robot_manager import RobotManager
from app.services.websocket_manager import ConnectionManager


# Settings dependency
SettingsDep = Annotated[Settings, Depends(get_settings)]


# Service dependencies
def get_robot_manager() -> RobotManager:
    """Get robot manager instance."""
    from app.services.robot_manager import robot_manager
    return robot_manager


def get_websocket_manager() -> ConnectionManager:
    """Get WebSocket connection manager instance."""
    from app.services.websocket_manager import connection_manager
    return connection_manager


RobotManagerDep = Annotated[RobotManager, Depends(get_robot_manager)]
WebSocketManagerDep = Annotated[ConnectionManager, Depends(get_websocket_manager)]
