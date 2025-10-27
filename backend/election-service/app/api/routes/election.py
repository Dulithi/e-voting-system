from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
from shared.database import get_db
from typing import List, Optional

router = APIRouter()

class ElectionCreate(BaseModel):
    title: str
    description: str | None = None
    start_time: str
    end_time: str
    threshold_t: int = 5
    total_trustees_n: int = 9

@router.post("/create")
def create_election(payload: ElectionCreate, db: Session = Depends(get_db)):
    row = db.execute(
        text("""
        INSERT INTO elections (title, description, start_time, end_time, threshold_t, total_trustees_n, created_by)
        VALUES (:t, :d, :st, :et, :tt, :nn, (SELECT user_id FROM users WHERE is_admin = true LIMIT 1))
        RETURNING election_id
        """),
        {
            "t": payload.title,
            "d": payload.description,
            "st": payload.start_time,
            "et": payload.end_time,
            "tt": payload.threshold_t,
            "nn": payload.total_trustees_n
        }
    ).fetchone()
    db.commit()
    return {"election_id": str(row[0])}


class ElectionResponse(BaseModel):
    election_id: str
    title: str
    description: str | None
    start_time: str
    end_time: str
    status: str
    threshold_t: int
    total_trustees_n: int


@router.get("/list", response_model=List[ElectionResponse])
def list_elections(db: Session = Depends(get_db)):
    rows = db.execute(
        text("""
        SELECT election_id, title, description, start_time, end_time, status, threshold_t, total_trustees_n
        FROM elections
        ORDER BY created_at DESC
        """)
    ).fetchall()
    
    return [
        ElectionResponse(
            election_id=str(row[0]),
            title=row[1],
            description=row[2],
            start_time=str(row[3]),
            end_time=str(row[4]),
            status=row[5],
            threshold_t=row[6],
            total_trustees_n=row[7]
        )
        for row in rows
    ]


class CandidateResponse(BaseModel):
    candidate_id: str
    name: str
    party: Optional[str]
    display_order: int


class ElectionDetailResponse(BaseModel):
    election_id: str
    title: str
    description: Optional[str]
    start_time: str
    end_time: str
    status: str
    threshold_t: int
    total_trustees_n: int
    candidates: List[CandidateResponse]


@router.get("/{election_id}", response_model=ElectionDetailResponse)
def get_election(election_id: str, db: Session = Depends(get_db)):
    # Get election details
    election_row = db.execute(
        text("""
        SELECT election_id, title, description, start_time, end_time, status, threshold_t, total_trustees_n
        FROM elections
        WHERE election_id::text = :eid
        """),
        {"eid": election_id}
    ).fetchone()
    
    if not election_row:
        raise HTTPException(status_code=404, detail="Election not found")
    
    # Get candidates for this election
    candidate_rows = db.execute(
        text("""
        SELECT candidate_id, name, party, display_order
        FROM candidates
        WHERE election_id::text = :eid
        ORDER BY display_order
        """),
        {"eid": election_id}
    ).fetchall()
    
    candidates = [
        CandidateResponse(
            candidate_id=str(row[0]),
            name=row[1],
            party=row[2],
            display_order=row[3]
        )
        for row in candidate_rows
    ]
    
    return ElectionDetailResponse(
        election_id=str(election_row[0]),
        title=election_row[1],
        description=election_row[2],
        start_time=str(election_row[3]),
        end_time=str(election_row[4]),
        status=election_row[5],
        threshold_t=election_row[6],
        total_trustees_n=election_row[7],
        candidates=candidates
    )


class CandidateCreate(BaseModel):
    election_id: str
    name: str
    party: str | None = None

@router.post("/candidate/add")
def add_candidate(payload: CandidateCreate, db: Session = Depends(get_db)):
    # Get the next display_order for this election
    max_order = db.execute(
        text("""
        SELECT COALESCE(MAX(display_order), 0) + 1
        FROM candidates
        WHERE election_id::text = :eid
        """),
        {"eid": payload.election_id}
    ).fetchone()[0]
    
    row = db.execute(
        text("""
        INSERT INTO candidates (election_id, name, party, m_value, display_order)
        VALUES (:eid, :name, :party, '\\x01'::bytea, :ord)
        RETURNING candidate_id
        """),
        {
            "eid": payload.election_id,
            "name": payload.name,
            "party": payload.party,
            "ord": max_order
        }
    ).fetchone()
    db.commit()
    return {"candidate_id": str(row[0])}


class DashboardStats(BaseModel):
    total_elections: int
    active_elections: int
    total_voters: int
    pending_kyc: int


@router.get("/stats/dashboard", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    # Get total elections
    total_elections = db.execute(
        text("SELECT COUNT(*) FROM elections")
    ).fetchone()[0]
    
    # Get active elections
    active_elections = db.execute(
        text("SELECT COUNT(*) FROM elections WHERE status = 'ACTIVE'")
    ).fetchone()[0]
    
    # Get total voters (non-admin users)
    total_voters = db.execute(
        text("SELECT COUNT(*) FROM users WHERE is_admin = false")
    ).fetchone()[0]
    
    # Get pending KYC
    pending_kyc = db.execute(
        text("SELECT COUNT(*) FROM users WHERE kyc_status = 'PENDING'")
    ).fetchone()[0]
    
    return DashboardStats(
        total_elections=total_elections,
        active_elections=active_elections,
        total_voters=total_voters,
        pending_kyc=pending_kyc
    )


class UpdateStatusRequest(BaseModel):
    status: str

    class Config:
        # Validate status values
        schema_extra = {
            "example": {
                "status": "ACTIVE"
            }
        }


@router.put("/{election_id}/status")
def update_election_status(
    election_id: str, 
    payload: UpdateStatusRequest, 
    db: Session = Depends(get_db)
):
    """
    Update election status.
    
    Valid statuses:
    - DRAFT: Election is being prepared (can edit candidates, details)
    - ACTIVE: Election is open for voting (cannot edit)
    - CLOSED: Election has ended, waiting for tallying
    - TALLIED: Results have been calculated and published
    
    Status transitions:
    - DRAFT → ACTIVE (start election)
    - ACTIVE → CLOSED (end election)
    - CLOSED → TALLIED (publish results)
    - Any → DRAFT (reset/reopen for editing - use with caution)
    """
    # Validate status
    valid_statuses = ['DRAFT', 'ACTIVE', 'CLOSED', 'TALLIED']
    if payload.status not in valid_statuses:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    # Check if election exists
    election = db.execute(
        text("SELECT status FROM elections WHERE election_id::text = :eid"),
        {"eid": election_id}
    ).fetchone()
    
    if not election:
        raise HTTPException(status_code=404, detail="Election not found")
    
    current_status = election[0]
    
    # Update status
    db.execute(
        text("""
        UPDATE elections 
        SET status = :status, updated_at = CURRENT_TIMESTAMP 
        WHERE election_id::text = :eid
        """),
        {"status": payload.status, "eid": election_id}
    )
    db.commit()
    
    return {
        "message": f"Election status updated from {current_status} to {payload.status}",
        "election_id": election_id,
        "old_status": current_status,
        "new_status": payload.status
    }
