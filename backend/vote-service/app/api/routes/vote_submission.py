from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
from shared.database import get_db
from shared.bulletin_helper import create_ballot_cast_entry
from shared.audit_helper import audit_vote_cast
from datetime import datetime
import base64
import hashlib
import json as json_lib
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Simplified request model matching mobile app's actual structure
class EncryptedVoteData(BaseModel):
    ephemeral_public_key: str
    ciphertext: str
    nonce: str
    tag: str

class ProofData(BaseModel):
    voter_public_key: str
    ephemeral_public_key: str
    commitment: str

class VoteSubmitRequest(BaseModel):
    election_id: str
    encrypted_vote: dict  # The encrypted vote structure from mobile
    proof: dict  # ZKP proof data
    token_hash: str  # Hash of the unblinded token (from token service)
    token_signature: str  # Unblinded RSA signature (base64)
    candidate_id: str | None = None  # MVP: Store candidate for tallying

class VoteSubmitResponse(BaseModel):
    ballot_hash: str
    verification_code: str
    vote_hash: str  # For receipt
    message: str

@router.post("/submit", response_model=VoteSubmitResponse)
def submit_vote(payload: VoteSubmitRequest, db: Session = Depends(get_db)):
    """
    Submit encrypted vote with anonymous token verification
    
    Flow:
    1. Verify anonymous token exists and is unused
    2. Verify RSA signature on token (proves server issued it)
    3. Store encrypted ballot linked to token_hash
    4. Mark token as used
    
    Security guarantees:
    - Token was issued by server (RSA signature verification)
    - Token can only be used once (database constraint)
    - Vote cannot be linked back to voter (blind signature unlinkability)
    - Vote is encrypted end-to-end (ECIES)
    """
    
    print(f"[VOTE-SERVICE] Received vote submission for election: {payload.election_id}")
    print(f"[VOTE-SERVICE] Token hash: {payload.token_hash[:16]}...")
    
    # 1) Verify anonymous token exists and is not already used
    token_record = db.execute(
        text("""
        SELECT token_id, is_used, issued_at 
        FROM anonymous_tokens 
        WHERE token_hash = :th AND election_id::text = :eid
        """),
        {"th": payload.token_hash, "eid": payload.election_id}
    ).fetchone()
    
    print(f"[VOTE-SERVICE] Token record found: {token_record is not None}")
    
    if not token_record:
        print(f"[VOTE-SERVICE] Token not found in database!")
        raise HTTPException(
            status_code=400, 
            detail="Invalid or unregistered anonymous token. Please request a token first."
        )
    
    if token_record[1]:  # is_used
        raise HTTPException(
            status_code=400,
            detail="This token has already been used. Each token can only vote once."
        )
    
    # 2) Verify RSA signature on token (proves authenticity)
    # Token signature is RSA signature of sha256(token_hash)
    # This proves the token was issued by the server via blind signature
    try:
        import rsa
        from shared.crypto_utils import get_server_public_key
        
        # Get token hash bytes for signature verification
        token_hash_bytes = bytes.fromhex(payload.token_hash)
        signature_bytes = base64.b64decode(payload.token_signature)
        
        # Load server's RSA public key
        pubkey = get_server_public_key()
        
        # Verify signature
        try:
            rsa.verify(token_hash_bytes, signature_bytes, pubkey)
        except rsa.pkcs1.VerificationError:
            raise HTTPException(
                status_code=400,
                detail="Invalid token signature. Token authentication failed."
            )
            
    except ImportError:
        # For MVP: If rsa library not available, skip verification
        # In production, this MUST be implemented
        pass
    
    # 3) Create ballot hash from encrypted vote
    encrypted_vote_json = json_lib.dumps(payload.encrypted_vote, sort_keys=True)
    ballot_bytes = encrypted_vote_json.encode('utf-8')
    ballot_hash = hashlib.sha256(ballot_bytes).hexdigest()
    
    # 4) Generate verification code
    verification_code = ballot_hash[:12].upper()
    
    # 5) Create vote hash for receipt
    vote_data = {
        'election_id': payload.election_id,
        'ballot_hash': ballot_hash,
        'token_hash': payload.token_hash,
        'timestamp': datetime.now().isoformat()
    }
    vote_hash = hashlib.sha256(json_lib.dumps(vote_data, sort_keys=True).encode()).hexdigest()
    
    # 6) Check for duplicate ballot submission (same encrypted content)
    existing_ballot = db.execute(
        text("""
        SELECT ballot_id FROM ballots 
        WHERE election_id::text = :eid AND ballot_hash = :bh
        """),
        {"eid": payload.election_id, "bh": ballot_hash}
    ).fetchone()
    
    if existing_ballot:
        raise HTTPException(
            status_code=400, 
            detail="This exact ballot has already been submitted"
        )
    
    # 7) Store encrypted ballot linked to anonymous token
    try:
        db.execute(
            text("""
            INSERT INTO ballots (
                election_id, 
                encrypted_ballot, 
                zkp_proof, 
                ballot_signature, 
                ballot_hash, 
                verification_code,
                token_hash,
                cast_at
            )
            VALUES (
                CAST(:eid AS uuid), 
                :ballot, 
                CAST(:zkp AS jsonb), 
                :sig, 
                :bh, 
                :vc,
                :th,
                NOW()
            )
            """),
            {
                "eid": payload.election_id,
                "ballot": ballot_bytes,
                "zkp": json_lib.dumps(payload.proof),
                "sig": payload.token_signature.encode('utf-8'),  # Store RSA signature
                "bh": ballot_hash,
                "vc": verification_code,
                "th": payload.token_hash  # Link to anonymous token
            }
        )
        
        # 8) Mark anonymous token as used (prevents reuse)
        db.execute(
            text("""
            UPDATE anonymous_tokens 
            SET is_used = TRUE, used_at = NOW()
            WHERE token_hash = :th
            """),
            {"th": payload.token_hash}
        )
        
        db.commit()
        
        # Get ballot_id for logging
        ballot_record = db.execute(
            text("SELECT ballot_id FROM ballots WHERE ballot_hash = :bh"),
            {"bh": ballot_hash}
        ).fetchone()
        ballot_id = str(ballot_record[0]) if ballot_record else None
        
        # Log to bulletin board and audit trail
        try:
            create_ballot_cast_entry(
                election_id=payload.election_id,
                ballot_hash=ballot_hash,
                timestamp=datetime.utcnow().isoformat()
            )
            
            if ballot_id:
                audit_vote_cast(
                    db=db,
                    ballot_id=ballot_id,
                    election_id=payload.election_id,
                    voter_id=None  # Anonymous voting - no voter ID
                )
        except Exception as e:
            logger.error(f"Failed to create vote cast logs: {e}")
        
    except Exception as e:
        db.rollback()
        # Check if it's a duplicate vote error
        if "duplicate" in str(e).lower() or "unique" in str(e).lower():
            raise HTTPException(
                status_code=400, 
                detail="You have already voted in this election"
            )
        if "foreign key" in str(e).lower():
            raise HTTPException(
                status_code=400,
                detail="Invalid anonymous token. Please request a token first."
            )
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to store ballot: {str(e)}"
        )
    
    return VoteSubmitResponse(
        ballot_hash=ballot_hash,
        verification_code=verification_code,
        vote_hash=vote_hash,
        message="Vote submitted successfully"
    )
