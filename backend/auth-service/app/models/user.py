"""
User database model
"""
from sqlalchemy import Column, String, Boolean, DateTime, Date, BigInteger, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from shared.database import Base


class User(Base):
    __tablename__ = "users"
    
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nic = Column(String(20), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    phone_number = Column(String(20))
    
    # WebAuthn credentials
    webauthn_credential_id = Column(Text)
    webauthn_public_key = Column(Text)
    webauthn_counter = Column(BigInteger, default=0)
    
    # KYC Status
    kyc_status = Column(String(20), default='PENDING', index=True)
    kyc_document_path = Column(Text)
    kyc_verified_at = Column(DateTime(timezone=True))
    kyc_verified_by = Column(UUID(as_uuid=True))
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True))
    
    # Password hash (fallback)
    password_hash = Column(Text)
    
    def __repr__(self):
        return f"<User {self.email}>"
