"""
Shared security utilities and constants
"""
import os
from datetime import datetime, timedelta, timezone
from typing import Optional
import hashlib
import secrets

# Security constants
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change_this_to_very_long_random_secret_key_at_least_64_characters")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Password hashing configuration
BCRYPT_ROUNDS = 12

# Rate limiting
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
RATE_LIMIT_PER_HOUR = int(os.getenv("RATE_LIMIT_PER_HOUR", "1000"))

# Security headers
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'",
}

# CORS settings
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:3001").split(",")

def generate_secure_token(length: int = 32) -> str:
    """
    Generate a cryptographically secure random token
    """
    return secrets.token_urlsafe(length)

def hash_data(data: str) -> str:
    """
    SHA-256 hash of data (for non-password hashing)
    """
    return hashlib.sha256(data.encode()).hexdigest()

def constant_time_compare(a: str, b: str) -> bool:
    """
    Constant-time string comparison to prevent timing attacks
    """
    return secrets.compare_digest(a.encode(), b.encode())

def get_token_expiry(token_type: str = "access") -> datetime:
    """
    Calculate token expiry time
    """
    if token_type == "access":
        return datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    elif token_type == "refresh":
        return datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    else:
        raise ValueError(f"Unknown token type: {token_type}")
