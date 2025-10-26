from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from shared.database import get_db

router = APIRouter()

class TrusteeAdd(BaseModel):
    election_id: str
    user_id: str

@router.post("/add")
def add_trustee(payload: TrusteeAdd, db: Session = Depends(get_db)):
    row = db.execute(
        """
        INSERT INTO trustees (election_id, user_id, status)
        VALUES (:eid, :uid, 'INVITED')
        RETURNING trustee_id
        """,
        {"eid": payload.election_id, "uid": payload.user_id}
    ).fetchone()
    db.commit()
    return {"trustee_id": str(row[0])}
