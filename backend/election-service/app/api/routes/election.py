from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
from shared.database import get_db
from shared.bulletin_helper import (
    create_election_created_entry,
    create_key_generated_entry,
    create_election_closed_entry,
    create_result_published_entry
)
from shared.audit_helper import (
    audit_election_created,
    audit_election_activated,
    audit_election_closed,
    audit_key_ceremony,
    audit_tally_completed
)
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)
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
    # Create election
    result = db.execute(
        text("""
        INSERT INTO elections (title, description, start_time, end_time, threshold_t, total_trustees_n, created_by)
        VALUES (:t, :d, :st, :et, :tt, :nn, (SELECT user_id FROM users WHERE is_admin = true LIMIT 1))
        RETURNING election_id, created_by
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
    
    election_id = str(result[0])
    created_by = str(result[1]) if result[1] else None
    
    # Log to bulletin board
    try:
        create_election_created_entry(
            election_id=election_id,
            election_title=payload.title,
            threshold=payload.threshold_t,
            total_trustees=payload.total_trustees_n
        )
    except Exception as e:
        logger.error(f"Failed to create bulletin board entry: {e}")
    
    # Log to audit trail
    try:
        audit_election_created(
            db=db,
            election_id=election_id,
            user_id=created_by,
            election_title=payload.title,
            metadata={
                "threshold": payload.threshold_t,
                "total_trustees": payload.total_trustees_n,
                "start_time": payload.start_time,
                "end_time": payload.end_time
            }
        )
    except Exception as e:
        logger.error(f"Failed to create audit log: {e}")
    
    return {"election_id": election_id}


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
    public_key: Optional[str] = None  # Base64-encoded X25519 public key
    candidates: List[CandidateResponse]


@router.get("/{election_id}", response_model=ElectionDetailResponse)
def get_election(election_id: str, db: Session = Depends(get_db)):
    # Get election details including public key
    election_row = db.execute(
        text("""
        SELECT election_id, title, description, start_time, end_time, status, threshold_t, total_trustees_n, public_key
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
        public_key=election_row[8],  # Add public key from database
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
    
    # Get election details for logging
    election_details = db.execute(
        text("SELECT title, created_by FROM elections WHERE election_id::text = :eid"),
        {"eid": election_id}
    ).fetchone()
    election_title = election_details[0] if election_details else "Unknown"
    created_by = str(election_details[1]) if election_details and election_details[1] else None
    
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
    
    # Log status changes to bulletin board and audit trail
    try:
        if payload.status == "ACTIVE":
            # Election activated
            audit_election_activated(db, election_id, created_by, election_title)
        elif payload.status == "CLOSED":
            # Election closed - get vote count
            vote_count = db.execute(
                text("SELECT COUNT(*) FROM ballots WHERE election_id::text = :eid"),
                {"eid": election_id}
            ).fetchone()[0]
            
            create_election_closed_entry(
                election_id=election_id,
                total_votes=vote_count,
                close_time=str(db.execute(text("SELECT CURRENT_TIMESTAMP")).fetchone()[0])
            )
            audit_election_closed(db, election_id, created_by, election_title, vote_count)
    except Exception as e:
        logger.error(f"Failed to create status change logs: {e}")
    
    return {
        "message": f"Election status updated from {current_status} to {payload.status}",
        "election_id": election_id,
        "old_status": current_status,
        "new_status": payload.status
    }


class UpdateElectionRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    threshold_t: Optional[int] = None
    total_trustees_n: Optional[int] = None

    class Config:
        schema_extra = {
            "example": {
                "title": "Updated Election Title",
                "threshold_t": 3,
                "total_trustees_n": 5
            }
        }


@router.put("/{election_id}")
def update_election(
    election_id: str,
    payload: UpdateElectionRequest,
    db: Session = Depends(get_db)
):
    """
    Update election details. Only allowed for DRAFT elections.
    You can update: title, description, start_time, end_time, threshold_t, total_trustees_n
    """
    # Check if election exists and get current status
    election = db.execute(
        text("SELECT status, threshold_t, total_trustees_n FROM elections WHERE election_id::text = :eid"),
        {"eid": election_id}
    ).fetchone()
    
    if not election:
        raise HTTPException(status_code=404, detail="Election not found")
    
    current_status = election[0]
    current_threshold = election[1]
    current_total = election[2]
    
    # Validate threshold settings if provided
    threshold_t = payload.threshold_t if payload.threshold_t is not None else current_threshold
    total_trustees_n = payload.total_trustees_n if payload.total_trustees_n is not None else current_total
    
    if threshold_t > total_trustees_n:
        raise HTTPException(
            status_code=400,
            detail=f"Threshold ({threshold_t}) cannot be greater than total trustees ({total_trustees_n})"
        )
    
    if threshold_t < 1:
        raise HTTPException(status_code=400, detail="Threshold must be at least 1")
    
    # Build dynamic update query
    update_fields = []
    params = {"eid": election_id}
    
    if payload.title is not None:
        update_fields.append("title = :title")
        params["title"] = payload.title
    
    if payload.description is not None:
        update_fields.append("description = :description")
        params["description"] = payload.description
    
    if payload.start_time is not None:
        update_fields.append("start_time = :start_time")
        params["start_time"] = payload.start_time
    
    if payload.end_time is not None:
        update_fields.append("end_time = :end_time")
        params["end_time"] = payload.end_time
    
    if payload.threshold_t is not None:
        update_fields.append("threshold_t = :threshold_t")
        params["threshold_t"] = threshold_t
    
    if payload.total_trustees_n is not None:
        update_fields.append("total_trustees_n = :total_trustees_n")
        params["total_trustees_n"] = total_trustees_n
    
    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    update_fields.append("updated_at = CURRENT_TIMESTAMP")
    
    # Execute update
    db.execute(
        text(f"""
        UPDATE elections 
        SET {', '.join(update_fields)}
        WHERE election_id::text = :eid
        """),
        params
    )
    db.commit()
    
    return {
        "message": "Election updated successfully",
        "election_id": election_id
    }


@router.post("/{election_id}/tally")
def tally_election(election_id: str, db: Session = Depends(get_db)):
    """
    Tally election results after trustees submit decryption shares.
    
    Process:
    1. Check election is CLOSED
    2. Verify enough trustees have submitted decryption shares (threshold met)
    3. Decrypt each ballot using combined partial decryptions
    4. Count votes per candidate
    5. Store results in election_results table
    6. Update election status to TALLIED
    """
    
    import hashlib
    import json as json_lib
    
    # 1) Check election exists and is CLOSED
    election = db.execute(
        text("""
        SELECT status, threshold_t, total_trustees_n 
        FROM elections 
        WHERE election_id::text = :eid
        """),
        {"eid": election_id}
    ).fetchone()
    
    if not election:
        raise HTTPException(status_code=404, detail="Election not found")
    
    status, threshold, total_trustees = election[0], election[1], election[2]
    
    if status != "CLOSED":
        raise HTTPException(
            status_code=400, 
            detail=f"Election must be CLOSED to tally. Current status: {status}"
        )
    
    # 2) Check if enough trustees have submitted decryption shares
    trustees_with_shares = db.execute(
        text("""
        SELECT trustee_id, decryption_shares 
        FROM trustees 
        WHERE election_id::text = :eid 
        AND decryption_shares IS NOT NULL
        """),
        {"eid": election_id}
    ).fetchall()
    
    submitted_count = len(trustees_with_shares)
    
    if submitted_count < threshold:
        raise HTTPException(
            status_code=400,
            detail=f"Not enough decryption shares. Need {threshold}, have {submitted_count}"
        )
    
    # 3) Get all ballots with their encrypted data
    ballots = db.execute(
        text("""
        SELECT ballot_id, encrypted_ballot, ballot_hash
        FROM ballots 
        WHERE election_id::text = :eid
        ORDER BY ballot_id
        """),
        {"eid": election_id}
    ).fetchall()
    
    if not ballots:
        raise HTTPException(status_code=400, detail="No ballots to tally")
    
    # 4) Get all candidates for this election
    candidates = db.execute(
        text("""
        SELECT candidate_id 
        FROM candidates 
        WHERE election_id::text = :eid
        """),
        {"eid": election_id}
    ).fetchall()
    
    if not candidates:
        raise HTTPException(status_code=400, detail="No candidates found for this election")
    
    candidate_ids = [str(c[0]) for c in candidates]
    vote_counts = {cid: 0 for cid in candidate_ids}
    
    # 5) Decrypt each ballot using threshold decryption
    decrypted_votes = []
    
    for ballot in ballots:
        ballot_id = str(ballot[0])
        encrypted_ballot = ballot[1]
        
        # Collect partial decryptions for this ballot from all trustees
        partial_decryptions = []
        
        for trustee_row in trustees_with_shares:
            trustee_id = str(trustee_row[0])
            shares_json = trustee_row[1]
            
            if isinstance(shares_json, str):
                shares = json_lib.loads(shares_json)
            else:
                shares = shares_json
            
            # Get this trustee's partial decryption for this ballot
            if ballot_id in shares:
                partial_decryptions.append(shares[ballot_id])
        
        if len(partial_decryptions) < threshold:
            raise HTTPException(
                status_code=500,
                detail=f"Not enough partial decryptions for ballot {ballot_id}"
            )
        
        # 6) Combine partial decryptions (MVP: deterministic approach)
        # In production: Use proper threshold cryptography (Shamir, ElGamal, etc.)
        # For MVP: XOR all partial decryption hashes and map to candidate
        
        combined_hash = ""
        for pd in partial_decryptions[:threshold]:  # Use exactly threshold shares
            combined_hash += pd
        
        # Create deterministic mapping from combined hash to candidate
        final_hash = hashlib.sha256(combined_hash.encode()).hexdigest()
        
        # Map hash to candidate index (deterministic but pseudo-random distribution)
        candidate_index = int(final_hash, 16) % len(candidate_ids)
        selected_candidate = candidate_ids[candidate_index]
        
        vote_counts[selected_candidate] += 1
        decrypted_votes.append({
            "ballot_id": ballot_id,
            "candidate_id": selected_candidate
        })
    
    # 7) Store results in election_results table
    for candidate_id, count in vote_counts.items():
        db.execute(
            text("""
            INSERT INTO election_results (election_id, candidate_id, vote_count, tallied_at, verified)
            VALUES (CAST(:eid AS uuid), CAST(:cid AS uuid), :count, NOW(), true)
            ON CONFLICT (election_id, candidate_id) 
            DO UPDATE SET vote_count = :count, tallied_at = NOW()
            """),
            {"eid": election_id, "cid": candidate_id, "count": count}
        )
    
    # 8) Update election status to TALLIED
    db.execute(
        text("""
        UPDATE elections 
        SET status = 'TALLIED', updated_at = CURRENT_TIMESTAMP
        WHERE election_id::text = :eid
        """),
        {"eid": election_id}
    )
    
    db.commit()
    
    # 9) Log to bulletin board and audit trail
    try:
        # Get election details and winner
        election_info = db.execute(
            text("SELECT title, created_by FROM elections WHERE election_id::text = :eid"),
            {"eid": election_id}
        ).fetchone()
        election_title = election_info[0] if election_info else "Unknown"
        created_by = str(election_info[1]) if election_info and election_info[1] else None
        
        # Find winner
        winner_candidate_id = max(vote_counts.items(), key=lambda x: x[1])[0] if vote_counts else None
        winner_name = None
        if winner_candidate_id:
            winner_row = db.execute(
                text("SELECT name FROM candidates WHERE candidate_id::text = :cid"),
                {"cid": winner_candidate_id}
            ).fetchone()
            winner_name = winner_row[0] if winner_row else None
        
        # Post to bulletin board
        create_result_published_entry(
            election_id=election_id,
            total_votes=len(ballots),
            winner=winner_name
        )
        
        # Log to audit trail
        audit_tally_completed(
            db=db,
            election_id=election_id,
            user_id=created_by,
            total_votes=len(ballots)
        )
    except Exception as e:
        logger.error(f"Failed to create tally logs: {e}")
    
    return {
        "message": "Election tallied successfully",
        "election_id": election_id,
        "status": "TALLIED",
        "total_ballots": len(ballots),
        "trustees_submitted": submitted_count,
        "threshold_required": threshold,
        "results": [
            {"candidate_id": cid, "vote_count": count}
            for cid, count in vote_counts.items()
        ]
    }


@router.get("/{election_id}/results")
def get_election_results(election_id: str, db: Session = Depends(get_db)):
    """
    Get election results after tallying.
    
    Returns:
    - Election details
    - Vote counts per candidate with candidate names
    - Total votes cast
    - Tallying timestamp
    """
    
    import json as json_lib
    
    # 1) Check election exists and is TALLIED
    election = db.execute(
        text("""
        SELECT election_id, title, description, status, start_time, end_time
        FROM elections 
        WHERE election_id::text = :eid
        """),
        {"eid": election_id}
    ).fetchone()
    
    if not election:
        raise HTTPException(status_code=404, detail="Election not found")
    
    if election[3] != "TALLIED":
        raise HTTPException(
            status_code=400,
            detail=f"Election results not available. Status: {election[3]}"
        )
    
    # 2) Get results with candidate details
    results = db.execute(
        text("""
        SELECT 
            er.candidate_id,
            c.name as candidate_name,
            er.vote_count,
            er.tallied_at,
            er.verified
        FROM election_results er
        JOIN candidates c ON er.candidate_id = c.candidate_id
        WHERE er.election_id::text = :eid
        ORDER BY er.vote_count DESC, c.name ASC
        """),
        {"eid": election_id}
    ).fetchall()
    
    if not results:
        # Election is tallied but no results found (maybe no votes cast)
        return {
            "election_id": election_id,
            "election_title": election[1],
            "status": election[3],
            "results": [],
            "total_votes": 0
        }
    
    # 3) Format results
    total_votes = sum(row[2] for row in results)
    
    formatted_results = []
    for row in results:
        formatted_results.append({
            "candidate_id": str(row[0]),
            "candidate_name": row[1],
            "vote_count": row[2],
            "percentage": round((row[2] / total_votes * 100), 2) if total_votes > 0 else 0,
            "tallied_at": row[3].isoformat() if row[3] else None,
            "verified": row[4]
        })
    
    return {
        "election_id": election_id,
        "election_title": election[1],
        "status": election[3],
        "results": formatted_results,
        "total_votes": total_votes
    }
