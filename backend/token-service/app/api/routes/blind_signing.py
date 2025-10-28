"""
Blind Signature API Routes - RSA Blind Signature Implementation
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
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
        text("""
        SELECT code_id, main_code_used FROM voting_codes 
        WHERE main_voting_code = :code AND election_id::text = :eid
        """),
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
        
        # Store anonymous token record with blinded signature
        db.execute(
            text("""
            INSERT INTO anonymous_tokens 
            (election_id, token_hash, signed_blind_token, issued_at, is_used)
            VALUES (CAST(:eid AS uuid), :hash, :sig, :issued_at, FALSE)
            """),
            {
                "eid": payload.election_id,
                "hash": token_hash,
                "sig": blinded_signature_bytes,  # Store the blinded signature
                "issued_at": datetime.utcnow()
            }
        )
        
        # Mark main code used
        db.execute(
            text("""
            UPDATE voting_codes 
            SET main_code_used = true, main_code_used_at = now() 
            WHERE code_id = :cid
            """),
            {"cid": vc[0]}
        )
        
        db.commit()
        
        print(f"[TOKEN-SERVICE] Blind signature issued for election {payload.election_id}")
        print(f"[TOKEN-SERVICE] Token hash: {token_hash[:20]}...")
        
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


class CreateTokenDirectRequest(BaseModel):
    election_id: str
    token_hash: str


@router.post("/create-direct")
def create_token_direct(payload: CreateTokenDirectRequest, db: Session = Depends(get_db)):
    """
    Create anonymous token directly (simplified MVP approach)
    Skips blind signature protocol for simplified implementation
    """
    print(f"[TOKEN-SERVICE] Creating token for election: {payload.election_id}")
    print(f"[TOKEN-SERVICE] Token hash: {payload.token_hash[:16]}...")
    
    try:
        # Check if token already exists
        existing = db.execute(
            text("""
            SELECT token_id FROM anonymous_tokens 
            WHERE token_hash = :th
            """),
            {"th": payload.token_hash}
        ).fetchone()
        
        if existing:
            print(f"[TOKEN-SERVICE] Token already exists: {existing[0]}")
            return {
                "message": "Token already exists",
                "token_hash": payload.token_hash
            }
        
        # Create token record
        # For simplified MVP: Use token_hash as placeholder for signed_blind_token
        placeholder_signature = bytes.fromhex(payload.token_hash)
        
        db.execute(
            text("""
            INSERT INTO anonymous_tokens 
            (election_id, token_hash, signed_blind_token, issued_at, is_used)
            VALUES (CAST(:eid AS uuid), :hash, :sig, :issued_at, FALSE)
            """),
            {
                "eid": payload.election_id,
                "hash": payload.token_hash,
                "sig": placeholder_signature,
                "issued_at": datetime.utcnow()
            }
        )
        
        db.commit()
        
        print(f"[TOKEN-SERVICE] Token created successfully")
        
        return {
            "message": "Anonymous token created successfully",
            "token_hash": payload.token_hash
        }
        
    except Exception as e:
        db.rollback()
        print(f"[TOKEN-SERVICE] Error creating token: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create token: {str(e)}")


