"""
Configuration settings for RootMind.
Loads environment variables from .env file using pydantic-settings.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "RootMind AIOps"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./rootmind.db"
    
    # AI & Vector DB (Free Tier Keys)
    GROQ_API_KEY: str = ""
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str = ""
    
    # Integrations
    SLACK_WEBHOOK_URL: str = ""
    GITHUB_TOKEN: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()