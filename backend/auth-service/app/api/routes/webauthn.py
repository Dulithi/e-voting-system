"""
WebAuthn endpoints (MVP stubs)
- registration options
- registration verification
- authentication options
- authentication verification
Note: For MVP, we return static challenges and skip full ceremony.
"""
from fastapi import APIRouter
from pydantic import BaseModel
import os

router = APIRouter()


class ChallengeResponse(BaseModel):
    challenge: str
    rp_id: str
    rp_name: str


@router.get("/register/options", response_model=ChallengeResponse)
def registration_options():
    return ChallengeResponse(
        challenge=os.urandom(16).hex(),
        rp_id="localhost",
        rp_name="SecureVote E-Voting System"
    )


class VerifyRequest(BaseModel):
    client_data_json: str
    attestation_object: str | None = None
    authenticator_data: str | None = None
    signature: str | None = None
    raw_id: str | None = None


@router.post("/register/verify")
def registration_verify(_: VerifyRequest):
    # TODO: Implement full WebAuthn verification
    return {"status": "ok"}


@router.get("/authenticate/options", response_model=ChallengeResponse)
def authentication_options():
    return ChallengeResponse(
        challenge=os.urandom(16).hex(),
        rp_id="localhost",
        rp_name="SecureVote E-Voting System"
    )


@router.post("/authenticate/verify")
def authentication_verify(_: VerifyRequest):
    # TODO: Implement full WebAuthn assertion verification
    return {"status": "ok"}
