"""
Authentication Service Configuration
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Application
    app_name: str = "SecureVote Authentication Service"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "postgresql://evoting_admin:secure_password_123@postgres:5432/evoting_db")
    
    # JWT
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "change_this_to_very_long_random_secret_key")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    
    # WebAuthn
    webauthn_rp_name: str = "SecureVote E-Voting System"
    webauthn_rp_id: str = "localhost"
    webauthn_origin: str = "http://localhost:5173"
    
    # CORS
    allowed_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Security
    bcrypt_rounds: int = 12
    rate_limit_per_minute: int = 60
    
    # Service
    service_port: int = 8001
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
