"""
Helper functions for audit trail logging
"""
import logging
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime

logger = logging.getLogger(__name__)


def log_audit_event(
    db: Session,
    event_type: str,
    event_description: str,
    user_id: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    request_method: Optional[str] = None,
    request_path: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    severity: str = "INFO"
) -> bool:
    """
    Log an event to the audit trail.
    
    Args:
        db: Database session
        event_type: Type of event (e.g., "ELECTION_CREATED", "VOTE_CAST")
        event_description: Human-readable description
        user_id: Optional user who performed the action
        resource_type: Type of resource affected (e.g., "ELECTION", "BALLOT")
        resource_id: ID of the resource
        ip_address: Client IP address
        user_agent: Client user agent string
        request_method: HTTP method (GET, POST, etc.)
        request_path: Request path
        metadata: Additional JSON data
        severity: Log severity (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        import json
        metadata_json = json.dumps(metadata) if metadata else None
        
        db.execute(
            text("""
                INSERT INTO audit_logs (
                    event_type,
                    event_description,
                    user_id,
                    resource_type,
                    resource_id,
                    ip_address,
                    user_agent,
                    request_method,
                    request_path,
                    metadata,
                    severity,
                    created_at
                ) VALUES (
                    :event_type,
                    :event_description,
                    :user_id::uuid,
                    :resource_type,
                    :resource_id::uuid,
                    :ip_address::inet,
                    :user_agent,
                    :request_method,
                    :request_path,
                    :metadata::jsonb,
                    :severity,
                    :created_at
                )
            """),
            {
                "event_type": event_type,
                "event_description": event_description,
                "user_id": user_id,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "request_method": request_method,
                "request_path": request_path,
                "metadata": metadata_json,
                "severity": severity,
                "created_at": datetime.utcnow()
            }
        )
        db.commit()
        logger.debug(f"Audit log created: {event_type}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create audit log: {e}")
        db.rollback()
        return False


# Convenience functions for common events

def audit_election_created(db: Session, election_id: str, user_id: str, election_title: str, metadata: Dict = None):
    """Log election creation."""
    return log_audit_event(
        db=db,
        event_type="ELECTION_CREATED",
        event_description=f"Election '{election_title}' created",
        user_id=user_id,
        resource_type="ELECTION",
        resource_id=election_id,
        metadata=metadata,
        severity="INFO"
    )


def audit_election_activated(db: Session, election_id: str, user_id: str, election_title: str):
    """Log election activation."""
    return log_audit_event(
        db=db,
        event_type="ELECTION_ACTIVATED",
        event_description=f"Election '{election_title}' activated",
        user_id=user_id,
        resource_type="ELECTION",
        resource_id=election_id,
        severity="INFO"
    )


def audit_election_closed(db: Session, election_id: str, user_id: str, election_title: str, total_votes: int):
    """Log election closure."""
    return log_audit_event(
        db=db,
        event_type="ELECTION_CLOSED",
        event_description=f"Election '{election_title}' closed with {total_votes} votes",
        user_id=user_id,
        resource_type="ELECTION",
        resource_id=election_id,
        metadata={"total_votes": total_votes},
        severity="WARNING"
    )


def audit_key_ceremony(db: Session, election_id: str, trustees_count: int, threshold: int):
    """Log key ceremony completion."""
    return log_audit_event(
        db=db,
        event_type="KEY_CEREMONY_COMPLETED",
        event_description=f"Key ceremony completed with {trustees_count} trustees (threshold: {threshold})",
        resource_type="ELECTION",
        resource_id=election_id,
        metadata={"trustees": trustees_count, "threshold": threshold},
        severity="INFO"
    )


def audit_vote_cast(db: Session, ballot_id: str, election_id: str, voter_id: Optional[str] = None):
    """Log vote casting."""
    return log_audit_event(
        db=db,
        event_type="VOTE_CAST",
        event_description="Vote cast successfully",
        user_id=voter_id,
        resource_type="BALLOT",
        resource_id=ballot_id,
        metadata={"election_id": election_id},
        severity="INFO"
    )


def audit_trustee_share_submitted(db: Session, election_id: str, trustee_id: str, share_count: int):
    """Log trustee decryption share submission."""
    return log_audit_event(
        db=db,
        event_type="TRUSTEE_SHARE_SUBMITTED",
        event_description=f"Trustee submitted {share_count} decryption shares",
        user_id=trustee_id,
        resource_type="ELECTION",
        resource_id=election_id,
        metadata={"share_count": share_count},
        severity="INFO"
    )


def audit_tally_completed(db: Session, election_id: str, user_id: str, total_votes: int):
    """Log tally completion."""
    return log_audit_event(
        db=db,
        event_type="TALLY_COMPLETED",
        event_description=f"Election tallying completed with {total_votes} votes",
        user_id=user_id,
        resource_type="ELECTION",
        resource_id=election_id,
        metadata={"total_votes": total_votes},
        severity="WARNING"
    )


def audit_login(db: Session, user_id: str, ip_address: str, success: bool = True):
    """Log user login attempt."""
    return log_audit_event(
        db=db,
        event_type="USER_LOGIN" if success else "USER_LOGIN_FAILED",
        event_description="User logged in successfully" if success else "Failed login attempt",
        user_id=user_id if success else None,
        resource_type="USER",
        resource_id=user_id if success else None,
        ip_address=ip_address,
        severity="INFO" if success else "WARNING"
    )


def audit_kyc_status_change(db: Session, user_id: str, admin_id: str, new_status: str, reason: Optional[str] = None):
    """Log KYC status change."""
    return log_audit_event(
        db=db,
        event_type="KYC_STATUS_CHANGED",
        event_description=f"KYC status changed to {new_status}",
        user_id=admin_id,
        resource_type="USER",
        resource_id=user_id,
        metadata={"new_status": new_status, "reason": reason},
        severity="INFO"
    )


def audit_voting_codes_generated(db: Session, election_id: str, admin_id: str, codes_count: int):
    """Log voting codes generation."""
    return log_audit_event(
        db=db,
        event_type="VOTING_CODES_GENERATED",
        event_description=f"Generated {codes_count} voting codes",
        user_id=admin_id,
        resource_type="ELECTION",
        resource_id=election_id,
        metadata={"codes_count": codes_count},
        severity="INFO"
    )


def audit_security_event(db: Session, event_description: str, user_id: Optional[str] = None, 
                         ip_address: Optional[str] = None, metadata: Optional[Dict] = None):
    """Log security-related events."""
    return log_audit_event(
        db=db,
        event_type="SECURITY_EVENT",
        event_description=event_description,
        user_id=user_id,
        ip_address=ip_address,
        metadata=metadata,
        severity="CRITICAL"
    )
