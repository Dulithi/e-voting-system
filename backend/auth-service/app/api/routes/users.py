"""
User management endpoints for admin
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from datetime import datetime, timezone
from shared.database import get_db
from app.models.user import User
from app.utils.jwt_handler import verify_access_token

router = APIRouter()


class VoterResponse(BaseModel):
    user_id: str
    full_name: str
    email: str
    nic: str
    kyc_status: str
    created_at: str
    last_login_at: Optional[str]


def get_current_admin(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    """Verify admin access"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authorization header")
    
    token = authorization.split(" ")[1]
    user_id = verify_access_token(token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user or not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    
    return user


@router.get("/list", response_model=List[VoterResponse])
def list_voters(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """List all voters (non-admin users)"""
    rows = db.execute(
        text("""
        SELECT user_id, full_name, email, nic, kyc_status, created_at, last_login_at
        FROM users
        WHERE is_admin = false
        ORDER BY created_at DESC
        """)
    ).fetchall()
    
    return [
        VoterResponse(
            user_id=str(row[0]),
            full_name=row[1],
            email=row[2],
            nic=row[3],
            kyc_status=row[4],
            created_at=str(row[5]),
            last_login_at=str(row[6]) if row[6] else None
        )
        for row in rows
    ]


@router.post("/kyc/approve/{user_id}")
def approve_kyc(
    user_id: str,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Approve user KYC"""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.kyc_status = "APPROVED"
    user.kyc_verified_at = datetime.now(timezone.utc)
    user.kyc_verified_by = admin.user_id
    db.commit()
    
    return {"message": "KYC approved successfully"}


@router.post("/kyc/reject/{user_id}")
def reject_kyc(
    user_id: str,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Reject user KYC"""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.kyc_status = "REJECTED"
    user.kyc_verified_at = datetime.now(timezone.utc)
    user.kyc_verified_by = admin.user_id
    db.commit()
    
    return {"message": "KYC rejected"}
