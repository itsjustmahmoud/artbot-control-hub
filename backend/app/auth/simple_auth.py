from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
import hashlib
from app.config import settings

class SimpleAuth:
    """Simple two-password authentication system"""
    
    @staticmethod
    def validate_password(password: str) -> Optional[Dict[str, Any]]:
        """Validate password and return access level"""
        if password == settings.admin_password:
            return SimpleAuth._create_token("ADMIN")
        elif password == settings.museum_password:
            return SimpleAuth._create_token("MUSEUM")
        else:
            return None
    
    @staticmethod
    def _create_token(access_level: str) -> Dict[str, Any]:
        """Create JWT token with access level"""
        payload = {
            "access_level": access_level,
            "exp": datetime.utcnow() + timedelta(hours=settings.jwt_expire_hours),
            "iat": datetime.utcnow(),
            "sub": f"user_{access_level.lower()}"
        }
        
        token = jwt.encode(
            payload, 
            settings.jwt_secret, 
            algorithm=settings.jwt_algorithm
        )
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "access_level": access_level,
            "expires_in": settings.jwt_expire_hours * 3600  # seconds
        }
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(
                token, 
                settings.jwt_secret, 
                algorithms=[settings.jwt_algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.JWTError:
            return None
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password for logging (without revealing actual password)"""
        return hashlib.sha256(password.encode()).hexdigest()[:8]
