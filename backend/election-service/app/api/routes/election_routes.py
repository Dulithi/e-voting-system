from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from shared.database import get_db
from datetime import datetime

router = APIRouter()

class ElectionCreate(BaseModel):
    title: str
    description: str | None = None
    start_time: str  # ISO format
    end_time: str
    threshold_t: int = 5
    total_trustees_n: int = 9

@router.post("/create")
def create_election(payload: ElectionCreate, db: Session = Depends(get_db)):
    # MVP admin user stub (use first admin or create if needed)
    admin = db.execute("SELECT user_id FROM users WHERE is_admin = true LIMIT 1").fetchone()
    if not admin:
        # Create default admin
        admin_row = db.execute(
            """
            INSERT INTO users (nic, email, full_name, date_of_birth, is_admin, kyc_status, password_hash)
            VALUES ('ADMIN001', 'admin@securevote.com', 'Admin', '1990-01-01', true, 'APPROVED', 'stub')
            RETURNING user_id
            """
        ).fetchone()
        admin_id = admin_row[0]
    else:
        admin_id = admin[0]
    
    row = db.execute(
        """
        INSERT INTO elections (title, description, start_time, end_time, threshold_t, total_trustees_n, status, created_by)
        VALUES (:title, :desc, :start, :end, :t, :n, 'DRAFT', :admin)
        RETURNING election_id, title
        """,
        {
            "title": payload.title,
            "desc": payload.description,
            "start": payload.start_time,
            "end": payload.end_time,
            "t": payload.threshold_t,
            "n": payload.total_trustees_n,
            "admin": admin_id
        }
    ).fetchone()
    db.commit()
    return {"election_id": str(row[0]), "title": row[1]}

class CandidateAdd(BaseModel):
    election_id: str
    name: str
    party: str | None = None
    description: str | None = None
    display_order: int

@router.post("/candidate/add")
def add_candidate(payload: CandidateAdd, db: Session = Depends(get_db)):
    import secrets
    m_value = secrets.token_bytes(32)  # Placeholder for ElGamal point
    
    row = db.execute(
        """
        INSERT INTO candidates (election_id, name, party, description, display_order, m_value)
        VALUES (:eid, :name, :party, :desc, :order, :m)
        RETURNING candidate_id
        """,
        {
            "eid": payload.election_id,
            "name": payload.name,
            "party": payload.party,
            "desc": payload.description,
            "order": payload.display_order,
            "m": m_value
        }
    ).fetchone()
    db.commit()
    return {"candidate_id": str(row[0])}

@router.get("/{election_id}")
def get_election(election_id: str, db: Session = Depends(get_db)):
    row = db.execute(
        "SELECT election_id, title, description, start_time, end_time, status, threshold_t, total_trustees_n FROM elections WHERE election_id::text = :eid",
        {"eid": election_id}
    ).fetchone()
    if not row:
        return {"error": "Not found"}
    
    candidates = db.execute(
        "SELECT candidate_id, name, party, display_order FROM candidates WHERE election_id::text = :eid ORDER BY display_order",
        {"eid": election_id}
    ).fetchall()
    
    return {
        "election_id": str(row[0]),
        "title": row[1],
        "description": row[2],
        "start_time": row[3].isoformat() if row[3] else None,
        "end_time": row[4].isoformat() if row[4] else None,
        "status": row[5],
        "threshold_t": row[6],
        "total_trustees_n": row[7],
        "candidates": [
            {"candidate_id": str(c[0]), "name": c[1], "party": c[2], "display_order": c[3]}
            for c in candidates
        ]
    }

@router.get("/list")
def list_elections(db: Session = Depends(get_db)):
    rows = db.execute(
        "SELECT election_id, title, status, start_time, end_time FROM elections ORDER BY created_at DESC"
    ).fetchall()
    return [
        {
            "election_id": str(r[0]),
            "title": r[1],
            "status": r[2],
            "start_time": r[3].isoformat() if r[3] else None,
            "end_time": r[4].isoformat() if r[4] else None
        }
        for r in rows
    ]
