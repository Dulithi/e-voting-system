from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from shared.database import get_db
from datetime import datetime
import base64

router = APIRouter()

class VoteSubmitRequest(BaseModel):
    election_id: str
    token_hash: str
    signed_token_b64: str
    encrypted_ballot_b64: str
    zkp_proof: dict
    encrypted_code_sheet_b64: str

class VoteSubmitResponse(BaseModel):
    ballot_hash: str
    verification_code: str

@router.post("/submit", response_model=VoteSubmitResponse)
def submit_vote(payload: VoteSubmitRequest, db: Session = Depends(get_db)):
    # 1) Verify token exists and not used
    token = db.execute(
        "SELECT token_id, is_used FROM anonymous_tokens WHERE token_hash = :h",
        {"h": payload.token_hash}
    ).fetchone()
    if not token:
        raise HTTPException(status_code=400, detail="Invalid token")
    if token[1]:
        raise HTTPException(status_code=400, detail="Token already used")

    # 2) TODO: Verify signature and ZKP (MVP: skip, assume valid)

    # 3) Persist ballot
    ballot_bytes = base64.b64decode(payload.encrypted_ballot_b64)
    ballot_hash = __import__('hashlib').sha256(ballot_bytes).hexdigest()

    # For MVP, generate a placeholder verification code from ballot hash prefix
    verification_code = ballot_hash[:8]

    db.execute(
        """
        INSERT INTO ballots (election_id, encrypted_ballot, zkp_proof, ballot_signature, ballot_hash, verification_code, token_hash)
        VALUES (:eid, :ballot, :zkp::jsonb, :sig, :bh, :vc, :th)
        """,
        {
            "eid": payload.election_id,
            "ballot": ballot_bytes,
            "zkp": __import__('json').dumps(payload.zkp_proof),
            "sig": base64.b64decode(payload.signed_token_b64),
            "bh": ballot_hash,
            "vc": verification_code,
            "th": payload.token_hash
        }
    )

    # 4) Mark token as used
    db.execute(
        "UPDATE anonymous_tokens SET is_used = true, used_at = now() WHERE token_hash = :h",
        {"h": payload.token_hash}
    )

    # 5) TODO: Append to bulletin board

    db.commit()

    return VoteSubmitResponse(ballot_hash=ballot_hash, verification_code=verification_code)
