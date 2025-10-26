"""
Blind Signature API Routes - RSA Blind Signature Implementation
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from shared.database import get_db
from app.utils.blind_signature import get_blind_signer
from datetime import datetime
import base64
import hashlib

router = APIRouter()

class BlindSignRequest(BaseModel):
    election_id: str
    main_voting_code: str
    blinded_token: str  # base64 encoded blinded message

class BlindSignResponse(BaseModel):
    blinded_signature: str  # base64 encoded blind signature
    token_hash: str  # For anonymity tracking
    public_key: str  # Server's public key for verification

@router.post("/request-signature", response_model=BlindSignResponse)
def request_signature(payload: BlindSignRequest, db: Session = Depends(get_db)):
    """
    Issue RSA blind signature for anonymous voting token
    Server signs blinded message without seeing original
    """
    # Validate main_voting_code exists and not used
    vc = db.execute(
        """
        SELECT code_id, main_code_used FROM voting_codes 
        WHERE main_voting_code = :code AND election_id::text = :eid
        """,
        {"code": payload.main_voting_code, "eid": payload.election_id}
    ).fetchone()
    
    if not vc:
        raise HTTPException(status_code=400, detail="Invalid main voting code")
    if vc[1]:
        raise HTTPException(status_code=400, detail="Main code already used")

    try:
        # Decode blinded token
        blinded_bytes = base64.b64decode(payload.blinded_token)
        
        # Get blind signer and sign the blinded message
        signer = get_blind_signer()
        blinded_signature_bytes = signer.blind_sign(blinded_bytes)
        
        # Encode signature
        blinded_signature = base64.b64encode(blinded_signature_bytes).decode('utf-8')
        
        # Compute token hash from blinded token (maintains anonymity)
        token_hash = hashlib.sha256(blinded_bytes).hexdigest()
        
        # Store anonymous token record
        db.execute(
            """
            INSERT INTO anonymous_tokens 
            (election_id, token_hash, issued_at, is_used)
            VALUES (:eid::uuid, :hash, :issued_at, FALSE)
            """,
            {
                "eid": payload.election_id,
                "hash": token_hash,
                "issued_at": datetime.utcnow()
            }
        )
        
        # Mark main code used
        db.execute(
            "UPDATE voting_codes SET main_code_used = true, main_code_used_at = now() WHERE code_id = :cid",
            {"cid": vc[0]}
        )
        
        db.commit()
        
        return BlindSignResponse(
            blinded_signature=blinded_signature,
            token_hash=token_hash,
            public_key=signer.export_public_key()
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Blind signature failed: {str(e)}")


@router.get("/public-key")
def get_public_key():
    """Get server's public key for blind signature operations"""
    signer = get_blind_signer()
    return {
        "public_key": signer.export_public_key(),
        "algorithm": "RSA-2048",
        "purpose": "Blind signature for anonymous voting tokens"
    }

