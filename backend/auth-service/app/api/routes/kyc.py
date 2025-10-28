"""
KYC endpoints (MVP)
- submit: upload KYC metadata (stub)
- approve: admin approves KYC
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.config import settings
from shared.database import get_db
from shared.audit_helper import audit_kyc_status_change
from app.models.user import User
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class KYCSubmitRequest(BaseModel):
    user_id: str
    document_path: str


@router.post("/submit")
def kyc_submit(payload: KYCSubmitRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.kyc_document_path = payload.document_path
    db.commit()
    return {"status": "submitted"}


class KYCApproveRequest(BaseModel):
    user_id: str
    approve: bool = True


@router.post("/approve")
def kyc_approve(payload: KYCApproveRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    old_status = user.kyc_status
    new_status = "APPROVED" if payload.approve else "REJECTED"
    user.kyc_status = new_status
    db.commit()
    
    # Log to audit trail
    try:
        # Get admin user (should be passed from auth context in production)
        admin_user = db.query(User).filter(User.is_admin == True).first()
        admin_id = str(admin_user.user_id) if admin_user else None
        
        audit_kyc_status_change(
            db=db,
            user_id=payload.user_id,
            admin_id=admin_id,
            new_status=new_status,
            reason=f"Changed from {old_status} to {new_status}"
        )
    except Exception as e:
        logger.error(f"Failed to create KYC audit log: {e}")
    
    return {"status": user.kyc_status}
