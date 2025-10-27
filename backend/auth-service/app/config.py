"""
Authentication Service Configuration
"""
from pydantic_settings import BaseSettings
from typing import List
import os
from pathlib import Path

# Load .env from project root (3 levels up: auth-service/app -> auth-service -> backend -> root)
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    # Application
    app_name: str = "SecureVote Authentication Service"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Database
    database_url: str = os.getenv("DATABASE_URL")
    
    # JWT
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "XXDN41u505T0mk2uiPeqw4Lm6wa3ByNZ3V9B9iRF8Jq1RsePaLk7sDH8VogoJgTH2cy7ZcF")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    
    # WebAuthn
    webauthn_rp_name: str = "SecureVote E-Voting System"
    webauthn_rp_id: str = "localhost"
    webauthn_origin: str = "http://localhost:5173"
    
    # CORS - Don't load from .env, use defaults
    # allowed_origins: List[str] - Removed to avoid parsing issues
    
    # Security
    bcrypt_rounds: int = 12
    rate_limit_per_minute: int = 60
    
    # Service
    service_port: int = 8001
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        
    @property
    def allowed_origins(self) -> List[str]:
        """CORS allowed origins - parse from env or use defaults"""
        origins_str = os.getenv("ALLOWED_ORIGINS", "")
        if origins_str:
            return [origin.strip() for origin in origins_str.split(",")]
        # Default: Allow local development + mobile app connections
        return [
            "http://localhost:5173",
            "http://localhost:3000", 
            "http://127.0.0.1:5173",
            "http://192.168.1.1",  # Placeholder - will match any 192.168.x.x in CORS middleware
        ]


settings = Settings()
