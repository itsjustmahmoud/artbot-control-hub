"""
Custom application exceptions.
"""
from typing import Any, Dict, Optional


class ArtbotException(Exception):
    """Base exception class for the application."""
    
    def __init__(
        self, 
        message: str, 
        error_code: str = None, 
        details: Dict[str, Any] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class RobotNotFoundException(ArtbotException):
    """Exception raised when a robot is not found."""
    
    def __init__(self, robot_id: str):
        super().__init__(
            message=f"Robot {robot_id} not found",
            error_code="ROBOT_NOT_FOUND",
            details={"robot_id": robot_id}
        )


class RobotOfflineException(ArtbotException):
    """Exception raised when trying to control an offline robot."""
    
    def __init__(self, robot_id: str):
        super().__init__(
            message=f"Robot {robot_id} is offline",
            error_code="ROBOT_OFFLINE",
            details={"robot_id": robot_id}
        )


class AgentNotFoundException(ArtbotException):
    """Exception raised when an agent is not found."""
    
    def __init__(self, agent_id: str):
        super().__init__(
            message=f"Agent {agent_id} not found",
            error_code="AGENT_NOT_FOUND",
            details={"agent_id": agent_id}
        )


class CommandExecutionException(ArtbotException):
    """Exception raised when a robot command fails to execute."""
    
    def __init__(self, robot_id: str, command: str, reason: str):
        super().__init__(
            message=f"Command '{command}' failed on robot {robot_id}: {reason}",
            error_code="COMMAND_EXECUTION_FAILED",
            details={
                "robot_id": robot_id,
                "command": command,
                "reason": reason
            }
        )


class AuthenticationException(ArtbotException):
    """Exception raised for authentication failures."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_FAILED"
        )


class AuthorizationException(ArtbotException):
    """Exception raised for authorization failures."""
    
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_FAILED"
        )


class WebSocketException(ArtbotException):
    """Exception raised for WebSocket-related errors."""
    
    def __init__(self, message: str, connection_type: str = None):
        super().__init__(
            message=message,
            error_code="WEBSOCKET_ERROR",
            details={"connection_type": connection_type} if connection_type else {}
        )


class ValidationException(ArtbotException):
    """Exception raised for data validation errors."""
    
    def __init__(self, field: str, value: Any, reason: str):
        super().__init__(
            message=f"Validation failed for field '{field}': {reason}",
            error_code="VALIDATION_ERROR",
            details={
                "field": field,
                "value": value,
                "reason": reason
            }
        )
