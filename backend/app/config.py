from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # Authentication
    admin_password: str = os.getenv("ADMIN_PASSWORD", "admin123")
    museum_password: str = os.getenv("MUSEUM_PASSWORD", "museum123")
    
    # JWT Configuration
    jwt_secret: str = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
    jwt_algorithm: str = "HS256"
    jwt_expire_hours: int = 8
    
    # Hub Configuration
    hub_domain: str = os.getenv("HUB_DOMAIN", "http://localhost:8000")
    hub_port: int = int(os.getenv("HUB_PORT", "8000"))
    
    # Optional Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Development
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "info")
    
    class Config:
        env_file = ".env"

settings = Settings()
