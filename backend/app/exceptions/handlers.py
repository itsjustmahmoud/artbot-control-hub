"""
Exception handlers for FastAPI application.
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import ValidationError
import logging

from app.exceptions.custom import (
    ArtbotException,
    RobotNotFoundException,
    RobotOfflineException,
    AgentNotFoundException,
    CommandExecutionException,
    AuthenticationException,
    AuthorizationException,
    WebSocketException,
    ValidationException
)

logger = logging.getLogger(__name__)


async def artbot_exception_handler(request: Request, exc: ArtbotException) -> JSONResponse:
    """Handle custom application exceptions."""
    logger.error(f"Application error: {exc.message}", exc_info=exc)
    
    status_map = {
        "ROBOT_NOT_FOUND": status.HTTP_404_NOT_FOUND,
        "AGENT_NOT_FOUND": status.HTTP_404_NOT_FOUND,
        "ROBOT_OFFLINE": status.HTTP_400_BAD_REQUEST,
        "COMMAND_EXECUTION_FAILED": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "AUTHENTICATION_FAILED": status.HTTP_401_UNAUTHORIZED,
        "AUTHORIZATION_FAILED": status.HTTP_403_FORBIDDEN,
        "WEBSOCKET_ERROR": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "VALIDATION_ERROR": status.HTTP_422_UNPROCESSABLE_ENTITY,
    }
    
    status_code = status_map.get(exc.error_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "message": exc.message,
                "code": exc.error_code,
                "details": exc.details
            }
        }
    )


async def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Handle FastAPI validation errors."""
    logger.error(f"Validation error: {exc}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "message": "Validation failed",
                "code": "VALIDATION_ERROR",
                "details": exc.errors()
            }
        }
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTP exceptions."""
    logger.error(f"HTTP error: {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.detail,
                "code": "HTTP_ERROR"
            }
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=exc)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "message": "Internal server error",
                "code": "INTERNAL_ERROR"
            }
        }
    )
