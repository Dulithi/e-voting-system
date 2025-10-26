from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from shared.database import get_db
import secrets
import json

router = APIRouter()

class GenerateRequest(BaseModel):
    election_id: str
    user_id: str

@router.post("/generate")
def generate_codes(payload: GenerateRequest, db: Session = Depends(get_db)):
    # Generate main code and candidate codes
    main_code = secrets.token_hex(16)
    # Fetch candidates
    candidates = db.execute(
        "SELECT candidate_id FROM candidates WHERE election_id::text = :eid ORDER BY display_order",
        {"eid": payload.election_id}
    ).fetchall()
    if not candidates:
        raise HTTPException(status_code=400, detail="No candidates configured")

    candidate_codes = {str(c[0]): secrets.token_hex(4) for c in candidates}

    row = db.execute(
        """
        INSERT INTO voting_codes (user_id, election_id, main_voting_code, candidate_codes, encrypted_code_sheet, code_sheet_generated)
        VALUES (:uid, :eid, :main, :cc::jsonb, :enc, true)
        ON CONFLICT (user_id, election_id) DO UPDATE SET main_voting_code = EXCLUDED.main_voting_code, candidate_codes = EXCLUDED.candidate_codes, code_sheet_generated = true
        RETURNING code_id
        """,
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
