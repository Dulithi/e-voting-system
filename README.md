# E-Vote - Cryptographically Secure E-Voting System

**Group F - Information Security & Cryptography Project**  
MUNASINGHE S.K. (210396E) | JAYASOORIYA D.D.M. (210250D)  
University of Moratuwa | October 2025

---

##  Table of Contents

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Cryptographic Implementation](#cryptographic-implementation)
4. [Security Features](#security-features)
5. [Technology Stack](#technology-stack)
6. [Getting Started](#getting-started)
7. [API Documentation](#api-documentation)
8. [Testing Guide](#testing-guide)

---

##  Project Overview

E-Vote is a comprehensive e-voting system implementing modern cryptographic protocols to ensure:

- **Ballot Secrecy**: End-to-end encryption prevents anyone from reading votes
- **Voter Anonymity**: Blind signatures break the link between voter and ballot
- **Vote Verifiability**: Voters can verify their vote was counted correctly
- **Result Integrity**: Threshold cryptography prevents single-point manipulation
- **Universal Auditability**: Public bulletin board with cryptographic hash chain

### Key Cryptographic Features

- **RSA-2048 Blind Signatures** for anonymous voting credentials
- **X25519 ECIES** for ballot encryption (X25519 + AES-256-GCM + HKDF-SHA256)
- **Threshold ElGamal** for distributed decryption (t=5 of n=9 trustees)
- **Blockchain-inspired Bulletin Board** with SHA-256 hash chaining
- **Zero-Knowledge Proofs** for ballot validity (Schnorr protocol)
- **Comprehensive Audit Trail** logging all system events

---

##  System Architecture

### Microservices (6 Python FastAPI Services)

1. **Auth Service** (Port 8001): JWT authentication, KYC management, WebAuthn
2. **Token Service** (Port 8002): RSA blind signature for anonymous tokens
3. **Vote Service** (Port 8003): Vote submission, encryption, ZKP verification
4. **Bulletin Board Service** (Port 8004): SHA-256 hash chain, public audit log
5. **Election Service** (Port 8005): Election CRUD, trustee management, tallying
6. **Code Sheet Service** (Port 8006): Voting code generation and management

### Frontend Applications

- **Admin Web** (React + TypeScript, Port 5173): Election management dashboard
- **Mobile App** (Flutter/Dart): Voter interface with secure cryptography

### Database

- **PostgreSQL 18**: 11 tables with full audit trail and bulletin board

---

##  Cryptographic Implementation

### 1. Ballot Encryption (ECIES)

**Algorithm**: X25519 + AES-256-GCM + HKDF-SHA256

``
Encryption Process:
1. Generate ephemeral X25519 keypair
2. Compute shared secret: ECDH(ephemeral_private, recipient_public)
3. Derive encryption key: HKDF-SHA256(shared_secret)
4. Encrypt vote: AES-256-GCM(plaintext, key)
5. Output: (ephemeral_public, ciphertext, nonce, tag)
``

**Security**: IND-CCA2 secure, forward secrecy, 128-bit security level

### 2. Blind Signatures (Anonymous Credentials)

**Algorithm**: RSA-2048 (Chaum's Protocol)

```
Process:
1. Voter blinds token: m' = H(t)  r^e mod n
2. Server signs blinded: s' = (m')^d mod n
3. Voter unblinds: s = s'  r^(-1) mod n
4. Submit vote with (t, s)
```

**Security**: Unlinkable, unforgeable, one-time use enforced

### 3. Threshold Cryptography

**Parameters**: t=5 trustees required, n=9 total trustees

- **Key Generation**: Distributed key generation (DKG) with Shamir secret sharing
- **Encryption**: ElGamal on Curve25519
- **Decryption**: Lagrange interpolation on t=5 partial decryptions

**Security**: No single point of failure, collusion resistant

### 4. Bulletin Board (Hash Chain)

```json
{
  "entry_hash": "SHA256(entry_data + previous_hash)",
  "previous_hash": "hash of entry N-1",
  "entry_type": "BALLOT_CAST | ELECTION_CREATED | ...",
  "entry_data": { "ballot_hash": "...", "timestamp": "..." }
}
```

**Security**: Tamper-evident, append-only, publicly verifiable

---

##  Security Features

### Authentication & Authorization
- **JWT**: HS256, 15-min access tokens, 7-day refresh tokens
- **Passwords**: bcrypt with 12 rounds
- **WebAuthn**: Infrastructure ready for biometrics

### Database Security
- **Encryption at rest**: AES-256 for sensitive fields
- **SQL injection prevention**: Parameterized queries only
- **Audit logging**: Every critical operation logged

### Network Security
- **CORS**: Strict origin whitelist
- **Rate limiting**: Per-endpoint limits
- **TLS 1.3**: For production deployment

---

##  Technology Stack

### Backend
- Python 3.13, FastAPI, PostgreSQL 18, SQLAlchemy 2.0
- Cryptography: cryptography (PyCA), pynacl, 
sa, hashlib
- Authentication: JWT (PyJWT), bcrypt

### Frontend
- **Admin Web**: React 18 + TypeScript, Material-UI v5, Redux Toolkit, Vite
- **Mobile**: Flutter 3.16+, Provider, pointycastle, flutter_secure_storage

---

##  Getting Started

### Prerequisites

- Python 3.13+
- Node.js 20+ and npm
- PostgreSQL 18
- Flutter 3.16+ (for mobile)

### Quick Start

#### 1. Database Setup

```powershell
# Create database
psql -U postgres -c "CREATE DATABASE evoting_db;"

# Initialize schema
psql -U postgres -d evoting_db -f scripts/db-init.sql
```

#### 2. Start Backend Services

Each service needs its own terminal:

```powershell
# Example for Auth Service (Port 8001)
cd backend/auth-service
python -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

Repeat for all 6 services (ports 8001-8006).

#### 3. Start Admin Web

```powershell
cd admin-web
npm install
npm run dev
```

Access at: http://localhost:5173

#### 4. Start Mobile App

```powershell
cd mobile-app
flutter pub get
flutter run
```

### Default Login Credentials

**Admin Web**:
- Email: admin@evote.com
- Password: Admin@123

---

##  API Documentation

Access interactive API docs at:

- Auth: http://localhost:8001/api/docs
- Token: http://localhost:8002/api/docs
- Vote: http://localhost:8003/api/docs
- Bulletin: http://localhost:8004/api/docs
- Election: http://localhost:8005/api/docs
- Code Sheet: http://localhost:8006/api/docs

### Key Endpoints

**POST /api/auth/login**
```json
{ "email": "admin@evote.com", "password": "Admin@123" }
```

**POST /api/election/create** (Admin only)
```json
{
  "title": "2025 Election",
  "start_time": "2025-11-01T09:00:00Z",
  "end_time": "2025-11-01T17:00:00Z",
  "threshold_t": 5,
  "total_trustees_n": 9
}
```

**POST /api/vote/submit**
```json
{
  "election_id": "uuid",
  "encrypted_vote": { "ephemeral_public_key": "...", "ciphertext": "..." },
  "proof": { "commitment": "..." },
  "token_hash": "...",
  "token_signature": "..."
}
```

---

##  Testing Guide

### 1. Backend Health Check

```powershell
curl http://localhost:8001/health  # Auth
curl http://localhost:8002/health  # Token
curl http://localhost:8003/health  # Vote
curl http://localhost:8004/health  # Bulletin
curl http://localhost:8005/health  # Election
curl http://localhost:8006/health  # Code Sheet
```

### 2. Admin Web Workflow

1. **Login**: http://localhost:5173 with admin@evote.com / Admin@123
2. **Create Election**: Dashboard  Elections  Create
3. **Add Candidates**: Election Details  Add Candidate
4. **Approve KYC**: Voters  Approve pending users
5. **Key Ceremony**: Election Details  Key Ceremony (generates election public key)
6. **Activate Election**: Change status to ACTIVE
7. **Generate Voting Codes**: Voting Codes  Generate Codes
8. **Tally Results**: After voting ends, collect 5/9 trustee shares  Tally
9. **View Bulletin Board**: Verify hash chain integrity

### 3. Mobile App Workflow

1. **Register**: Create voter account
2. **Wait for KYC Approval**: Admin approves from web dashboard
3. **View Elections**: See active elections
4. **Cast Vote**: Select candidate  Encrypt & Submit
5. **Receive Receipt**: Ballot hash, verification code, QR code

### 4. End-to-End Test

1. Admin creates election with 3 candidates
2. Admin runs key ceremony (9 trustees)
3. Admin activates election
4. Voter registers via mobile app
5. Admin approves voter KYC
6. Voter requests anonymous token (blind signature)
7. Voter encrypts and submits vote
8. Bulletin board records vote (with ballot hash)
9. Admin closes election
10. 5 trustees submit decryption shares
11. Admin tallies results
12. Anyone verifies bulletin board hash chain

---

##  Database Schema

### Core Tables (11)

1. **users**: Voter and admin accounts (NIC, email, password_hash, public_key, kyc_status)
2. **elections**: Election metadata (title, start/end time, status, threshold_t, total_trustees_n)
3. **candidates**: Election candidates (name, party, display_order)
4. **trustees**: Threshold trustees (public_key_share, decryption_shares)
5. **ballots**: Encrypted votes (encrypted_ballot, zkp_proof, ballot_hash, verification_code)
6. **anonymous_tokens**: Blind signed tokens (token_hash, is_used)
7. **election_results**: Tally results (candidate_id, vote_count)
8. **voting_codes**: Voter verification codes
9. **bulletin_board**: Public audit log (entry_hash, previous_hash, entry_type, entry_data)
10. **sessions**: JWT session management
11. **audit_logs**: System audit trail (event_type, user_id, metadata, severity)

---

##  Implemented Features

### Backend (100% Complete)
 JWT authentication & refresh tokens  
 KYC approval workflow  
 Election CRUD with candidate management  
 Threshold trustee management (t=5, n=9)  
 RSA-2048 blind signature token issuance  
 ECIES ballot encryption support  
 Vote submission with anonymous tokens  
 Double-vote prevention  
 Threshold decryption and tallying  
 Voting code generation (bulk & individual)  
 Bulletin board with SHA-256 hash chaining  
 Chain integrity verification  
 Comprehensive audit trail logging  

### Admin Web (100% Complete)
 Admin dashboard with statistics  
 Election management (create, edit, activate, close)  
 Candidate management  
 Voter KYC approval  
 Trustee key ceremony coordination  
 Election tallying and results display  
 Voting code generation and CSV export  
 Bulletin board visualization with verification  

### Mobile App (100% Complete)
 User registration and login  
 X25519 keypair generation  
 ECIES vote encryption  
 RSA blind signature client  
 Election listing  
 Secure vote casting  
 Vote receipt with QR code  
 Secure key storage (Keychain/Keystore)  

---

##  Cryptographic Guarantees

| Property | Implementation | Security Level |
|----------|---------------|----------------|
| Ballot Secrecy | ECIES (X25519 + AES-256-GCM) | IND-CCA2 secure |
| Voter Anonymity | RSA-2048 Blind Signatures | Unlinkable |
| Vote Integrity | GCM Authentication Tag | Tamper-proof |
| Distributed Trust | Threshold ElGamal (t=5, n=9) | No single point of failure |
| Verifiability | SHA-256 Hash Chain + ZKPs | Publicly auditable |
| Forward Secrecy | Ephemeral X25519 keys | Past messages secure |

---

##  References

### Cryptographic Standards
- NIST FIPS 186-5: Digital Signature Standard
- NIST SP 800-56A Rev. 3: Elliptic Curve Cryptography
- RFC 8032: EdDSA (Ed25519)
- RFC 7748: Curve25519, X25519
- RFC 5869: HKDF

### E-Voting Research
- Helios Voting System: https://heliosvoting.org
- Swiss E-Voting Framework
- Chaum, D. (1983): Blind Signatures for Untraceable Payments
- Adida, B. (2008): Helios: Web-based Open-Audit Voting

---

##  Team

**Group F**  
- MUNASINGHE S.K. - 210396E  
- JAYASOORIYA D.D.M. - 210250D  

**Course**: Information Security & Cryptography  
**Institution**: University of Moratuwa  
**Semester**: 7 (2024/2025)

---

##  License

This project is an academic assignment for course evaluation purposes. All rights reserved.

---

**Last Updated**: October 29, 2025

---

##  Support

For technical issues:
1. Check API documentation at http://localhost:PORT/api/docs
2. Verify all services running: 
etstat -ano | findstr "800[1-6]"
3. Check service logs in terminal outputs
4. Review audit logs: psql -U postgres -d evoting_db -c "SELECT * FROM audit_logs ORDER BY created_at DESC LIMIT 10;"

---

**End of Documentation**
