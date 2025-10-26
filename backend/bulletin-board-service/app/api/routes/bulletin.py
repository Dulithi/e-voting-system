from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from shared.database import get_db
import hashlib
import json

router = APIRouter()

class BulletinEntryIn(BaseModel):
    election_id: str
    entry_type: str
    entry_data: dict

class BulletinEntryOut(BaseModel):
    entry_id: str
    entry_hash: str
    previous_hash: str | None

@router.post("/append", response_model=BulletinEntryOut)
def append_entry(payload: BulletinEntryIn, db: Session = Depends(get_db)):
    # Get last entry hash
    last = db.execute(
        "SELECT entry_hash FROM bulletin_board WHERE election_id::text = :eid ORDER BY sequence_number DESC LIMIT 1",
        {"eid": payload.election_id}
    ).fetchone()
    previous_hash = last[0] if last else None

    computed_hash = hashlib.sha256(json.dumps(payload.entry_data, sort_keys=True).encode() + (previous_hash.encode() if previous_hash else b"" )).hexdigest()

    row = db.execute(
        """
        INSERT INTO bulletin_board (election_id, entry_type, entry_hash, previous_hash, entry_data, signature)
        VALUES (:eid, :etype, :eh, :ph, :edata::jsonb, :sig)
        RETURNING entry_id, entry_hash, previous_hash
        """,
        {
            "eid": payload.election_id,
            "etype": payload.entry_type,
            "eh": computed_hash,
            "ph": previous_hash,
            "edata": json.dumps(payload.entry_data),
            "sig": b"mvp"
        }
    ).fetchone()
    db.commit()

    return BulletinEntryOut(entry_id=str(row[0]), entry_hash=row[1], previous_hash=row[2])

@router.get("/{election_id}/chain")
def get_chain(election_id: str, db: Session = Depends(get_db)):
    rows = db.execute(
        "SELECT sequence_number, entry_type, entry_hash, previous_hash, entry_data, created_at FROM bulletin_board WHERE election_id::text = :eid ORDER BY sequence_number",
        {"eid": election_id}
    ).fetchall()
    return [
        {
            "seq": r[0],
            "type": r[1],
            "hash": r[2],
            "prev": r[3],
            "data": r[4],
            "time": r[5].isoformat() if r[5] else None
        }
        for r in rows
    ]
