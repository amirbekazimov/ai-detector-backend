"""Application configuration."""

import os
from typing import List

from pydantic import BaseModel, Field, computed_field


class Settings(BaseModel):
    """Application settings."""
    
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    BACKEND_CORS_ORIGINS_STR: str = Field(default="http://localhost:3000,http://localhost:8080,http://127.0.0.1:5500,http://localhost:5173,http://localhost:5174,http://127.0.0.1:5173,http://127.0.0.1:5174")
    
    @computed_field
    @property
    def BACKEND_CORS_ORIGINS(self) -> List[str]:
        return [i.strip() for i in self.BACKEND_CORS_ORIGINS_STR.split(",")]
    
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "root123")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "ai_detector")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    
    @property
    def DATABASE_URL(self) -> str:
        # Use provided DATABASE_URL if available (for Supabase/Render production)
        if os.getenv("DATABASE_URL"):
            return os.getenv("DATABASE_URL")
        
        # Use local PostgreSQL for development
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    PROJECT_NAME: str = "AI Detector API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "AI Detection Service API"
    
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # API URL for generating tracking scripts
    @property
    def API_URL(self) -> str:
        # If API_URL is explicitly set, use it
        if os.getenv("API_URL"):
            return os.getenv("API_URL")
        
        # Auto-detect based on environment
        if self.ENVIRONMENT == "production":
            return "https://ai-detector-backend-nsv6.onrender.com"
        else:
            return "http://localhost:8000"
    
    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
