"""
Core application configuration and settings.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from typing import List


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application
    app_name: str = "Artbot Control Hub"
    app_version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Authentication
    admin_password: str = os.getenv("ADMIN_PASSWORD", "admin123")
    museum_password: str = os.getenv("MUSEUM_PASSWORD", "museum123")
    
    # JWT Configuration
    jwt_secret: str = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
    jwt_algorithm: str = "HS256"
    jwt_expire_hours: int = 8
    
    # Server Configuration
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    hub_domain: str = os.getenv("HUB_DOMAIN", "http://localhost:8000")
    
    # CORS Configuration
    cors_origins: List[str] = ["*"]  # Configure properly for production
    cors_credentials: bool = True
    cors_methods: List[str] = ["*"]
    cors_headers: List[str] = ["*"]
    
    # WebSocket Configuration
    websocket_timeout: int = 30
    websocket_ping_interval: int = 10
    
    # Redis Configuration (Optional)
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    use_redis: bool = os.getenv("USE_REDIS", "false").lower() == "true"
    
    # Logging Configuration
    log_level: str = os.getenv("LOG_LEVEL", "info")
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Robot Management
    robot_heartbeat_timeout: int = 60  # seconds
    max_command_history: int = 1000
    max_robot_logs: int = 1000
    
    # System Limits
    max_concurrent_connections: int = 100
    max_robots_per_exhibition: int = 50
    command_timeout: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


# Global settings instance
settings = get_settings()
