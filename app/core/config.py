"""Application configuration."""

import os
from typing import List

from pydantic import BaseModel, Field, validator


class Settings(BaseModel):
    """Application settings."""
    
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    BACKEND_CORS_ORIGINS_STR: str = Field(default="http://localhost:3000,http://localhost:8080,http://127.0.0.1:5500,http://localhost:5173,http://localhost:5174,http://127.0.0.1:5173,http://127.0.0.1:5174")
    
    @validator('BACKEND_CORS_ORIGINS_STR', pre=True)
    def assemble_cors_origins(cls, v: str) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "password")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "ai_detector")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    
    @property
    def DATABASE_URL(self) -> str:
        # Use SQLite for local development, PostgreSQL for production
        if self.ENVIRONMENT == "development":
            return "sqlite:///./ai_detector.db"
        else:
            return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    PROJECT_NAME: str = "AI Detector API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "AI Detection Service API"
    
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
