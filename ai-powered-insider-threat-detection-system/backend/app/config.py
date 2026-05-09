"""
ITDT FastAPI Backend Configuration
"""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""
    
    APP_NAME: str = "ITDT - Insider Threat Detection"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database - using provided PostgreSQL connection
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"
    DATABASE_SCHEMA: str = "threat_detection"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production-min-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # Anomaly Thresholds
    COMPOSITE_HIGH_THRESHOLD: float = 0.55
    COMPOSITE_MEDIUM_THRESHOLD: float = 0.38
    
    # CORS
    CORS_ORIGINS: list = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
