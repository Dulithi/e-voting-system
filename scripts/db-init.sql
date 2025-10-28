-- SecureVote E-Voting System Database Schema
-- Group F: MUNASINGHE S.K. (210396E), JAYASOORIYA D.D.M. (210250D)
-- Date: October 26, 2025

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =============================================
-- USERS AND AUTHENTICATION
-- =============================================

CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nic VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    date_of_birth DATE NOT NULL,
    phone_number VARCHAR(20),
    
    -- WebAuthn credentials
    webauthn_credential_id TEXT,
    webauthn_public_key TEXT,
    webauthn_counter BIGINT DEFAULT 0,
    
    -- KYC Status
    kyc_status VARCHAR(20) DEFAULT 'PENDING' CHECK (kyc_status IN ('PENDING', 'APPROVED', 'REJECTED')),
    kyc_document_path TEXT,
    kyc_verified_at TIMESTAMP,
    kyc_verified_by UUID REFERENCES users(user_id),
    
    -- Account status
    is_active BOOLEAN DEFAULT true,
    is_admin BOOLEAN DEFAULT false,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP,
    
    -- Audit
    created_by UUID,
    password_hash TEXT, -- Fallback authentication
    
    CONSTRAINT valid_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_nic ON users(nic);
CREATE INDEX idx_users_kyc_status ON users(kyc_status);

-- User sessions
CREATE TABLE sessions (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    access_token TEXT NOT NULL,
    refresh_token TEXT NOT NULL,
    device_info JSONB,
    ip_address INET,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    revoked_at TIMESTAMP,
    
    CONSTRAINT valid_expiry CHECK (expires_at > created_at)
);

CREATE INDEX idx_sessions_user ON sessions(user_id);
CREATE INDEX idx_sessions_access_token ON sessions(access_token);
CREATE INDEX idx_sessions_expires_at ON sessions(expires_at);

-- =============================================
-- ELECTIONS
-- =============================================

CREATE TABLE elections (
    election_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Election timing
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    
    -- Status
    status VARCHAR(20) DEFAULT 'DRAFT' CHECK (status IN ('DRAFT', 'ACTIVE', 'CLOSED', 'TALLIED')),
    
    -- Cryptographic parameters
    public_key TEXT, -- Threshold ElGamal public key
    key_generation_completed BOOLEAN DEFAULT false,
    threshold_t INTEGER NOT NULL, -- Minimum trustees needed to decrypt
    total_trustees_n INTEGER NOT NULL, -- Total number of trustees
    
    -- Election configuration
    allow_revote BOOLEAN DEFAULT false,
    require_code_verification BOOLEAN DEFAULT true,
    max_voters INTEGER,
    
    -- Metadata
    created_by UUID NOT NULL REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_election_times CHECK (end_time > start_time),
    CONSTRAINT valid_threshold CHECK (threshold_t > 0 AND threshold_t <= total_trustees_n)
);

CREATE INDEX idx_elections_status ON elections(status);
CREATE INDEX idx_elections_timing ON elections(start_time, end_time);

-- Candidates
CREATE TABLE candidates (
    candidate_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    election_id UUID NOT NULL REFERENCES elections(election_id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    party VARCHAR(255),
    description TEXT,
    photo_url TEXT,
    
    -- Cryptographic identifier (for ElGamal encryption)
    m_value BYTEA NOT NULL, -- Elliptic curve point representation
    
    display_order INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT true,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(election_id, display_order)
);

CREATE INDEX idx_candidates_election ON candidates(election_id);

-- =============================================
-- TRUSTEES (Threshold Cryptography)
-- =============================================

CREATE TABLE trustees (
    trustee_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    election_id UUID NOT NULL REFERENCES elections(election_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(user_id),
    
    -- Key share information
    public_key_share TEXT, -- Trustee's public key share
    key_share_proof TEXT, -- Zero-knowledge proof of key share validity
    
    -- Decryption shares (after election)
    decryption_shares JSONB, -- Array of partial decryptions
    shares_submitted BOOLEAN DEFAULT false,
    shares_submitted_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(election_id, user_id)
);

CREATE INDEX idx_trustees_election ON trustees(election_id);
CREATE INDEX idx_trustees_user ON trustees(user_id);

-- =============================================
-- VOTING CODES (Return Codes for Verification)
-- =============================================

CREATE TABLE voting_codes (
    code_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    election_id UUID NOT NULL REFERENCES elections(election_id) ON DELETE CASCADE,
    
    -- Main voting code (proves eligibility)
    main_voting_code VARCHAR(64) NOT NULL UNIQUE,
    
    -- Individual candidate verification codes
    candidate_codes JSONB NOT NULL, -- {candidate_id: verification_code}
    
    -- Encrypted code sheet
    encrypted_code_sheet BYTEA, -- Encrypted with server secret
    
    -- Status
    code_sheet_generated BOOLEAN DEFAULT false,
    code_sheet_sent BOOLEAN DEFAULT false,
    code_sheet_sent_at TIMESTAMP,
    
    main_code_used BOOLEAN DEFAULT false,
    main_code_used_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    
    UNIQUE(user_id, election_id)
);

CREATE INDEX idx_voting_codes_user ON voting_codes(user_id);
CREATE INDEX idx_voting_codes_election ON voting_codes(election_id);
CREATE INDEX idx_voting_codes_main_code ON voting_codes(main_voting_code);

-- =============================================
-- ANONYMOUS TOKENS (Blind Signatures)
-- =============================================

CREATE TABLE anonymous_tokens (
    token_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    election_id UUID NOT NULL REFERENCES elections(election_id) ON DELETE CASCADE,
    
    -- Token hash (to prevent double-use without revealing voter)
    token_hash VARCHAR(64) UNIQUE NOT NULL,
    
    -- Blind signature
    signed_blind_token BYTEA NOT NULL,
    
    -- Usage tracking
    is_used BOOLEAN DEFAULT false,
    used_at TIMESTAMP,
    
    -- Link to original user (only stored temporarily, deleted after use)
    original_user_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT check_used_timestamp CHECK (
        (is_used = true AND used_at IS NOT NULL) OR 
        (is_used = false AND used_at IS NULL)
    )
);

CREATE INDEX idx_anonymous_tokens_election ON anonymous_tokens(election_id);
CREATE INDEX idx_anonymous_tokens_hash ON anonymous_tokens(token_hash);
CREATE INDEX idx_anonymous_tokens_used ON anonymous_tokens(is_used);

-- =============================================
-- BALLOTS (Encrypted Votes)
-- =============================================

CREATE TABLE ballots (
    ballot_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    election_id UUID NOT NULL REFERENCES elections(election_id) ON DELETE CASCADE,
    
    -- Encrypted ballot (ECIES + ElGamal)
    encrypted_ballot BYTEA NOT NULL,
    
    -- Zero-knowledge proof
    zkp_proof JSONB NOT NULL, -- Proof that ballot is well-formed
    
    -- Ballot signature (Ed25519)
    ballot_signature BYTEA NOT NULL,
    
    -- Hash for verification
    ballot_hash VARCHAR(64) UNIQUE NOT NULL,
    
    -- Verification code returned to voter
    verification_code VARCHAR(64),
    
    -- Anonymous token used (hash only)
    token_hash VARCHAR(64) NOT NULL,
    
    -- Bulletin board reference
    bulletin_entry_id UUID,
    
    -- Metadata (no identifying information)
    cast_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address_hash VARCHAR(64), -- Hashed IP for abuse detection
    
    -- Mix-net processing
    mixed BOOLEAN DEFAULT false,
    mixed_at TIMESTAMP,
    mix_position INTEGER,
    
    CONSTRAINT fk_token FOREIGN KEY (token_hash) REFERENCES anonymous_tokens(token_hash)
);

CREATE INDEX idx_ballots_election ON ballots(election_id);
CREATE INDEX idx_ballots_hash ON ballots(ballot_hash);
CREATE INDEX idx_ballots_token ON ballots(token_hash);
CREATE INDEX idx_ballots_cast_time ON ballots(cast_at);

-- =============================================
-- BULLETIN BOARD (Public Verifiable Record)
-- =============================================

CREATE TABLE bulletin_board (
    entry_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    election_id UUID NOT NULL REFERENCES elections(election_id) ON DELETE CASCADE,
    
    -- Entry type
    entry_type VARCHAR(50) NOT NULL CHECK (entry_type IN (
        'ELECTION_CREATED', 
        'KEY_GENERATED', 
        'BALLOT_CAST', 
        'ELECTION_CLOSED', 
        'TRUSTEE_SHARE',
        'RESULT_PUBLISHED'
    )),
    
    -- Hash chain
    entry_hash VARCHAR(64) UNIQUE NOT NULL,
    previous_hash VARCHAR(64), -- Links to previous entry
    
    -- Entry data (public information only)
    entry_data JSONB NOT NULL,
    
    -- Digital signature
    signature BYTEA NOT NULL,
    
    -- Timestamp
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Sequential order
    sequence_number BIGSERIAL UNIQUE
);

CREATE INDEX idx_bulletin_election ON bulletin_board(election_id);
CREATE INDEX idx_bulletin_type ON bulletin_board(entry_type);
CREATE INDEX idx_bulletin_sequence ON bulletin_board(sequence_number);
CREATE INDEX idx_bulletin_hash ON bulletin_board(entry_hash);

-- =============================================
-- ELECTION RESULTS
-- =============================================

CREATE TABLE election_results (
    result_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    election_id UUID NOT NULL REFERENCES elections(election_id) ON DELETE CASCADE,
    candidate_id UUID NOT NULL REFERENCES candidates(candidate_id) ON DELETE CASCADE,
    
    -- Vote count
    vote_count INTEGER NOT NULL DEFAULT 0,
    
    -- Verification data
    decrypted_tally BYTEA, -- Final decrypted tally
    tally_proof JSONB, -- Proof of correct tallying
    
    -- Metadata
    tallied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    verified BOOLEAN DEFAULT false,
    
    UNIQUE(election_id, candidate_id)
);

CREATE INDEX idx_results_election ON election_results(election_id);

-- =============================================
-- AUDIT LOGS
-- =============================================

CREATE TABLE audit_logs (
    log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Event details
    event_type VARCHAR(100) NOT NULL,
    event_description TEXT,
    
    -- User involved (nullable for anonymous actions)
    user_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    
    -- Resource affected
    resource_type VARCHAR(50),
    resource_id UUID,
    
    -- Request details
    ip_address INET,
    user_agent TEXT,
    request_method VARCHAR(10),
    request_path TEXT,
    
    -- Additional data
    metadata JSONB,
    
    -- Timestamp
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Severity
    severity VARCHAR(20) DEFAULT 'INFO' CHECK (severity IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'))
);

CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_event_type ON audit_logs(event_type);
CREATE INDEX idx_audit_created_at ON audit_logs(created_at);
CREATE INDEX idx_audit_resource ON audit_logs(resource_type, resource_id);

-- =============================================
-- TRIGGERS FOR UPDATED_AT
-- =============================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_elections_updated_at BEFORE UPDATE ON elections
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================
-- SECURITY: ROW LEVEL SECURITY (Example)
-- =============================================

-- Enable RLS on sensitive tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE ballots ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own data
CREATE POLICY users_select_own ON users
    FOR SELECT
    USING (user_id = current_setting('app.current_user_id')::UUID OR 
           (SELECT is_admin FROM users WHERE user_id = current_setting('app.current_user_id')::UUID));

-- =============================================
-- INITIAL DATA (Optional)
-- =============================================

-- Create default admin user (password: Admin@123 - CHANGE THIS!)
INSERT INTO users (nic, email, full_name, date_of_birth, is_admin, kyc_status, password_hash)
VALUES (
    'ADMIN001',
    'admin@securevote.com',
    'System Administrator',
    '1990-01-01',
    true,
    'APPROVED',
    crypt('Admin@123', gen_salt('bf', 10))
);

-- =============================================
-- VIEWS FOR REPORTING
-- =============================================

-- View: Election statistics
CREATE VIEW election_statistics AS
SELECT 
    e.election_id,
    e.title,
    e.status,
    COUNT(DISTINCT b.ballot_id) as total_votes_cast,
    COUNT(DISTINCT vc.user_id) as total_eligible_voters,
    e.start_time,
    e.end_time
FROM elections e
LEFT JOIN ballots b ON e.election_id = b.election_id
LEFT JOIN voting_codes vc ON e.election_id = vc.election_id
GROUP BY e.election_id;

-- View: Trustee participation
CREATE VIEW trustee_participation AS
SELECT 
    e.election_id,
    e.title as election_title,
    COUNT(t.trustee_id) as total_trustees,
    COUNT(t.trustee_id) FILTER (WHERE t.key_share_proof IS NOT NULL) as trustees_with_keys,
    COUNT(t.trustee_id) FILTER (WHERE t.shares_submitted = true) as trustees_submitted_shares
FROM elections e
LEFT JOIN trustees t ON e.election_id = t.election_id
GROUP BY e.election_id, e.title;

-- =============================================
-- FUNCTIONS
-- =============================================

-- Function: Check if user can vote in election
CREATE OR REPLACE FUNCTION can_user_vote(p_user_id UUID, p_election_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
    v_kyc_approved BOOLEAN;
    v_election_active BOOLEAN;
    v_has_code BOOLEAN;
    v_already_voted BOOLEAN;
BEGIN
    -- Check KYC status
    SELECT kyc_status = 'APPROVED' INTO v_kyc_approved
    FROM users WHERE user_id = p_user_id;
    
    -- Check election status
    SELECT status = 'ACTIVE' AND CURRENT_TIMESTAMP BETWEEN start_time AND end_time
    INTO v_election_active
    FROM elections WHERE election_id = p_election_id;
    
    -- Check if user has voting code
    SELECT EXISTS(
        SELECT 1 FROM voting_codes 
        WHERE user_id = p_user_id AND election_id = p_election_id
    ) INTO v_has_code;
    
    -- Check if already voted
    SELECT EXISTS(
        SELECT 1 FROM voting_codes vc
        JOIN anonymous_tokens at ON at.original_user_id = vc.user_id
        WHERE vc.user_id = p_user_id 
        AND vc.election_id = p_election_id 
        AND at.is_used = true
    ) INTO v_already_voted;
    
    RETURN v_kyc_approved AND v_election_active AND v_has_code AND NOT v_already_voted;
END;
$$ LANGUAGE plpgsql;

-- =============================================
-- COMMENTS
-- =============================================

COMMENT ON TABLE users IS 'Stores registered voter information with KYC verification';
COMMENT ON TABLE elections IS 'Election definitions with cryptographic parameters';
COMMENT ON TABLE ballots IS 'Encrypted ballots with zero-knowledge proofs';
COMMENT ON TABLE bulletin_board IS 'Public verifiable ledger of all election events';
COMMENT ON TABLE anonymous_tokens IS 'Blind signatures for anonymous voting';
COMMENT ON TABLE trustees IS 'Threshold cryptography trustees for result decryption';
COMMENT ON TABLE voting_codes IS 'Individual verification codes for vote confirmation';

-- End of schema
