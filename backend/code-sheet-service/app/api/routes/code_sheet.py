from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
from shared.database import get_db
from shared.audit_helper import audit_voting_codes_generated
from typing import List, Optional
import secrets
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class GenerateRequest(BaseModel):
    election_id: str
    user_id: str

class BulkGenerateRequest(BaseModel):
    election_id: str

class CodeResponse(BaseModel):
    code_id: str
    user_id: str
    user_email: str
    user_name: str
    main_voting_code: str
    candidate_codes: dict
    code_sheet_generated: bool
    main_code_used: bool
    created_at: str

class BulkGenerateResponse(BaseModel):
    election_id: str
    total_voters: int
    codes_generated: int
    codes: List[CodeResponse]

@router.post("/generate")
def generate_codes(payload: GenerateRequest, db: Session = Depends(get_db)):
    """Generate voting codes for a single user"""
    # Generate main code and candidate codes
    main_code = secrets.token_hex(16)
    
    # Fetch candidates
    candidates = db.execute(
        text("SELECT candidate_id FROM candidates WHERE election_id::text = :eid ORDER BY display_order"),
        {"eid": payload.election_id}
    ).fetchall()
    if not candidates:
        raise HTTPException(status_code=400, detail="No candidates configured")

    candidate_codes = {str(c[0]): secrets.token_hex(4) for c in candidates}

    row = db.execute(
        text("""
        INSERT INTO voting_codes (user_id, election_id, main_voting_code, candidate_codes, encrypted_code_sheet, code_sheet_generated)
        VALUES (CAST(:uid AS uuid), CAST(:eid AS uuid), :main, CAST(:cc AS jsonb), :enc, true)
        ON CONFLICT (user_id, election_id) DO UPDATE 
        SET main_voting_code = EXCLUDED.main_voting_code, 
            candidate_codes = EXCLUDED.candidate_codes, 
            code_sheet_generated = true
        RETURNING code_id
        """),
        {
            "uid": payload.user_id,
            "eid": payload.election_id,
            "main": main_code,
            "cc": json.dumps(candidate_codes),
            "enc": b"mvp"
        }
    ).fetchone()
    db.commit()

    return {"code_id": str(row[0]), "main_voting_code": main_code, "candidate_codes": candidate_codes}

@router.post("/generate-bulk", response_model=BulkGenerateResponse)
def generate_codes_bulk(payload: BulkGenerateRequest, db: Session = Depends(get_db)):
    """Generate voting codes for all eligible voters in an election"""
    
    print(f"[CODE-SHEET] Generating codes for election: {payload.election_id}")
    
    # Verify election exists
    election = db.execute(
        text("SELECT election_id, title FROM elections WHERE election_id::text = :eid"),
        {"eid": payload.election_id}
    ).fetchone()
    
    if not election:
        raise HTTPException(status_code=404, detail="Election not found")
    
    # Fetch candidates
    candidates = db.execute(
        text("SELECT candidate_id FROM candidates WHERE election_id::text = :eid ORDER BY display_order"),
        {"eid": payload.election_id}
    ).fetchall()
    
    if not candidates:
        raise HTTPException(status_code=400, detail="No candidates configured for this election")
    
    # Fetch all eligible voters (KYC approved)
    voters = db.execute(
        text("""
        SELECT user_id, email, full_name 
        FROM users 
        WHERE kyc_status = 'APPROVED' AND is_active = true AND is_admin = false
        ORDER BY email
        """)
    ).fetchall()
    
    if not voters:
        raise HTTPException(status_code=400, detail="No eligible voters found")
    
    print(f"[CODE-SHEET] Found {len(voters)} eligible voters and {len(candidates)} candidates")
    
    codes_generated = []
    
    for voter in voters:
        # Check if code already exists
        existing = db.execute(
            text("""
            SELECT code_id FROM voting_codes 
            WHERE user_id = CAST(:uid AS uuid) AND election_id = CAST(:eid AS uuid)
            """),
            {"uid": str(voter[0]), "eid": payload.election_id}
        ).fetchone()
        
        if existing:
            print(f"[CODE-SHEET] Skipping {voter[1]}: codes already exist")
            continue
        
        # Generate codes
        main_code = secrets.token_hex(16)
        candidate_codes = {str(c[0]): secrets.token_hex(4) for c in candidates}
        
        # Insert voting codes
        result = db.execute(
            text("""
            INSERT INTO voting_codes (user_id, election_id, main_voting_code, candidate_codes, encrypted_code_sheet, code_sheet_generated)
            VALUES (CAST(:uid AS uuid), CAST(:eid AS uuid), :main, CAST(:cc AS jsonb), :enc, true)
            RETURNING code_id, created_at
            """),
            {
                "uid": str(voter[0]),
                "eid": payload.election_id,
                "main": main_code,
                "cc": json.dumps(candidate_codes),
                "enc": b"mvp"
            }
        ).fetchone()
        
        codes_generated.append({
            "code_id": str(result[0]),
            "user_id": str(voter[0]),
            "user_email": voter[1],
            "user_name": voter[2],
            "main_voting_code": main_code,
            "candidate_codes": candidate_codes,
            "code_sheet_generated": True,
            "main_code_used": False,
            "created_at": str(result[1])
        })
    
    db.commit()
    
    print(f"[CODE-SHEET] Generated {len(codes_generated)} new code sheets")
    
    # Log to audit trail
    if codes_generated:
        try:
            # Get admin user
            admin_user = db.execute(
                text("SELECT user_id FROM users WHERE is_admin = true LIMIT 1")
            ).fetchone()
            admin_id = str(admin_user[0]) if admin_user else None
            
            audit_voting_codes_generated(
                db=db,
                election_id=payload.election_id,
                admin_id=admin_id,
                codes_count=len(codes_generated)
            )
        except Exception as e:
            logger.error(f"Failed to create voting codes audit log: {e}")
    
    # Fetch all codes for this election
    all_codes = db.execute(
        text("""
        SELECT 
            vc.code_id, vc.user_id, u.email, u.full_name, 
            vc.main_voting_code, vc.candidate_codes, 
            vc.code_sheet_generated, vc.main_code_used, vc.created_at
        FROM voting_codes vc
        JOIN users u ON vc.user_id = u.user_id
        WHERE vc.election_id = CAST(:eid AS uuid)
        ORDER BY u.email
        """),
        {"eid": payload.election_id}
    ).fetchall()
    
    all_codes_response = [
        CodeResponse(
            code_id=str(row[0]),
            user_id=str(row[1]),
            user_email=row[2],
            user_name=row[3],
            main_voting_code=row[4],
            candidate_codes=row[5],
            code_sheet_generated=row[6],
            main_code_used=row[7],
            created_at=str(row[8])
        )
        for row in all_codes
    ]
    
    return BulkGenerateResponse(
        election_id=payload.election_id,
        total_voters=len(voters),
        codes_generated=len(codes_generated),
        codes=all_codes_response
    )

@router.get("/election/{election_id}", response_model=List[CodeResponse])
def get_election_codes(election_id: str, db: Session = Depends(get_db)):
    """Get all voting codes for an election"""
    
    codes = db.execute(
        text("""
        SELECT 
            vc.code_id, vc.user_id, u.email, u.full_name, 
            vc.main_voting_code, vc.candidate_codes, 
            vc.code_sheet_generated, vc.main_code_used, vc.created_at
        FROM voting_codes vc
        JOIN users u ON vc.user_id = u.user_id
        WHERE vc.election_id = CAST(:eid AS uuid)
        ORDER BY u.email
        """),
        {"eid": election_id}
    ).fetchall()
    
    return [
        CodeResponse(
            code_id=str(row[0]),
            user_id=str(row[1]),
            user_email=row[2],
            user_name=row[3],
            main_voting_code=row[4],
            candidate_codes=row[5],
            code_sheet_generated=row[6],
            main_code_used=row[7],
            created_at=str(row[8])
        )
        for row in codes
    ]

@router.get("/user/{user_id}/election/{election_id}")
def get_user_codes(user_id: str, election_id: str, db: Session = Depends(get_db)):
    """Get voting codes for a specific user and election"""
    
    code = db.execute(
        text("""
        SELECT 
            vc.code_id, vc.main_voting_code, vc.candidate_codes, 
            vc.code_sheet_generated, vc.main_code_used, vc.created_at
        FROM voting_codes vc
        WHERE vc.user_id = CAST(:uid AS uuid) AND vc.election_id = CAST(:eid AS uuid)
        """),
        {"uid": user_id, "eid": election_id}
    ).fetchone()
    
    if not code:
        raise HTTPException(status_code=404, detail="Voting codes not found")
    
    return {
        "code_id": str(code[0]),
        "main_voting_code": code[1],
        "candidate_codes": code[2],
        "code_sheet_generated": code[3],
        "main_code_used": code[4],
        "created_at": str(code[5])
    }

@router.delete("/election/{election_id}/user/{user_id}")
def delete_user_codes(election_id: str, user_id: str, db: Session = Depends(get_db)):
    """Delete voting codes for a user (for regeneration)"""
    
    result = db.execute(
        text("""
        DELETE FROM voting_codes 
        WHERE election_id = CAST(:eid AS uuid) AND user_id = CAST(:uid AS uuid)
        RETURNING code_id
        """),
        {"eid": election_id, "uid": user_id}
    ).fetchone()
    
    if not result:
        raise HTTPException(status_code=404, detail="Voting codes not found")
    
    db.commit()
    return {"message": "Voting codes deleted successfully", "code_id": str(result[0])}
