from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://powerplant:powerplant_pass@db:5432/powerplant_pms"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # File Storage
    UPLOAD_DIR: str = "/app/uploads"
    ARCHIVE_DIR: str = "/app/archive"
    MAX_UPLOAD_SIZE: int = 500 * 1024 * 1024  # 500MB
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

