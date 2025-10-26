"""
Shared application constants
"""

# Election statuses
class ElectionStatus:
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"
    TALLIED = "TALLIED"

# KYC statuses
class KYCStatus:
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

# Trustee statuses
class TrusteeStatus:
    INVITED = "INVITED"
    ACCEPTED = "ACCEPTED"
    KEY_GENERATED = "KEY_GENERATED"
    ACTIVE = "ACTIVE"

# Bulletin board entry types
class BulletinEntryType:
    ELECTION_CREATED = "ELECTION_CREATED"
    KEY_GENERATED = "KEY_GENERATED"
    BALLOT_CAST = "BALLOT_CAST"
    ELECTION_CLOSED = "ELECTION_CLOSED"
    TRUSTEE_SHARE = "TRUSTEE_SHARE"
    RESULT_PUBLISHED = "RESULT_PUBLISHED"

# Audit log severity levels
class AuditSeverity:
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

# Cryptographic parameters
CURVE_NAME = "curve25519"
SECURITY_LEVEL = 128  # bits
ED25519_KEY_SIZE = 32  # bytes
X25519_KEY_SIZE = 32  # bytes
AES_KEY_SIZE = 32  # 256 bits
NONCE_SIZE = 12  # 96 bits for AES-GCM
TAG_SIZE = 16  # 128 bits for AES-GCM
SHA256_HASH_SIZE = 32  # 256 bits

# Threshold cryptography default parameters
DEFAULT_THRESHOLD_T = 5
DEFAULT_TOTAL_TRUSTEES_N = 9

# Code generation
MAIN_CODE_LENGTH = 16  # characters
CANDIDATE_CODE_LENGTH = 8  # characters
