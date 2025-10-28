from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
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
    """
    Append a new entry to the bulletin board.
    Creates a tamper-evident chain of events for the election.
    """
    # Get last entry hash for this election
    last = db.execute(
        text("""
        SELECT entry_hash FROM bulletin_board 
        WHERE election_id::text = :eid 
        ORDER BY sequence_number DESC LIMIT 1
        """),
        {"eid": payload.election_id}
    ).fetchone()
    previous_hash = last[0] if last else None

    # Compute hash: hash(entry_data + previous_hash)
    data_str = json.dumps(payload.entry_data, sort_keys=True)
    hash_input = data_str.encode() + (previous_hash.encode() if previous_hash else b"")
    computed_hash = hashlib.sha256(hash_input).hexdigest()

    # Insert into bulletin board
    row = db.execute(
        text("""
        INSERT INTO bulletin_board (
            election_id, 
            entry_type, 
            entry_hash, 
            previous_hash, 
            entry_data, 
            signature
        )
        VALUES (
            CAST(:eid AS uuid), 
            :etype, 
            :eh, 
            :ph, 
            CAST(:edata AS jsonb), 
            :sig
        )
        RETURNING entry_id, entry_hash, previous_hash
        """),
        {
            "eid": payload.election_id,
            "etype": payload.entry_type,
            "eh": computed_hash,
            "ph": previous_hash,
            "edata": data_str,
            "sig": b"mvp_signature"  # MVP: simplified signature
        }
    ).fetchone()
    db.commit()

    return BulletinEntryOut(
        entry_id=str(row[0]), 
        entry_hash=row[1], 
        previous_hash=row[2]
    )

@router.get("/{election_id}/chain")
def get_chain(election_id: str, db: Session = Depends(get_db)):
    """
    Get the complete bulletin board chain for an election.
    Returns all entries in chronological order.
    """
    rows = db.execute(
        text("""
        SELECT 
            sequence_number, 
            entry_type, 
            entry_hash, 
            previous_hash, 
            entry_data, 
            created_at 
        FROM bulletin_board 
        WHERE election_id::text = :eid 
        ORDER BY sequence_number
        """),
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

@router.get("/{election_id}/verify")
def verify_chain(election_id: str, db: Session = Depends(get_db)):
    """
    Verify the integrity of the bulletin board chain.
    Checks that each entry's hash correctly links to the previous entry.
    """
    rows = db.execute(
        text("""
        SELECT 
            entry_hash, 
            previous_hash, 
            entry_data 
        FROM bulletin_board 
        WHERE election_id::text = :eid 
        ORDER BY sequence_number
        """),
        {"eid": election_id}
    ).fetchall()
    
    if not rows:
        return {"valid": True, "message": "No entries to verify"}
    
    # Verify each entry's hash
    for i, row in enumerate(rows):
        entry_hash = row[0]
        previous_hash = row[1]
        entry_data = row[2]
        
        # Check previous hash link
        if i > 0:
            expected_prev = rows[i - 1][0]
            if previous_hash != expected_prev:
                return {
                    "valid": False,
                    "message": f"Chain broken at entry {i}: prev hash mismatch"
                }
        
        # Recompute hash to verify integrity
        data_str = json.dumps(entry_data, sort_keys=True)
        hash_input = data_str.encode() + (previous_hash.encode() if previous_hash else b"")
        computed_hash = hashlib.sha256(hash_input).hexdigest()
        
        if computed_hash != entry_hash:
            return {
                "valid": False,
                "message": f"Hash mismatch at entry {i}: data may have been tampered"
            }
    
    return {
        "valid": True,
        "message": f"All {len(rows)} entries verified successfully",
        "total_entries": len(rows)
    }

@router.get("/{election_id}/summary")
def get_summary(election_id: str, db: Session = Depends(get_db)):
    """
    Get a summary of bulletin board entries by type.
    """
    rows = db.execute(
        text("""
        SELECT 
            entry_type, 
            COUNT(*) as count,
            MIN(created_at) as first_entry,
            MAX(created_at) as last_entry
        FROM bulletin_board 
        WHERE election_id::text = :eid 
        GROUP BY entry_type
        ORDER BY MAX(sequence_number)
        """),
        {"eid": election_id}
    ).fetchall()
    
    total = db.execute(
        text("""
        SELECT COUNT(*) 
        FROM bulletin_board 
        WHERE election_id::text = :eid
        """),
        {"eid": election_id}
    ).fetchone()[0]
    
    return {
        "election_id": election_id,
        "total_entries": total,
        "entries_by_type": [
            {
                "type": r[0],
                "count": r[1],
                "first_entry": r[2].isoformat() if r[2] else None,
                "last_entry": r[3].isoformat() if r[3] else None
            }
            for r in rows
        ]
    }
