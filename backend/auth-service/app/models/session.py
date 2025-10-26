"""
Session database model
"""
from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from shared.database import Base


class Session(Base):
    __tablename__ = "sessions"
    
    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    access_token = Column(Text, nullable=False, index=True)
    refresh_token = Column(Text, nullable=False)
    device_info = Column(JSONB)
    ip_address = Column(INET)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    revoked_at = Column(DateTime(timezone=True))
    
    def __repr__(self):
        return f"<Session {self.session_id} for user {self.user_id}>"
