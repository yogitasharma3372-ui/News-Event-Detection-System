"""
Application configuration using Pydantic Settings.
Loads settings from environment variables or .env file with defaults.
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "News Event Detection and Tracking System"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = True
    
    # Server configuration
    API_V1_PREFIX: str = "/api"
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    
    # Database
    DATABASE_URL: str = "sqlite:///./news_events.db"
    
    # Embedding Model Settings
    DEFAULT_EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_CACHE_DIR: str = "./data/cache/embeddings"
    
    # Hybrid Clustering Parameters (alpha + beta + gamma = 1.0)
    DEFAULT_ALPHA_SEMANTIC: float = 0.55
    DEFAULT_BETA_TEMPORAL: float = 0.25
    DEFAULT_GAMMA_ENTITY: float = 0.20
    
    # Clustering Thresholds
    DEFAULT_SIMILARITY_THRESHOLD: float = 0.60
    DEFAULT_TEMPORAL_DECAY_HOURS: float = 72.0
    
    # Live News API (Optional)
    NEWSAPI_KEY: str = ""
    NEWS_API_BASE_URL: str = "https://newsapi.org/v2"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
