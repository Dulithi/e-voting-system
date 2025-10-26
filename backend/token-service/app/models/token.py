from sqlalchemy import Column, String, Boolean, DateTime, LargeBinary
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from shared.database import Base

class AnonymousToken(Base):
    __tablename__ = "anonymous_tokens"

    token_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    election_id = Column(UUID(as_uuid=True), nullable=False)
    token_hash = Column(String(64), unique=True, nullable=False)
    signed_blind_token = Column(LargeBinary, nullable=False)
    is_used = Column(Boolean, default=False)
    used_at = Column(DateTime(timezone=True))
    original_user_id = Column(UUID(as_uuid=True))
    issued_at = Column(DateTime(timezone=True), server_default=func.now())
