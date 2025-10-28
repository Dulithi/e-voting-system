from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
from shared.database import get_db
from shared.bulletin_helper import create_trustee_share_entry, create_key_generated_entry
from shared.audit_helper import audit_trustee_share_submitted, audit_key_ceremony
from typing import List, Optional
import sys
import json
import logging

logger = logging.getLogger(__name__)

# Import threshold crypto - path is already set in main.py
try:
    from shared.threshold_crypto import (
        ThresholdCrypto, 
        generate_election_keypair_with_trustees,
        generate_trustee_keypair
    )
    print("[TRUSTEE] ✅ ThresholdCrypto imported successfully")
except ImportError as e:
    # Fallback for development
    print(f"[TRUSTEE] ❌ Failed to import ThresholdCrypto: {e}")
    ThresholdCrypto = None

router = APIRouter()

class TrusteeAdd(BaseModel):
    election_id: str
    user_id: str

class TrusteeResponse(BaseModel):
    trustee_id: str
    election_id: str
    user_id: str
    user_email: str
    user_name: str
    has_key_share: bool
    shares_submitted: bool
    created_at: str

class KeyCeremonyRequest(BaseModel):
    election_id: str

class KeyCeremonyResponse(BaseModel):
    election_id: str
    threshold: int
    total_trustees: int
    public_key: str
    trustees_updated: int

class SubmitShareRequest(BaseModel):
    trustee_id: str
    decryption_shares: dict  # {ballot_id: partial_decryption}

class MyElectionResponse(BaseModel):
    trustee_id: str
    election_id: str
    election_title: str
    election_status: str
    start_time: str
    end_time: str
    has_key_share: bool
    shares_submitted: bool
    threshold: int
    total_trustees: int
    trustees_submitted: int

@router.get("/my-elections/{user_id}", response_model=List[MyElectionResponse])
def get_my_trustee_elections(user_id: str, db: Session = Depends(get_db)):
    """Get all elections where the user is a trustee"""
    
    rows = db.execute(
        text("""
        SELECT 
            t.trustee_id,
            e.election_id,
            e.title,
            e.status,
            e.start_time,
            e.end_time,
            CASE WHEN t.public_key_share IS NOT NULL THEN true ELSE false END as has_key_share,
            t.shares_submitted,
            e.threshold_t,
            e.total_trustees_n,
            (SELECT COUNT(*) FROM trustees t2 
             WHERE t2.election_id = e.election_id 
             AND t2.shares_submitted = true) as trustees_submitted
        FROM trustees t
        JOIN elections e ON t.election_id = e.election_id
        WHERE t.user_id = CAST(:uid AS uuid)
        ORDER BY e.created_at DESC
        """),
        {"uid": user_id}
    ).fetchall()
    
    return [
        MyElectionResponse(
            trustee_id=str(row[0]),
            election_id=str(row[1]),
            election_title=row[2],
            election_status=row[3],
            start_time=str(row[4]),
            end_time=str(row[5]),
            has_key_share=row[6],
            shares_submitted=row[7],
            threshold=row[8],
            total_trustees=row[9],
            trustees_submitted=row[10]
        )
        for row in rows
    ]

@router.post("/add")
def add_trustee(payload: TrusteeAdd, db: Session = Depends(get_db)):
    """Add a trustee to an election"""
    
    # Verify election exists
    election = db.execute(
        text("SELECT election_id, total_trustees_n FROM elections WHERE election_id = CAST(:eid AS uuid)"),
        {"eid": payload.election_id}
    ).fetchone()
    
    if not election:
        raise HTTPException(status_code=404, detail="Election not found")
    
    # Check if user exists
    user = db.execute(
        text("SELECT user_id, email FROM users WHERE user_id = CAST(:uid AS uuid)"),
        {"uid": payload.user_id}
    ).fetchone()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if already a trustee
    existing = db.execute(
        text("""
        SELECT trustee_id FROM trustees 
        WHERE election_id = CAST(:eid AS uuid) AND user_id = CAST(:uid AS uuid)
        """),
        {"eid": payload.election_id, "uid": payload.user_id}
    ).fetchone()
    
    if existing:
        raise HTTPException(status_code=400, detail="User is already a trustee for this election")
    
    # Count existing trustees
    trustee_count = db.execute(
        text("SELECT COUNT(*) FROM trustees WHERE election_id = CAST(:eid AS uuid)"),
        {"eid": payload.election_id}
    ).scalar()
    
    if trustee_count >= election[1]:  # total_trustees_n
        raise HTTPException(
            status_code=400, 
            detail=f"Maximum number of trustees ({election[1]}) already reached"
        )
    
    row = db.execute(
        text("""
        INSERT INTO trustees (election_id, user_id)
        VALUES (CAST(:eid AS uuid), CAST(:uid AS uuid))
        RETURNING trustee_id
        """),
        {"eid": payload.election_id, "uid": payload.user_id}
    ).fetchone()
    db.commit()
    
    return {
        "trustee_id": str(row[0]),
        "election_id": payload.election_id,
        "user_id": payload.user_id,
        "user_email": user[1],
        "message": "Trustee added successfully"
    }

@router.get("/election/{election_id}", response_model=List[TrusteeResponse])
def get_election_trustees(election_id: str, db: Session = Depends(get_db)):
    """Get all trustees for an election"""
    
    trustees = db.execute(
        text("""
        SELECT 
            t.trustee_id, t.election_id, t.user_id, u.email, u.full_name,
            (t.public_key_share IS NOT NULL) as has_key_share,
            t.shares_submitted,
            t.created_at
        FROM trustees t
        JOIN users u ON t.user_id = u.user_id
        WHERE t.election_id = CAST(:eid AS uuid)
        ORDER BY t.created_at
        """),
        {"eid": election_id}
    ).fetchall()
    
    return [
        TrusteeResponse(
            trustee_id=str(row[0]),
            election_id=str(row[1]),
            user_id=str(row[2]),
            user_email=row[3],
            user_name=row[4],
            has_key_share=row[5],
            shares_submitted=row[6],
            created_at=str(row[7])
        )
        for row in trustees
    ]

@router.post("/key-ceremony", response_model=KeyCeremonyResponse)
def initiate_key_ceremony(payload: KeyCeremonyRequest, db: Session = Depends(get_db)):
    """
    Initiate key ceremony for election
    Generates election keypair and distributes shares to trustees
    """
    
    if not ThresholdCrypto:
        raise HTTPException(
            status_code=500, 
            detail="Threshold cryptography not available. Install cryptography package."
        )
    
    # Get election details
    election = db.execute(
        text("""
        SELECT election_id, threshold_t, total_trustees_n, public_key 
        FROM elections 
        WHERE election_id = CAST(:eid AS uuid)
        """),
        {"eid": payload.election_id}
    ).fetchone()
    
    if not election:
        raise HTTPException(status_code=404, detail="Election not found")
    
    threshold = election[1]
    total_trustees = election[2]
    
    # Check if key ceremony already performed
    if election[3]:
        raise HTTPException(status_code=400, detail="Key ceremony already completed for this election")
    
    # Get all trustees
    trustees = db.execute(
        text("""
        SELECT trustee_id, user_id 
        FROM trustees 
        WHERE election_id = CAST(:eid AS uuid)
        ORDER BY created_at
        """),
        {"eid": payload.election_id}
    ).fetchall()
    
    if len(trustees) < total_trustees:
        raise HTTPException(
            status_code=400,
            detail=f"Not enough trustees accepted. Need {total_trustees}, have {len(trustees)}"
        )
    
    print(f"[TRUSTEE] Initiating key ceremony for election {payload.election_id}")
    print(f"[TRUSTEE] Threshold: {threshold}, Total Trustees: {total_trustees}")
    
    # Generate election keypair with trustee shares
    key_material = generate_election_keypair_with_trustees(threshold, total_trustees)
    
    public_key_pem = key_material['public_key'].decode('utf-8')
    trustee_shares = key_material['trustee_shares']
    
    # Update election with public key
    db.execute(
        text("""
        UPDATE elections 
        SET public_key = :pubkey
        WHERE election_id = CAST(:eid AS uuid)
        """),
        {"eid": payload.election_id, "pubkey": public_key_pem}
    )
    
    # Distribute shares to trustees
    trustees_updated = 0
    for i, (trustee_id, user_id) in enumerate(trustees[:total_trustees]):
        share = trustee_shares[i]
        
        db.execute(
            text("""
            UPDATE trustees 
            SET 
                public_key_share = :pubkey_share,
                key_share_proof = :proof
            WHERE trustee_id = :tid
            """),
            {
                "tid": trustee_id,
                "pubkey_share": json.dumps(share),
                "proof": share['proof']
            }
        )
        trustees_updated += 1
    
    db.commit()
    
    print(f"[TRUSTEE] Key ceremony completed. Updated {trustees_updated} trustees")
    
    # Log to bulletin board and audit trail
    try:
        create_key_generated_entry(
            election_id=payload.election_id,
            public_key=public_key_pem,
            threshold=threshold,
            participants=trustees_updated
        )
        
        audit_key_ceremony(
            db=db,
            election_id=payload.election_id,
            trustees_count=trustees_updated,
            threshold=threshold
        )
    except Exception as e:
        logger.error(f"Failed to create key ceremony logs: {e}")
    
    return KeyCeremonyResponse(
        election_id=payload.election_id,
        threshold=threshold,
        total_trustees=total_trustees,
        public_key=public_key_pem,
        trustees_updated=trustees_updated
    )

@router.post("/submit-decryption-share")
def submit_decryption_share(payload: SubmitShareRequest, db: Session = Depends(get_db)):
    """Trustee submits their decryption shares for ballots"""
    
    # Verify trustee exists and has key share
    trustee = db.execute(
        text("""
        SELECT trustee_id, election_id, public_key_share
        FROM trustees 
        WHERE trustee_id = CAST(:tid AS uuid)
        """),
        {"tid": payload.trustee_id}
    ).fetchone()
    
    if not trustee:
        raise HTTPException(status_code=404, detail="Trustee not found")
    
    if not trustee[2]:  # public_key_share
        raise HTTPException(status_code=400, detail="Trustee has not received key share yet")
    
    # Update trustee with decryption shares
    db.execute(
        text("""
        UPDATE trustees 
        SET 
            decryption_shares = CAST(:shares AS jsonb),
            shares_submitted = true,
            shares_submitted_at = NOW()
        WHERE trustee_id = CAST(:tid AS uuid)
        """),
        {
            "tid": payload.trustee_id,
            "shares": json.dumps(payload.decryption_shares)
        }
    )
    
    db.commit()
    
    election_id = str(trustee[1])
    share_count = len(payload.decryption_shares)
    
    # Log to bulletin board and audit trail
    try:
        create_trustee_share_entry(
            election_id=election_id,
            trustee_id=payload.trustee_id,
            share_count=share_count
        )
        
        audit_trustee_share_submitted(
            db=db,
            election_id=election_id,
            trustee_id=payload.trustee_id,
            share_count=share_count
        )
    except Exception as e:
        logger.error(f"Failed to create trustee share logs: {e}")
    
    return {
        "trustee_id": payload.trustee_id,
        "election_id": election_id,
        "shares_count": share_count,
        "message": "Decryption shares submitted successfully"
    }

@router.get("/election/{election_id}/decryption-status")
def get_decryption_status(election_id: str, db: Session = Depends(get_db)):
    """Check if enough trustees have submitted decryption shares"""
    
    election = db.execute(
        text("""
        SELECT threshold_t, total_trustees_n 
        FROM elections 
        WHERE election_id = CAST(:eid AS uuid)
        """),
        {"eid": election_id}
    ).fetchone()
    
    if not election:
        raise HTTPException(status_code=404, detail="Election not found")
    
    threshold = election[0]
    
    # Count trustees who submitted shares
    submitted_count = db.execute(
        text("""
        SELECT COUNT(*) 
        FROM trustees 
        WHERE election_id = CAST(:eid AS uuid) AND shares_submitted = true
        """),
        {"eid": election_id}
    ).scalar()
    
    can_decrypt = submitted_count >= threshold
    
    return {
        "election_id": election_id,
        "threshold": threshold,
        "total_trustees": election[1],
        "trustees_submitted": submitted_count,
        "can_decrypt": can_decrypt,
        "trustees_needed": max(0, threshold - submitted_count)
    }

@router.get("/election/{election_id}/ballots")
def get_election_ballots(election_id: str, db: Session = Depends(get_db)):
    """Get all ballots for an election (for trustees to verify before decryption)"""
    
    # Verify election exists
    election = db.execute(
        text("""
        SELECT election_id, status 
        FROM elections 
        WHERE election_id = CAST(:eid AS uuid)
        """),
        {"eid": election_id}
    ).fetchone()
    
    if not election:
        raise HTTPException(status_code=404, detail="Election not found")
    
    # Get all ballots
    ballots = db.execute(
        text("""
        SELECT ballot_id, encrypted_ballot, ballot_hash
        FROM ballots 
        WHERE election_id = CAST(:eid AS uuid)
        ORDER BY ballot_id
        """),
        {"eid": election_id}
    ).fetchall()
    
    return {
        "election_id": election_id,
        "status": election[1],
        "ballot_count": len(ballots),
        "ballots": [
            {
                "ballot_id": str(row[0]),
                "encrypted_ballot": row[1],  # Add encrypted ballot data
                "ballot_hash": row[2]
            }
            for row in ballots
        ]
    }

@router.delete("/{trustee_id}")
def remove_trustee(trustee_id: str, db: Session = Depends(get_db)):
    """Remove a trustee (only if key ceremony not started)"""
    
    trustee = db.execute(
        text("""
        SELECT trustee_id, election_id, public_key_share
        FROM trustees 
        WHERE trustee_id = CAST(:tid AS uuid)
        """),
        {"tid": trustee_id}
    ).fetchone()
    
    if not trustee:
        raise HTTPException(status_code=404, detail="Trustee not found")
    
    if trustee[2]:  # has key share (index 2 now, not 3)
        raise HTTPException(
            status_code=400,
            detail="Cannot remove trustee after key ceremony. Keys have been distributed."
        )
    
    db.execute(
        text("DELETE FROM trustees WHERE trustee_id = CAST(:tid AS uuid)"),
        {"tid": trustee_id}
    )
    db.commit()
    
    return {
        "trustee_id": trustee_id,
        "election_id": str(trustee[1]),
        "message": "Trustee removed successfully"
    }
