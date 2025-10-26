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
from app.models.user import User

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
    user.kyc_status = "APPROVED" if payload.approve else "REJECTED"
    db.commit()
    return {"status": user.kyc_status}
