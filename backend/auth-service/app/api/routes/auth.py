"""
Authentication endpoints (MVP)
- register: create user with basic details
- login: username/password fallback
- refresh: issue new access token
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime
from typing import Optional
from app.config import settings
from shared.database import get_db
from app.models.user import User
from app.models.session import Session as SessionModel
from app.utils.jwt_handler import create_access_token, create_refresh_token, verify_refresh_token, verify_access_token
from shared.security import get_token_expiry

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class RegisterRequest(BaseModel):
    nic: str
    email: EmailStr
    full_name: str
    date_of_birth: str  # YYYY-MM-DD
    phone_number: str | None = None
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = settings.access_token_expire_minutes * 60


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


@router.post("/register", response_model=TokenResponse)
def register(payload: RegisterRequest, request: Request, db: Session = Depends(get_db)):
    # Check existing user
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    user = User(
        nic=payload.nic,
        email=payload.email,
        full_name=payload.full_name,
        date_of_birth=datetime.strptime(payload.date_of_birth, "%Y-%m-%d").date(),
        phone_number=payload.phone_number,
        password_hash=hash_password(payload.password),
        kyc_status="PENDING"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create tokens
    access_token = create_access_token(str(user.user_id))
    refresh_token = create_refresh_token(str(user.user_id))

    session = SessionModel(
        user_id=user.user_id,
        access_token=access_token,
        refresh_token=refresh_token,
        device_info={"user_agent": request.headers.get("User-Agent")},
        ip_address=request.client.host,
        expires_at=get_token_expiry("access")
    )
    db.add(session)
    db.commit()

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not user.password_hash or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(str(user.user_id))
    refresh_token = create_refresh_token(str(user.user_id))

    session = SessionModel(
        user_id=user.user_id,
        access_token=access_token,
        refresh_token=refresh_token,
        device_info={"user_agent": request.headers.get("User-Agent")},
        ip_address=request.client.host,
        expires_at=get_token_expiry("access")
    )
    db.add(session)
    db.commit()

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, request: Request, db: Session = Depends(get_db)):
    user_id = verify_refresh_token(payload.refresh_token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    # Optionally verify session exists
    session = db.query(SessionModel).filter(SessionModel.refresh_token == payload.refresh_token).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session not found")

    access_token = create_access_token(user_id)
    new_refresh_token = create_refresh_token(user_id)

    session.access_token = access_token
    session.refresh_token = new_refresh_token
    session.expires_at = get_token_expiry("access")
    db.commit()

    return TokenResponse(access_token=access_token, refresh_token=new_refresh_token)


class UserResponse(BaseModel):
    user_id: str
    email: str
    full_name: str
    is_admin: bool
    kyc_status: str


@router.get("/me", response_model=UserResponse)
def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid authorization header")
    
    token = authorization.split(" ")[1]
    user_id = verify_access_token(token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return UserResponse(
        user_id=str(user.user_id),
        email=user.email,
        full_name=user.full_name,
        is_admin=user.is_admin,
        kyc_status=user.kyc_status
    )

