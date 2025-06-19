from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any
import logging

from app.auth.simple_auth import SimpleAuth

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()

# Permission definitions
PERMISSIONS = {
    "ADMIN": [
        "robot.*",           # All robot operations
        "agent.*",           # All agent operations  
        "exhibition.*",      # All exhibition operations
        "system.*",          # All system operations
        "logs.*"             # All log access
    ],
    "MUSEUM": [
        "robot.view",        # View robot status
        "exhibition.start",  # Start exhibition
        "exhibition.stop",   # Stop exhibition
        "logs.view_basic"    # Basic log viewing
    ]
}

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Dependency to get current authenticated user"""
    token = credentials.credentials
    payload = SimpleAuth.verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload

def require_permission(permission: str):
    """Decorator factory to require specific permission"""
    def permission_checker(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        access_level = user.get("access_level")
        
        if not access_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access level not found in token"
            )
        
        user_permissions = PERMISSIONS.get(access_level, [])
        
        # Check if user has the required permission
        if not has_permission(user_permissions, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission} required"
            )
        
        return user
    
    return permission_checker

def has_permission(user_permissions: list, required_permission: str) -> bool:
    """Check if user has required permission"""
    for perm in user_permissions:
        if perm == "*":  # Super admin
            return True
        if perm == required_permission:
            return True
        if perm.endswith(".*") and required_permission.startswith(perm[:-1]):
            return True
    
    return False

# Common permission dependencies
require_admin = require_permission("system.*")
require_robot_control = require_permission("robot.control")
require_robot_view = require_permission("robot.view")
require_exhibition_control = require_permission("exhibition.start")
