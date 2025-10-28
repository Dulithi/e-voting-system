"""
Helper functions for bulletin board integration
"""
import requests
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

BULLETIN_SERVICE_URL = "http://localhost:8004/api/bulletin"


def post_bulletin_entry(
    election_id: str,
    entry_type: str,
    entry_data: Dict[str, Any],
    timeout: int = 5
) -> Optional[Dict[str, Any]]:
    """
    Post an entry to the bulletin board service.
    
    Args:
        election_id: UUID of the election
        entry_type: Type of entry (ELECTION_CREATED, BALLOT_CAST, etc.)
        entry_data: Dictionary containing event-specific data
        timeout: Request timeout in seconds
        
    Returns:
        Response from bulletin board service or None if failed
    """
    try:
        payload = {
            "election_id": election_id,
            "entry_type": entry_type,
            "entry_data": entry_data
        }
        
        response = requests.post(
            f"{BULLETIN_SERVICE_URL}/append",
            json=payload,
            timeout=timeout
        )
        
        if response.status_code == 200:
            logger.info(f"Bulletin board entry created: {entry_type} for election {election_id}")
            return response.json()
        else:
            logger.error(f"Failed to create bulletin entry: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error posting to bulletin board: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error posting to bulletin board: {e}")
        return None


def create_election_created_entry(election_id: str, election_title: str, threshold: int, total_trustees: int):
    """Create bulletin board entry for election creation."""
    return post_bulletin_entry(
        election_id=election_id,
        entry_type="ELECTION_CREATED",
        entry_data={
            "election_title": election_title,
            "threshold": threshold,
            "total_trustees": total_trustees,
            "action": "Election initialized"
        }
    )


def create_key_generated_entry(election_id: str, public_key: str, threshold: int, participants: int):
    """Create bulletin board entry for key ceremony."""
    return post_bulletin_entry(
        election_id=election_id,
        entry_type="KEY_GENERATED",
        entry_data={
            "public_key": public_key[:64] + "...",  # Truncate for readability
            "threshold": threshold,
            "participants": participants,
            "action": "Election public key generated"
        }
    )


def create_ballot_cast_entry(election_id: str, ballot_hash: str, timestamp: str):
    """Create bulletin board entry for vote cast."""
    return post_bulletin_entry(
        election_id=election_id,
        entry_type="BALLOT_CAST",
        entry_data={
            "ballot_hash": ballot_hash,
            "timestamp": timestamp,
            "action": "Ballot cast and recorded"
        }
    )


def create_election_closed_entry(election_id: str, total_votes: int, close_time: str):
    """Create bulletin board entry for election closure."""
    return post_bulletin_entry(
        election_id=election_id,
        entry_type="ELECTION_CLOSED",
        entry_data={
            "total_votes": total_votes,
            "close_time": close_time,
            "action": "Voting period ended"
        }
    )


def create_trustee_share_entry(election_id: str, trustee_id: str, share_count: int):
    """Create bulletin board entry for trustee decryption share."""
    return post_bulletin_entry(
        election_id=election_id,
        entry_type="TRUSTEE_SHARE",
        entry_data={
            "trustee_id": trustee_id,
            "share_count": share_count,
            "action": "Trustee decryption share submitted"
        }
    )


def create_result_published_entry(election_id: str, total_votes: int, winner: Optional[str] = None):
    """Create bulletin board entry for results publication."""
    entry_data = {
        "total_votes": total_votes,
        "action": "Election results published"
    }
    if winner:
        entry_data["winner"] = winner
        
    return post_bulletin_entry(
        election_id=election_id,
        entry_type="RESULT_PUBLISHED",
        entry_data=entry_data
    )
