"""Application configuration via environment variables."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost/swasthyasetu"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Auth
    SECRET_KEY: str = "dev-secret-key-change-in-production-min-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # External APIs
    GEMINI_API_KEY: Optional[str] = None
    DAILY_API_KEY: Optional[str] = None
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    FIREBASE_CREDENTIALS: Optional[str] = None
    FIREBASE_CREDENTIALS_JSON: Optional[str] = None  # add this line
    # App
    APP_NAME: str = "SwasthyaSetu API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
