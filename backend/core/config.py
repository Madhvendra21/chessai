import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "ChessVision AI"
    VERSION: str = "1.0.0"
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/chessvision"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Storage
    UPLOAD_DIR: str = "data/uploads"
    FRAMES_DIR: str = "data/frames"
    MODELS_DIR: str = "data/models"
    MAX_UPLOAD_SIZE: int = 500 * 1024 * 1024  # 500MB
    
    # Stockfish
    STOCKFISH_PATH: Optional[str] = None
    STOCKFISH_DEPTH: int = 18
    STOCKFISH_TIME: float = 1.0
    
    # CV Pipeline
    FRAME_EXTRACTION_FPS: int = 2
    CONFIDENCE_THRESHOLD: float = 0.5
    BOARD_DETECTION_THRESHOLD: float = 0.7
    
    # Processing
    MAX_WORKERS: int = 4
    JOB_TIMEOUT: int = 3600  # 1 hour
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# Ensure directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.FRAMES_DIR, exist_ok=True)
os.makedirs(settings.MODELS_DIR, exist_ok=True)
