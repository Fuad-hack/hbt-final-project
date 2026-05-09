"""
ITDT FastAPI Backend Configuration
Pydantic v2 Settings for the application
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "ITDT - Insider Threat Detection"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/threatwatch",
        description="PostgreSQL async connection string"
    )
    DATABASE_SCHEMA: str = "threat_detection"
    
    # Redis
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection for Celery and caching"
    )
    
    # Security
    SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production-min-32-chars",
        description="JWT signing key"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Anomaly Thresholds
    COMPOSITE_HIGH_THRESHOLD: float = 0.55  # Above = HIGH risk
    COMPOSITE_MEDIUM_THRESHOLD: float = 0.38  # Above = MEDIUM risk
    
    # Celery
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/0")
    
    # ML Pipeline
    ML_FEATURES_BATCH_SIZE: int = 1000
    ML_TRAINING_DATA_LIMIT: Optional[int] = None  # None = all data
    XAI_TOP_N_USERS: int = 10  # Number of users to explain
    
    # CORS
    CORS_ORIGINS: list[str] = Field(default=["*"])  # Restrict in production
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()
