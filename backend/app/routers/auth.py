from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any
import logging

from app.auth.simple_auth import SimpleAuth

logger = logging.getLogger(__name__)

router = APIRouter()

class LoginRequest(BaseModel):
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    access_level: str
    expires_in: int

@router.post("/validate", response_model=LoginResponse)
async def validate_password(login_request: LoginRequest):
    """Validate password and return JWT token"""
    password = login_request.password
    
    # Log attempt (without revealing password)
    password_hash = SimpleAuth.hash_password(password)
    logger.info(f"Login attempt with password hash: {password_hash}")
    
    # Validate password
    auth_result = SimpleAuth.validate_password(password)
    
    if auth_result is None:
        logger.warning(f"Failed login attempt with password hash: {password_hash}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    
    logger.info(f"Successful login: {auth_result['access_level']} user")
    
    return LoginResponse(
        access_token=auth_result["access_token"],
        token_type=auth_result["token_type"],
        access_level=auth_result["access_level"],
        expires_in=auth_result["expires_in"]
    )

@router.get("/me")
async def get_current_user_info(current_user: Dict[str, Any] = None):
    """Get current user information from token"""
    # This would use the middleware dependency, simplified for now
    return {
        "access_level": current_user.get("access_level") if current_user else "unknown",
        "expires_at": current_user.get("exp") if current_user else None
    }

@router.post("/logout")
async def logout():
    """Logout endpoint (client-side token removal)"""
    return {"message": "Logged out successfully"}

@router.get("/permissions/{access_level}")
async def get_permissions(access_level: str):
    """Get permissions for a specific access level"""
    from app.auth.middleware import PERMISSIONS
    
    if access_level.upper() not in PERMISSIONS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Access level not found"
        )
    
    return {
        "access_level": access_level.upper(),
        "permissions": PERMISSIONS[access_level.upper()]
    }
