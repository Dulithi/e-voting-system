# SecureVote - Cryptographically Secure E-Voting System# SecureVote E-Voting System



**Group F - Information Security & Cryptography Project**  **Group F - IS & Cryptography Project**  

MUNASINGHE S.K. (210396E) | JAYASOORIYA D.D.M. (210250D)  MUNASINGHE S.K. (210396E) | JAYASOORIYA D.D.M. (210250D)

University of Moratuwa | October 2025

## 🎯 Project Overview

---

A secure, end-to-end verifiable e-voting system implementing modern cryptographic protocols including:

## 📋 Table of Contents- **WebAuthn/FIDO2** biometric authentication

- **RSA Blind Signatures** for anonymous voting credentials

1. [Project Overview](#project-overview)- **Threshold ElGamal** homomorphic encryption

2. [System Architecture](#system-architecture)- **Zero-Knowledge Proofs** for ballot validity

3. [Cryptographic Implementation](#cryptographic-implementation)- **Public Bulletin Board** for universal verifiability

4. [Security Features](#security-features)

5. [Technology Stack](#technology-stack)---

6. [Getting Started](#getting-started)

7. [Project Structure](#project-structure)## 🏗️ Architecture

8. [API Documentation](#api-documentation)

9. [Implemented Features](#implemented-features)### Microservices Backend (Python FastAPI)

10. [Database Schema](#database-schema)```

11. [Testing Guide](#testing-guide)┌─────────────────┬─────────────────┬─────────────────┬─────────────────┐

│  Auth Service   │  Token Service  │  Vote Service   │ Bulletin Board  │

---│   (Port 8001)   │   (Port 8002)   │   (Port 8003)   │   (Port 8004)   │

├─────────────────┼─────────────────┼─────────────────┼─────────────────┤

## 🎯 Project Overview│ • User Auth     │ • Blind RSA-2048│ • Vote Storage  │ • Hash Chain    │

│ • JWT Tokens    │   Signatures    │ • Ballot Verify │ • Public Audit  │

SecureVote is a comprehensive e-voting system implementing modern cryptographic protocols to ensure:│ • KYC Management│ • Anonymous     │ • ZK Proofs     │ • Vote Receipts │

- **Ballot Secrecy**: End-to-end encryption prevents anyone from reading votes│ • WebAuthn      │   Credentials   │ • Encryption    │                 │

- **Voter Anonymity**: Blind signatures break the link between voter and ballot└─────────────────┴─────────────────┴─────────────────┴─────────────────┘

- **Vote Verifiability**: Voters can verify their vote was counted correctly┌─────────────────┬─────────────────────────────────────────────────────┐

- **Result Integrity**: Threshold cryptography prevents single-point manipulation│ Election Service│              Code Sheet Service                     │

- **Universal Auditability**: Public bulletin board with cryptographic hash chain│   (Port 8005)   │                (Port 8006)                          │

├─────────────────┼─────────────────────────────────────────────────────┤

### Key Innovations│ • Election CRUD │ • PDF Generation                                    │

- **RSA-2048 Blind Signatures** for anonymous voting credentials│ • Candidate Mgmt│ • Voter Code Sheets (verification codes)            │

- **X25519 ECIES** for ballot encryption  │ • Threshold t/n │ • Secure Distribution                               │

- **Threshold ElGamal** for distributed decryption (t=5 of n=9 trustees)│ • Results Tally │                                                     │

- **Blockchain-inspired Bulletin Board** with SHA-256 hash chaining└─────────────────┴─────────────────────────────────────────────────────┘

- **Comprehensive Audit Trail** logging all system events```



---### Frontend Applications

- **Admin Web** (React + TypeScript + Material-UI) - Port 5173

## 🏗️ System Architecture- **Mobile App** (Flutter) - *Coming Soon*



### Microservices Architecture### Database

- **PostgreSQL 18** with 11 tables for complete election lifecycle

```

┌─────────────────────────────────────────────────────────────────┐---

│                        Client Layer                              │

├──────────────────────────┬──────────────────────────────────────┤## 🔐 Cryptographic Concepts Explained

│   Flutter Mobile App     │   React Admin Web App                │

│   (Voter Interface)      │   (Election Management)              │### 1. Threshold Encryption (t-of-n)

│   Port: Mobile Device    │   Port: 5173                         │**What it means:**

└──────────┬───────────────┴──────────────┬───────────────────────┘- **n = Total Trustees** (e.g., 9 election officials)

           │                               │- **t = Threshold** (e.g., 5 minimum required)

           │          HTTPS/TLS 1.3       │- Election results are encrypted so that **at least `t` out of `n` trustees** must collaborate to decrypt

           │                               │- Prevents any single authority from tampering with results

┌──────────┴───────────────────────────────┴───────────────────────┐- Even if `t-1` trustees collude, they cannot decrypt votes

│                    Backend Services (Python FastAPI)             │

├──────────────┬──────────────┬──────────────┬─────────────────────┤**Example:** With t=5, n=9:

│ Auth Service │ Token Service│ Vote Service │ Bulletin Board      │- Private key is split into 9 shares

│ Port: 8001   │ Port: 8002   │ Port: 8003   │ Port: 8004          │- Any 5 trustees can combine their shares to decrypt results

│              │              │              │                     │- 4 trustees alone cannot decrypt anything

│ • JWT Auth   │ • Blind RSA  │ • Vote Store │ • Hash Chain       │- This is **Threshold ElGamal** on Curve25519

│ • KYC Mgmt   │   Signatures │ • Encrypt    │ • Public Audit     │

│ • WebAuthn   │ • Anonymous  │ • ZKP Verify │ • Verifiability    │### 2. Blind Signatures (Anonymous Voting)

│ • User Mgmt  │   Tokens     │ • Receipts   │ • Tamper Evidence  │**RSA-2048 Blind Signatures:**

├──────────────┴──────────────┴──────────────┴─────────────────────┤1. Voter blinds their identity using random factor

│ Election Service │ Code Sheet Service                            │2. Token service signs the blinded value (without seeing identity)

│ Port: 8005       │ Port: 8006                                    │3. Voter unblinds the signature

│                  │                                               │4. Result: Valid signature on voter's credential, but server never saw the actual credential

│ • Election CRUD  │ • Voting Code Generation                      │5. Voter uses this anonymous credential to vote

│ • Candidate Mgmt │ • Bulk Code Generation                        │6. **Breaks the link between voter identity and ballot**

│ • Trustee Mgmt   │ • Code Verification                           │

│ • Key Ceremony   │ • CSV Export                                  │### 3. Display Order

│ • Tally/Decrypt  │                                               │**What it means:**

│ • Results View   │                                               │- The order in which candidates appear on the ballot (1, 2, 3, ...)

└──────────────────┴───────────────────────────────────────────────┘- Auto-increments when adding candidates

           │- Used for ballot layout in mobile app and code sheets

┌──────────┴───────────────────────────────────────────────────────┐- Important for consistent user experience

│                  PostgreSQL Database (Port: 5432)                │

│  • Users • Elections • Candidates • Ballots • Trustees           │---

│  • Voting Codes • Bulletin Board • Audit Logs • Sessions         │

└──────────────────────────────────────────────────────────────────┘## 📁 Project Structure

```

```

### Data Flowe-voting-system/

├── backend/

**1. Voter Registration & Authentication**│   ├── auth-service/          # User authentication, KYC, JWT tokens

```│   ├── token-service/         # Blind signatures for anonymous credentials

Mobile App → Auth Service (8001) → Database│   ├── vote-service/          # Vote submission and storage

   └─ Generate X25519 keypair locally│   ├── bulletin-board-service/# Public bulletin with hash chain

   └─ Store private key in Secure Storage│   ├── election-service/      # Election management, candidates, trustees

   └─ Send public key to server│   ├── code-sheet-service/    # Generate PDF verification code sheets

```│   └── shared/                # Common utilities (database, security, crypto)

│

**2. Anonymous Token Acquisition**├── admin-web/                 # React admin dashboard

```│   ├── src/

Mobile App → Token Service (8002)│   │   ├── pages/            # Dashboard, Elections, Voters, Results

   └─ Client blinds random token with RSA blinding factor│   │   ├── services/         # API clients for each backend service

   └─ Server signs blinded token (RSA-2048)│   │   └── store/            # Redux state management

   └─ Client unblinds to get valid anonymous credential│   └── package.json

   └─ Token stored securely, breaks voter-ballot link│

```├── mobile-app/                # Flutter voter app (coming soon)

├── infrastructure/            # Nginx, SSL configs

**3. Vote Casting**├── scripts/

```│   └── db-init.sql           # Complete PostgreSQL schema

Mobile App → Vote Service (8003) → Bulletin Board (8004)├── docs/                     # Project documentation

   └─ Encrypt vote with ECIES (X25519 + AES-256-GCM)├── .gitignore

   └─ Generate zero-knowledge proof of validity├── README.md                 # This file

   └─ Submit with anonymous token└── START_SERVICES.md         # How to run the system

   └─ Token marked as used (prevent double voting)```

   └─ Vote posted to public bulletin board

   └─ Receipt with ballot hash returned---

```

## 🚀 Quick Start

**4. Election Tallying**

```### Prerequisites

Admin Web → Election Service (8005) → Database- **Python 3.13+** (with pip, venv)

   └─ Collect decryption shares from trustees (threshold t=5)- **Node.js 20+** (with npm)

   └─ Combine shares to decrypt ballots- **PostgreSQL 18** (local installation)

   └─ Count votes per candidate- **Git**

   └─ Publish results to bulletin board

```### 1. Clone Repository

```bash

---git clone <repository-url>

cd e-voting-system

## 🔐 Cryptographic Implementation```



### 1. Ballot Encryption (ECIES - Elliptic Curve Integrated Encryption Scheme)### 2. Database Setup

```bash

**Algorithm**: X25519 (Curve25519) + AES-256-GCM + HKDF-SHA256# Create database

psql -U postgres -c "CREATE DATABASE evoting_db;"

**Process**:

1. **Key Generation**: Voter generates X25519 keypair# Initialize schema

   ```psql -U postgres -d evoting_db -f scripts/db-init.sql

   Private Key: 32 random bytes

   Public Key: X25519 point (32 bytes)# Create admin user

   ```psql -U postgres -d evoting_db -c "

INSERT INTO users (nic, email, full_name, date_of_birth, is_admin, kyc_status, password_hash)

2. **Encryption**:VALUES ('ADMIN001', 'admin@securevote.com', 'System Admin', '1990-01-01', true, 'APPROVED', '\$2b\$12\$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzNx7Z7rMu');

   ```"

   a. Generate ephemeral X25519 keypair# Password: Admin@123

   b. Compute shared secret: ECDH(ephemeral_private, recipient_public)```

   c. Derive encryption key: HKDF-SHA256(shared_secret)

   d. Encrypt vote: AES-256-GCM(plaintext, key)### 3. Start Backend Services

   e. Output: (ephemeral_public, ciphertext, nonce, authentication_tag)See **[START_SERVICES.md](./START_SERVICES.md)** for detailed instructions.

   ```

**Quick version:**

3. **Decryption** (by trustees using threshold scheme):```bash

   ```# Terminal 1 - Auth Service

   a. Each trustee computes partial shared secretcd backend/auth-service

   b. Combine t=5 partial secrets → full shared secretpython -m venv venv

   c. Derive decryption key: HKDF-SHA256(shared_secret).\venv\Scripts\Activate.ps1  # Windows

   d. Decrypt: AES-256-GCM-Decrypt(ciphertext, key)source venv/bin/activate      # Linux/Mac

   ```pip install -r requirements.txt

$env:DATABASE_URL="postgresql://postgres:YourPassword@localhost:5432/evoting_db"

**Security Properties**:uvicorn app.main:app --port 8001 --reload

- **IND-CCA2 Secure**: Indistinguishable under adaptive chosen-ciphertext attack

- **Forward Secrecy**: Ephemeral keys ensure past messages safe even if long-term key compromised# Terminal 2 - Election Service

- **Authentication**: GCM tag prevents tamperingcd backend/election-service

- **128-bit Security Level**: Curve25519 provides equivalent security to 3072-bit RSApython -m venv venv

.\venv\Scripts\Activate.ps1

---pip install -r requirements.txt

$env:DATABASE_URL="postgresql://postgres:YourPassword@localhost:5432/evoting_db"

### 2. Blind Signatures (Anonymous Credentials)uvicorn app.main:app --port 8005 --reload



**Algorithm**: RSA-2048 Blind Signature (Chaum's Protocol)# Repeat for other services (ports 8002-8004, 8006)

```

**Purpose**: Break the link between voter identity and ballot

### 4. Start Admin Web

**Process**:```bash

cd admin-web

1. **Voter Blinds Token** (Client-side):npm install

   ```npm run dev

   a. Generate random token: t = random(256 bits)# Opens on http://localhost:5173

   b. Choose random blinding factor: r ∈ Zn*```

   c. Compute blinded token: m' = H(t) · r^e mod n

   ```### 5. Login

- **URL:** http://localhost:5173

2. **Server Signs Blinded Token**:- **Email:** admin@securevote.com

   ```- **Password:** Admin@123

   a. Verify voter eligibility (KYC approved, hasn't voted)

   b. Sign blinded token: s' = (m')^d mod n---

   c. Store token_hash = SHA256(t) for double-vote prevention

   ```## 📚 API Documentation



3. **Voter Unblinds Signature**:### Auth Service (Port 8001)

   ```- `POST /api/auth/register` - Register new user

   a. Compute unblinded signature: s = s' · r^(-1) mod n- `POST /api/auth/login` - Login with email/password

   b. Verify: s^e ≡ H(t) mod n- `GET /api/auth/me` - Get current user info

   ```- `POST /api/auth/refresh` - Refresh access token

- `GET /api/users/list` - List all voters (admin only)

4. **Vote Submission**:- `POST /api/users/kyc/approve/{user_id}` - Approve KYC (admin only)

   ```- `POST /api/users/kyc/reject/{user_id}` - Reject KYC (admin only)

   a. Submit vote with (t, s)

   b. Server verifies RSA signature: s^e ≡ H(t) mod n### Election Service (Port 8005)

   c. Check token_hash not already used- `GET /api/election/list` - List all elections

   d. Accept vote, mark token as used- `GET /api/election/{id}` - Get election details with candidates

   ```- `POST /api/election/create` - Create new election

- `POST /api/election/candidate/add` - Add candidate to election

**Security Properties**:- `GET /api/election/stats/dashboard` - Get dashboard statistics

- **Unlinkability**: Server cannot link blinded signature to unblinded signature

- **Unforgeability**: Without private key, cannot create valid signatures### Token Service (Port 8002)

- **One-Time Use**: Each token can only vote once (database constraint)- `POST /api/token/request` - Request blind token

- **Voter Anonymity**: No way to determine which voter cast which ballot- `POST /api/token/verify` - Verify anonymous credential



**Mathematical Proof of Unlinkability**:### Vote Service (Port 8003)

```- `POST /api/vote/submit` - Submit encrypted ballot

Given: m' = H(t) · r^e mod n- `POST /api/vote/verify` - Verify ZK proof

Server computes: s' = (m')^d = (H(t) · r^e)^d = H(t)^d · r mod n

Client unblinds: s = s' · r^(-1) = H(t)^d · r · r^(-1) = H(t)^d mod n### Bulletin Board (Port 8004)

- `GET /api/bulletin/list` - View public bulletin board

Server sees: m', s'- `POST /api/bulletin/post` - Post ballot to bulletin (internal)

Voter uses: H(t), s

### Code Sheet Service (Port 8006)

Correlation impossible without knowing r (random blinding factor)- `POST /api/codesheet/generate` - Generate PDF code sheets

```

---

---

## 🗄️ Database Schema

### 3. Threshold Cryptography (ElGamal on Curve25519)

**11 Core Tables:**

**Parameters**: 1. **users** - Voter/admin accounts with WebAuthn credentials

- **Threshold (t)**: 5 trustees required to decrypt2. **sessions** - JWT session management

- **Total Trustees (n)**: 9 trustees total3. **elections** - Election metadata (title, dates, threshold_t, total_trustees_n)

- **Curve**: Curve25519 (Ed25519 for signatures, X25519 for encryption)4. **candidates** - Election candidates with m_value for encryption

5. **trustees** - Trustee key shares for threshold decryption

**Key Generation (Distributed Key Generation - DKG)**:6. **votes** - Encrypted ballots

7. **ballots** - Vote commitments

1. **Setup Phase**:8. **bulletin_board_entries** - Public audit trail

   ```9. **mix_servers** - Mix-net for anonymity

   Each trustee i generates:10. **verification_codes** - Code sheets for voter verification

   - Private key share: ski ∈ Zq (random)11. **audit_logs** - System audit trail

   - Public key share: PKi = ski · G (G is generator)

   ```---



2. **Key Combination**:## 🛡️ Security Features

   ```

   Election Public Key: PK = ∑(i=1 to n) PKi### ✅ Implemented

   Private key (never computed): sk = ∑(i=1 to n) ski- **JWT Authentication** with 15-minute access tokens

   ```- **PostgreSQL** with parameterized queries (SQL injection prevention)

- **CORS** configured for localhost:5173

3. **Shamir Secret Sharing** (for threshold property):- **Password Hashing** with bcrypt (12 rounds)

   ```- **Admin Authorization** middleware

   Each trustee creates polynomial: Pi(x) = ski + a1·x + ... + a(t-1)·x^(t-1)- **Timezone-aware** token expiry (UTC)

   Sends shares to other trustees: sij = Pi(j)- **Error Handling** with proper HTTP status codes

   Each trustee's combined share: SKi = ∑(j=1 to n) sji

   ```### 🔜 Coming Soon

- WebAuthn biometric authentication

**Encryption (ElGamal)**:- RSA-2048 blind signature implementation

```- Threshold ElGamal encryption

To encrypt message m with public key PK:- Zero-knowledge proofs (Schnorr, Chaum-Pedersen)

1. Choose random r ∈ Zq- Mix-net with 7+ servers

2. Compute: C1 = r · G- TLS 1.3 with certificate pinning

3. Compute: C2 = m + r · PK

4. Ciphertext: (C1, C2)---

```

## 🧪 Testing

**Threshold Decryption**:

```### Current Status

Each trustee i computes partial decryption:- ✅ Auth service endpoints tested

   Di = SKi · C1- ✅ Election CRUD operations working

- ✅ Dashboard real-time stats working

To decrypt (need t=5 trustees):- ✅ KYC approval/rejection working

1. Use Lagrange interpolation on t partial decryptions- ✅ Candidate management working

2. Compute: D = ∑(i∈S) λi · Di  (S is set of t trustees)

3. Recover message: m = C2 - D### Test User

``````

Email: admin@securevote.com

**Lagrange Coefficient**:Password: Admin@123

``````

λi = ∏(j∈S, j≠i) [j / (j - i)]

```---



**Security Properties**:## 📝 Development Status

- **No Single Point of Failure**: Need t=5 trustees to decrypt

- **Collusion Resistance**: t-1=4 trustees cannot decrypt alone### ✅ Completed (MVP Phase 1)

- **Verifiability**: Each partial decryption can be verified- [x] Backend microservices architecture

- **Distributed Trust**: No single entity ever knows full private key- [x] PostgreSQL database schema

- [x] User authentication (password-based)

---- [x] Admin web dashboard

- [x] Election management (CRUD)

### 4. Zero-Knowledge Proofs (Schnorr Protocol)- [x] Candidate management

- [x] Voter management with KYC

**Purpose**: Prove vote is valid without revealing the vote- [x] Dashboard statistics

- [x] Real-time data from database

**Implemented Proofs**:

### 🚧 In Progress (Phase 2)

1. **Proof of Knowledge of Private Key**:- [ ] WebAuthn/FIDO2 implementation

   ```- [ ] RSA blind signatures

   Prover knows sk such that PK = sk · G- [ ] Threshold ElGamal key generation

   - [ ] Vote encryption/decryption

   Protocol:- [ ] Zero-knowledge proofs

   1. Prover: Choose random k, compute R = k · G- [ ] Mobile app (Flutter)

   2. Prover → Verifier: Send R

   3. Verifier → Prover: Send challenge c (random)### 📅 Planned (Phase 3)

   4. Prover: Compute s = k + c · sk- [ ] Mix-net implementation

   5. Prover → Verifier: Send s- [ ] Public bulletin board

   6. Verifier: Check s · G = R + c · PK- [ ] Code sheet PDF generation

   ```- [ ] Results tallying with threshold decryption

- [ ] End-to-end verification

2. **Proof of Ballot Validity** (Chaum-Pedersen):- [ ] Audit log visualization

   ```

   Prove encrypted vote is one of the candidates without revealing which---

   

   Given: Ciphertext (C1, C2), candidates {m1, m2, ..., mk}## 👥 Team Collaboration Guide

   Prove: ∃i such that C2 = mi + r · PK

   ### Git Workflow

   Uses OR-composition of Schnorr proofs```bash

   ```# Always pull latest before working

git pull origin main

**Security Properties**:

- **Zero-Knowledge**: Verifier learns nothing except validity# Create feature branch

- **Soundness**: Cannot prove false statementgit checkout -b feature/your-feature-name

- **Completeness**: Valid vote always accepted

# Make changes, commit frequently

---git add .

git commit -m "feat: descriptive message"

### 5. Bulletin Board (Hash Chain for Tamper Evidence)

# Push to remote

**Structure**: Blockchain-inspired append-only loggit push origin feature/your-feature-name



**Entry Format**:# Create Pull Request on GitHub

```json```

{

  "entry_id": "uuid",### Branch Naming Convention

  "sequence_number": 1,- `feature/` - New features

  "entry_type": "BALLOT_CAST",- `fix/` - Bug fixes

  "entry_hash": "SHA256(entry_data + previous_hash)",- `docs/` - Documentation updates

  "previous_hash": "hash of entry N-1",- `refactor/` - Code refactoring

  "entry_data": {

    "ballot_hash": "SHA256(encrypted_ballot)",### Commit Message Format

    "timestamp": "2025-10-28T10:30:00Z"```

  },feat: Add blind signature endpoint

  "timestamp": "2025-10-28T10:30:00Z"fix: Resolve timezone issue in token expiry

}docs: Update API documentation

```refactor: Simplify database connection logic

```

**Hash Chain Verification**:

```---

For each entry i:

1. Recompute: hash = SHA256(entry_data[i] + previous_hash[i])## 📞 Support & Contact

2. Verify: hash == entry_hash[i]

3. Verify: previous_hash[i] == entry_hash[i-1]**Group F:**

- MUNASINGHE S.K. - 210396E

If all checks pass → Chain is valid (not tampered)- JAYASOORIYA D.D.M. - 210250D

```

**Course:** Information Security & Cryptography  

**Entry Types Logged**:**Institution:** University of Moratuwa  

- `ELECTION_CREATED`: Election initialized**Date:** October 2025

- `KEY_GENERATED`: Trustee key ceremony completed

- `BALLOT_CAST`: Vote recorded (with ballot hash)---

- `ELECTION_CLOSED`: Voting period ended

- `TRUSTEE_SHARE`: Decryption share submitted## 📄 License

- `RESULT_PUBLISHED`: Final results announced

This is an academic project for course evaluation purposes.

**Security Properties**:

- **Tamper-Evidence**: Any modification breaks hash chain---

- **Append-Only**: Cannot delete or reorder entries

- **Public Verifiability**: Anyone can verify integrity## 🎓 References

- **Timestamp Integrity**: Cannot backdate entries

1. Helios Voting System - https://heliosvoting.org

---2. Swiss E-Voting Standards - https://www.post.ch/evoting

3. WebAuthn Specification - https://www.w3.org/TR/webauthn/

## 🛡️ Security Features4. Threshold Cryptography - Shamir Secret Sharing

5. Blind Signatures - Chaum 1983

### 1. Authentication & Authorization

---

**JWT (JSON Web Tokens)**:

- **Access Token**: 15-minute expiry, used for API requests**Last Updated:** October 26, 2025

- **Refresh Token**: 7-day expiry, stored in httpOnly cookies

- **Algorithm**: HS256 (HMAC-SHA256)### Project Overview

- **Payload**: `{user_id, is_admin, exp, iat}`This is a secure, end-to-end verifiable e-voting system implementing modern cryptographic protocols including WebAuthn/FIDO2 authentication, ECIES ballot encryption, threshold ElGamal homomorphic encryption, and mix-net privacy protection.



**Password Security**:**Group Members:**

- **Hashing**: bcrypt with 12 rounds (2^12 = 4096 iterations)- MUNASINGHE S.K. - 210396E

- **Salt**: Random 16-byte salt per password- JAYASOORIYA D.D.M. - 210250D

- **Minimum Requirements**: 8 characters, 1 uppercase, 1 lowercase, 1 number, 1 special

---

**WebAuthn/FIDO2** (Infrastructure Ready):

- Biometric authentication (TouchID, FaceID, fingerprint)## Table of Contents

- Hardware security keys supported1. [Tech Stack & Justification](#tech-stack--justification)

- Phishing-resistant authentication2. [Security Architecture](#security-architecture)

- Challenge-response protocol3. [System Architecture](#system-architecture)

4. [Project Structure](#project-structure)

---5. [Prerequisites](#prerequisites)

6. [Step-by-Step Implementation](#step-by-step-implementation)

### 2. Database Security7. [Deployment Guide](#deployment-guide)

8. [Testing & Verification](#testing--verification)

**Encryption at Rest**:9. [Security Measures](#security-measures)

- Sensitive fields (ballots, tokens) encrypted with AES-256

- Encryption keys stored in environment variables---

- Database password: StrongDatabase@201

## Tech Stack & Justification

**SQL Injection Prevention**:

- **All queries use parameterized statements**### Backend Services (Microservices Architecture)

- Example:**Technology:** Python FastAPI + PostgreSQL

  ```python

  # Vulnerable (NOT used):**Why FastAPI?**

  query = f"SELECT * FROM users WHERE email = '{email}'"- **Performance:** ASGI-based, async/await support for high concurrency

  - **Security:** Built-in OAuth2, JWT, and input validation

  # Secure (Used everywhere):- **Documentation:** Auto-generated OpenAPI documentation

  query = text("SELECT * FROM users WHERE email = :email")- **Type Safety:** Pydantic models prevent injection attacks

  db.execute(query, {"email": email})- **Microservices Ready:** Easy service isolation for security boundaries

  ```

**Why PostgreSQL?**

**Access Control**:- **ACID Compliance:** Critical for election data integrity

- Service-specific database users (principle of least privilege)- **Strong Security:** Row-level security, SSL connections, audit logging

- Row-Level Security (RLS) policies- **Cryptographic Extensions:** pgcrypto for additional security layers

- Audit logging of all database access- **Reliability:** Battle-tested for critical applications



---### Mobile Application

**Technology:** Flutter (Dart)

### 3. Network Security

**Why Flutter?**

**CORS (Cross-Origin Resource Sharing)**:- **Cross-Platform:** Single codebase for iOS & Android (cost-effective for MVP)

- **Development**: Allow localhost:5173 (admin web)- **Security:** Secure storage plugins, biometric authentication support

- **Production**: Strict origin whitelist- **Cryptography:** pointycastle library for client-side encryption

- **Credentials**: Allow cookies with `allow_credentials=true`- **Performance:** Compiled to native code

- **UI/UX:** Material Design and Cupertino widgets for native feel

**Rate Limiting** (Application Level):

- **Login attempts**: 5 per IP per 15 minutes### Admin Web Platform

- **Vote submissions**: 1 per user per election**Technology:** React.js + TypeScript + Material-UI

- **Token requests**: 1 per user per election

**Why React?**

**TLS/HTTPS** (Production):- **Component Reusability:** Faster development of admin features

- TLS 1.3 with forward secrecy- **TypeScript:** Type safety prevents common vulnerabilities

- Certificate pinning in mobile app- **Ecosystem:** Rich cryptography libraries (Web Crypto API, elliptic.js)

- HSTS headers (Strict-Transport-Security)- **Security:** Virtual DOM prevents XSS attacks

- **State Management:** Redux for complex election management workflows

---

### Cryptography Libraries

### 4. Application Security

**Backend (Python):**

**Input Validation**:- **cryptography:** Industry-standard, maintained by PyCA

- **Pydantic Models**: Automatic type checking and validation- **pynacl:** libsodium bindings for modern cryptography

- **Email Validation**: RFC 5322 compliant- **ecdsa:** Elliptic curve signatures (Ed25519)

- **UUID Validation**: Proper UUID format checking- **Justification:** FIPS 140-2 validated, constant-time implementations

- **Date Validation**: ISO 8601 format

**Frontend (Flutter):**

**Error Handling**:- **pointycastle:** Pure Dart crypto library

- Generic error messages to prevent information leakage- **crypto:** Dart's official crypto package

- Detailed logs for debugging (not exposed to clients)- **Justification:** No native dependencies, cross-platform compatibility

- HTTP status codes: 401 (auth), 403 (forbidden), 404 (not found), 500 (server error)

**Web Admin (React):**

**Audit Trail**:- **Web Crypto API:** Browser-native, hardware-accelerated

- Every critical operation logged to `audit_logs` table- **elliptic:** Pure JavaScript ECC implementation

- Fields: event_type, user_id, resource_type, resource_id, ip_address, metadata, severity, timestamp- **Justification:** Secure, audited, widely used

- Tamper-evident with bulletin board cross-referencing

### Infrastructure & DevOps

---- **Docker + Docker Compose:** Service isolation and reproducible deployments

- **Nginx:** Reverse proxy with TLS 1.3 termination

### 5. Cryptographic Guarantees- **GitHub Actions:** CI/CD with automated security scanning



| Property | Implementation | Guarantee |---

|----------|---------------|-----------|

| **Ballot Secrecy** | ECIES (X25519 + AES-256-GCM) | IND-CCA2 secure |## Security Architecture

| **Voter Anonymity** | RSA Blind Signatures | Unlinkable |

| **Vote Integrity** | GCM Authentication Tag | Tamper-proof |### 1. Transport Security

| **Distributed Trust** | Threshold ElGamal (t=5, n=9) | No single point of failure |- **TLS 1.3** with forward secrecy

| **Verifiability** | Hash Chain + ZKPs | Publicly auditable |- **Certificate Pinning** in mobile app

| **Forward Secrecy** | Ephemeral X25519 keys | Past messages secure |- **HSTS** headers on all web endpoints



---### 2. Authentication & Authorization

- **WebAuthn/FIDO2** for passwordless authentication

## 💻 Technology Stack- **Biometric Verification** (TouchID, FaceID, fingerprint)

- **JWT Tokens** with short expiry (15 minutes)

### Backend- **Refresh Tokens** in httpOnly cookies

- **Language**: Python 3.13- **Why:** Phishing-resistant, no password database to breach

- **Framework**: FastAPI (ASGI, async/await)

- **Database**: PostgreSQL 18### 3. Ballot Encryption (Privacy)

- **ORM**: SQLAlchemy 2.0- **ECIES (Elliptic Curve Integrated Encryption Scheme)**

- **Cryptography**:   - Key Agreement: X25519

  - `cryptography` (PyCA) - ECIES, X25519, AES-GCM  - Symmetric: AES-256-GCM

  - `pynacl` (libsodium) - Ed25519, Blake2b  - KDF: HKDF-SHA256

  - `rsa` - RSA-2048 blind signatures- **Why:** Ensures ballot secrecy, prevents server from reading votes

  - `hashlib` - SHA-256, SHA-512

- **Authentication**: JWT (PyJWT), bcrypt### 4. Homomorphic Tallying

- **API Documentation**: OpenAPI/Swagger (auto-generated)- **Threshold ElGamal on Curve25519**

- **Threshold:** t=5 of n=9 trustees

### Frontend - Admin Web- **Why:** No single entity can decrypt votes, enables encrypted tallying

- **Framework**: React 18 + TypeScript

- **UI Library**: Material-UI (MUI) v5### 5. Anonymity Protection

- **State Management**: Redux Toolkit- **Blind Signatures** for anonymous credentials

- **HTTP Client**: Axios- **Mix-Net** with 7+ servers for vote shuffling

- **Routing**: React Router v6- **Zero-Knowledge Proofs** for ballot validity

- **Build Tool**: Vite- **Why:** Breaks link between voter identity and ballot

- **Deployment**: Port 5173 (dev), Nginx (prod)

### 6. Verifiability

### Frontend - Mobile App- **Individual Verifiability:** Ed25519 signatures on vote receipts

- **Framework**: Flutter 3.16+ (Dart)- **Universal Verifiability:** Public bulletin board with hash chain

- **State Management**: Provider- **Why:** Voters can verify their vote was counted, anyone can audit results

- **Cryptography**: pointycastle (pure Dart)

- **Secure Storage**: flutter_secure_storage (Keychain/Keystore)### 7. Database Security

- **HTTP Client**: http package- **Encryption at Rest:** AES-256 for sensitive fields

- **Biometrics**: local_auth package- **Prepared Statements:** Prevents SQL injection

- **Row-Level Security:** Postgres RLS policies

### Infrastructure- **Audit Logging:** All access logged with timestamps

- **Containerization**: Docker + Docker Compose (for production)

- **Reverse Proxy**: Nginx (for production)### 8. Application Security

- **CI/CD**: GitHub Actions (optional)- **Input Validation:** Pydantic models, schema validation

- **Monitoring**: Application-level logging- **Rate Limiting:** Redis-based, prevents DoS

- **CORS:** Strict origin policies

---- **CSP Headers:** Prevents XSS attacks

- **Dependency Scanning:** Automated vulnerability checks

## 🚀 Getting Started

---

### Prerequisites

## System Architecture

1. **Python 3.13+** installed

2. **Node.js 20+** and npm installed```

3. **PostgreSQL 18** installed and running┌─────────────────────────────────────────────────────────────────┐

4. **Flutter 3.16+** (for mobile app development)│                        Client Layer                              │

5. **Git** for version control├─────────────────────────────┬───────────────────────────────────┤

│   Flutter Mobile App        │   React Admin Web App             │

### Installation Steps│   (Voter Interface)         │   (Admin Dashboard)               │

│   - Biometric Auth          │   - Election Management           │

#### 1. Database Setup│   - Ballot Encryption       │   - Trustee Coordination          │

│   - Vote Verification       │   - Results Visualization         │

```powershell└──────────────┬──────────────┴────────────────┬──────────────────┘

# Start PostgreSQL (Windows Service or pg_ctl)               │                                │

Get-Service postgresql* | Start-Service               │        TLS 1.3 + Cert Pinning │

               │                                │

# Create database┌──────────────┴────────────────────────────────┴──────────────────┐

psql -U postgres -c "CREATE DATABASE evoting_db;"│                     API Gateway (Nginx)                           │

│              - TLS Termination                                    │

# Initialize schema│              - Rate Limiting                                      │

cd "d:\Dulithi\Semester 7\crypto-project\e-voting-system"│              - Load Balancing                                     │

psql -U postgres -d evoting_db -f scripts/db-init.sql└──────────────┬────────────────────────────────────────────────────┘

               │

# Create admin user    ┌──────────┴──────────┐

psql -U postgres -d evoting_db -c "    │   FastAPI Services  │

INSERT INTO users (nic, email, full_name, date_of_birth, is_admin, kyc_status, password_hash)    │   (Microservices)   │

VALUES ('ADMIN001', 'admin@securevote.com', 'System Admin', '1990-01-01', true, 'APPROVED', '\$2b\$12\$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzNx7Z7rMu');    └──────────┬──────────┘

"               │

# Password: Admin@123┌──────────────┴────────────────────────────────────────────────┐

```│                   Service Layer                                │

├───────────────┬──────────────┬──────────────┬─────────────────┤

#### 2. Backend Services Setup│  Auth Service │ Token Service│ Vote Service │ Bulletin Board  │

│               │              │              │   Service       │

**Set Database Password**:│  - WebAuthn   │ - Blind Sig  │ - ZK Verify  │ - Hash Chain   │

```powershell│  - KYC        │ - Anonymous  │ - Encrypted  │ - Public Audit │

# Update in each service's .env or set as environment variable│  - JWT        │   Credential │   Storage    │                │

$env:DATABASE_URL="postgresql://postgres:StrongDatabase@201@localhost:5432/evoting_db"└───────┬───────┴──────┬───────┴──────┬───────┴────────┬────────┘

```        │              │              │                │

┌──────────────┴────────────────────────────────────────────────┐

**Start Auth Service (Port 8001)**:│                    Data Layer                                  │

```powershell├────────────────────┬───────────────────────────────────────────┤

cd backend/auth-service│   PostgreSQL       │              File Storage                 │

python -m venv venv│   - Users          │           - Code Sheets                   │

.\venv\Scripts\Activate│   - Elections      │           - Audit Logs                    │

pip install -r requirements.txt│   - Ballots        │                                           │

uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload│   - Trustees       │                                           │

```│   - Sessions       │                                           │

└────────────────────┴───────────────────────────────────────────┘

**Start Election Service (Port 8005)**:```

```powershell

cd backend/election-service### Service Isolation

python -m venv venvEach microservice runs in a separate container with:

.\venv\Scripts\Activate- Dedicated database schema

pip install -r requirements.txt- Service-specific API keys

uvicorn app.main:app --host 0.0.0.0 --port 8005 --reload- Network isolation (internal Docker network)

```- Resource limits (CPU, memory)



**Start Token Service (Port 8002)**:---

```powershell

cd backend/token-service## Project Structure

python -m venv venv

.\venv\Scripts\Activate```

pip install -r requirements.txte-voting-system/

uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload├── backend/

```│   ├── auth-service/

│   │   ├── app/

**Start Vote Service (Port 8003)**:│   │   │   ├── api/

```powershell│   │   │   │   ├── routes/

cd backend/vote-service│   │   │   │   │   ├── auth.py

python -m venv venv│   │   │   │   │   ├── kyc.py

.\venv\Scripts\Activate│   │   │   │   │   └── webauthn.py

pip install -r requirements.txt│   │   │   │   └── dependencies.py

uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload│   │   │   ├── models/

```│   │   │   │   ├── user.py

│   │   │   │   └── session.py

**Start Bulletin Board Service (Port 8004)**:│   │   │   ├── schemas/

```powershell│   │   │   │   └── auth_schemas.py

cd backend/bulletin-board-service│   │   │   ├── services/

python -m venv venv│   │   │   │   ├── auth_service.py

.\venv\Scripts\Activate│   │   │   │   └── webauthn_service.py

pip install -r requirements.txt│   │   │   ├── utils/

uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload│   │   │   │   ├── crypto.py

```│   │   │   │   └── jwt_handler.py

│   │   │   ├── config.py

**Start Code Sheet Service (Port 8006)**:│   │   │   └── main.py

```powershell│   │   ├── tests/

cd backend/code-sheet-service│   │   ├── Dockerfile

python -m venv venv│   │   └── requirements.txt

.\venv\Scripts\Activate│   │

pip install -r requirements.txt│   ├── token-service/

uvicorn app.main:app --host 0.0.0.0 --port 8006 --reload│   │   ├── app/

```│   │   │   ├── api/

│   │   │   │   └── routes/

#### 3. Admin Web Setup│   │   │   │       └── blind_signing.py

│   │   │   ├── models/

```powershell│   │   │   │   └── token.py

cd admin-web│   │   │   ├── services/

npm install│   │   │   │   └── blind_signature_service.py

npm run dev│   │   │   ├── utils/

```│   │   │   │   └── blind_crypto.py

Access at: http://localhost:5173│   │   │   └── main.py

│   │   ├── Dockerfile

#### 4. Mobile App Setup│   │   └── requirements.txt

│   │

```powershell│   ├── vote-service/

cd mobile-app│   │   ├── app/

│   │   │   ├── api/

# Update API URL in lib/services/api_service.dart│   │   │   │   └── routes/

# Change baseUrl to your computer's IP address (e.g., http://192.168.1.100)│   │   │   │       └── vote_submission.py

│   │   │   ├── models/

flutter pub get│   │   │   │   └── ballot.py

flutter run│   │   │   ├── services/

```│   │   │   │   ├── vote_service.py

│   │   │   │   └── zkp_service.py

### Default Login Credentials│   │   │   ├── utils/

│   │   │   │   ├── elgamal.py

**Admin Web**:│   │   │   │   └── zkp.py

- Email: admin@securevote.com│   │   │   └── main.py

- Password: Admin@123│   │   ├── Dockerfile

│   │   └── requirements.txt

**Mobile App**:│   │

- Register a new voter account│   ├── bulletin-board-service/

- Wait for KYC approval from admin│   │   ├── app/

│   │   │   ├── api/

---│   │   │   │   └── routes/

│   │   │   │       └── bulletin.py

## 📁 Project Structure│   │   │   ├── models/

│   │   │   │   └── bulletin_entry.py

```│   │   │   ├── services/

e-voting-system/│   │   │   │   └── hash_chain_service.py

├── backend/│   │   │   └── main.py

│   ├── auth-service/                 # Port 8001 - Authentication & KYC│   │   ├── Dockerfile

│   │   ├── app/│   │   └── requirements.txt

│   │   │   ├── api/routes/│   │

│   │   │   │   ├── auth.py          # Register, login, refresh│   ├── election-service/

│   │   │   │   ├── users.py         # User management│   │   ├── app/

│   │   │   │   ├── kyc.py           # KYC approval│   │   │   ├── api/

│   │   │   │   └── webauthn.py      # WebAuthn (infrastructure)│   │   │   │   └── routes/

│   │   │   ├── models/│   │   │   │       ├── election.py

│   │   │   ├── config.py│   │   │   │       └── trustee.py

│   │   │   └── main.py│   │   │   ├── models/

│   │   └── requirements.txt│   │   │   │   ├── election.py

│   ││   │   │   │   └── trustee.py

│   ├── token-service/                # Port 8002 - Blind Signatures│   │   │   ├── services/

│   │   ├── app/│   │   │   │   ├── election_service.py

│   │   │   ├── api/routes/│   │   │   │   └── threshold_crypto_service.py

│   │   │   │   └── blind_signing.py # RSA blind signature│   │   │   └── main.py

│   │   │   ├── utils/│   │   ├── Dockerfile

│   │   │   │   └── blind_signature.py│   │   └── requirements.txt

│   │   │   └── main.py│   │

│   │   └── requirements.txt│   ├── code-sheet-service/

│   ││   │   ├── app/

│   ├── vote-service/                 # Port 8003 - Vote Submission│   │   │   ├── api/

│   │   ├── app/│   │   │   │   └── routes/

│   │   │   ├── api/routes/│   │   │   │       └── code_sheet.py

│   │   │   │   └── vote_submission.py # Vote + ZKP verification│   │   │   ├── services/

│   │   │   └── main.py│   │   │   │   └── pdf_generator.py

│   │   └── requirements.txt│   │   │   └── main.py

│   ││   │   ├── Dockerfile

│   ├── bulletin-board-service/       # Port 8004 - Public Bulletin│   │   └── requirements.txt

│   │   ├── app/│   │

│   │   │   ├── api/routes/│   ├── shared/

│   │   │   │   └── bulletin.py      # Hash chain operations│   │   ├── database.py

│   │   │   └── main.py│   │   ├── security.py

│   │   └── requirements.txt│   │   └── constants.py

│   ││   │

│   ├── election-service/             # Port 8005 - Election Management│   └── docker-compose.yml

│   │   ├── app/│

│   │   │   ├── api/routes/├── mobile-app/

│   │   │   │   ├── election.py      # CRUD, tally, results│   ├── android/

│   │   │   │   └── trustee.py       # Key ceremony, decryption│   ├── ios/

│   │   │   └── main.py│   ├── lib/

│   │   └── requirements.txt│   │   ├── main.dart

│   ││   │   ├── core/

│   ├── code-sheet-service/           # Port 8006 - Voting Codes│   │   │   ├── config/

│   │   ├── app/│   │   │   │   └── app_config.dart

│   │   │   ├── api/routes/│   │   │   ├── network/

│   │   │   │   └── code_sheet.py    # Generate codes│   │   │   │   └── api_client.dart

│   │   │   └── main.py│   │   │   └── utils/

│   │   └── requirements.txt│   │   │       ├── crypto_utils.dart

│   ││   │   │       └── secure_storage.dart

│   └── shared/                       # Shared utilities│   │   ├── features/

│       ├── database.py               # SQLAlchemy connection│   │   │   ├── auth/

│       ├── security.py               # JWT utilities│   │   │   │   ├── data/

│       ├── constants.py              # App constants│   │   │   │   ├── domain/

│       ├── crypto_utils.py           # Crypto helpers│   │   │   │   └── presentation/

│       ├── bulletin_helper.py        # Bulletin board integration│   │   │   │       ├── pages/

│       ├── audit_helper.py           # Audit logging│   │   │   │       │   ├── login_page.dart

│       └── threshold_crypto.py       # Threshold ElGamal│   │   │   │       │   ├── register_page.dart

││   │   │   │       │   └── kyc_page.dart

├── admin-web/                        # React Admin Dashboard│   │   │   │       └── widgets/

│   ├── src/│   │   │   ├── voting/

│   │   ├── components/│   │   │   │   ├── data/

│   │   │   └── Layout.tsx           # Main layout with sidebar│   │   │   │   ├── domain/

│   │   ├── pages/│   │   │   │   └── presentation/

│   │   │   ├── Dashboard.tsx        # Statistics overview│   │   │   │       ├── pages/

│   │   │   ├── Elections.tsx        # Election list│   │   │   │       │   ├── election_list_page.dart

│   │   │   ├── ElectionDetails.tsx  # Single election view│   │   │   │       │   ├── voting_page.dart

│   │   │   ├── VotingCodes.tsx      # Code management│   │   │   │       │   └── verification_page.dart

│   │   │   ├── BulletinBoard.tsx    # Public bulletin│   │   │   │       └── widgets/

│   │   │   ├── Voters.tsx           # Voter management│   │   │   └── profile/

│   │   │   ├── Results.tsx          # Election results│   │   │       └── presentation/

│   │   │   └── Login.tsx            # Admin login│   │   │           └── pages/

│   │   ├── services/│   │   │               └── profile_page.dart

│   │   │   └── api.ts               # API clients│   │   └── shared/

│   │   ├── store/│   │       └── widgets/

│   │   │   └── store.ts             # Redux store│   ├── test/

│   │   ├── App.tsx│   ├── pubspec.yaml

│   │   └── main.tsx│   └── README.md

│   ├── package.json│

│   └── vite.config.ts├── admin-web/

││   ├── public/

├── mobile-app/                       # Flutter Mobile App│   ├── src/

│   ├── lib/│   │   ├── components/

│   │   ├── main.dart│   │   │   ├── common/

│   │   ├── services/│   │   │   ├── elections/

│   │   │   ├── api_service.dart     # Backend API client│   │   │   │   ├── ElectionForm.tsx

│   │   │   ├── crypto_service.dart  # Cryptography (ECIES, blind sig)│   │   │   │   ├── ElectionList.tsx

│   │   │   └── storage_service.dart # Secure storage│   │   │   │   └── ElectionDetails.tsx

│   │   ├── providers/│   │   │   ├── trustees/

│   │   │   ├── auth_provider.dart   # Auth state│   │   │   │   ├── TrusteeManagement.tsx

│   │   │   └── election_provider.dart # Election state│   │   │   │   └── KeyGeneration.tsx

│   │   └── screens/│   │   │   ├── voters/

│   │       ├── login_screen.dart│   │   │   │   ├── VoterList.tsx

│   │       ├── register_screen.dart│   │   │   │   └── KYCVerification.tsx

│   │       ├── home_screen.dart     # Election list│   │   │   └── results/

│   │       ├── vote_screen.dart     # Voting interface│   │   │       ├── ResultsDashboard.tsx

│   │       └── receipt_screen.dart  # Vote receipt + QR│   │   │       └── AuditLog.tsx

│   ├── android/│   │   ├── services/

│   ├── ios/│   │   │   ├── api.ts

│   └── pubspec.yaml│   │   │   ├── crypto.ts

││   │   │   └── auth.ts

├── scripts/│   │   ├── store/

│   └── db-init.sql                  # Complete database schema│   │   │   ├── store.ts

││   │   │   └── slices/

└── README.md                        # This file│   │   ├── utils/

```│   │   │   └── crypto-helpers.ts

│   │   ├── App.tsx

---│   │   └── index.tsx

│   ├── package.json

## 📚 API Documentation│   ├── tsconfig.json

│   └── README.md

### Auth Service (http://localhost:8001)│

├── infrastructure/

**POST /api/auth/register**│   ├── nginx/

```json│   │   ├── nginx.conf

{│   │   └── ssl/

  "nic": "123456789V",│   ├── docker/

  "email": "voter@example.com",│   │   └── docker-compose.prod.yml

  "full_name": "John Doe",│   └── kubernetes/

  "date_of_birth": "1995-01-01",│       ├── deployments/

  "password": "SecurePass@123"│       └── services/

}│

```├── docs/

Response: `{ "access_token": "...", "refresh_token": "..." }`│   ├── API_DOCUMENTATION.md

│   ├── SECURITY_ANALYSIS.md

**POST /api/auth/login**│   ├── DEPLOYMENT_GUIDE.md

```json│   └── USER_MANUAL.md

{│

  "email": "voter@example.com",├── tests/

  "password": "SecurePass@123"│   ├── integration/

}│   ├── security/

```│   └── performance/

Response: `{ "access_token": "...", "refresh_token": "..." }`│

├── scripts/

**GET /api/auth/me**│   ├── setup.sh

Headers: `Authorization: Bearer {access_token}`│   ├── db-init.sql

Response: User profile with KYC status│   └── generate-keys.py

│

**GET /api/users/list** (Admin only)├── .github/

Response: Array of all users│   └── workflows/

│       ├── ci.yml

**POST /api/users/kyc/approve/{user_id}** (Admin only)│       └── security-scan.yml

Response: `{ "message": "KYC approved", "kyc_status": "APPROVED" }`│

├── docker-compose.yml

---├── .env.example

├── .gitignore

### Election Service (http://localhost:8005)└── README.md

```

**POST /api/election/create** (Admin only)

```json---

{

  "title": "2025 University Council Election",## Prerequisites

  "description": "Annual election",

  "start_time": "2025-11-01T09:00:00Z",### Development Environment

  "end_time": "2025-11-01T17:00:00Z",1. **Operating System:** Windows 10/11, macOS, or Linux

  "threshold_t": 5,2. **Docker Desktop:** Version 20.10+

  "total_trustees_n": 93. **Docker Compose:** Version 2.0+

}4. **Git:** Latest version

```

Response: `{ "election_id": "uuid" }`### Backend Development

1. **Python:** 3.11+

**GET /api/election/list**2. **pip:** Latest version

Response: Array of all elections3. **Virtual Environment:** venv or conda



**GET /api/election/{election_id}**### Mobile Development

Response: Election details with candidates1. **Flutter SDK:** 3.16+

2. **Android Studio:** Latest (for Android development)

**POST /api/election/candidate/add** (Admin only)3. **Xcode:** Latest (for iOS development, macOS only)

```json4. **Android SDK:** API Level 33+

{5. **iOS Simulator:** iOS 15+ (macOS only)

  "election_id": "uuid",

  "name": "Alice Perera",### Web Development

  "party": "Independent",1. **Node.js:** 20 LTS+

  "display_order": 12. **npm or yarn:** Latest version

}3. **Web Browser:** Chrome/Firefox (with dev tools)

```

### Database

**PUT /api/election/{election_id}/status** (Admin only)1. **PostgreSQL:** 15+ (via Docker)

```json

{ "status": "ACTIVE" }### Optional (Recommended)

```1. **Postman:** API testing

Valid statuses: DRAFT, ACTIVE, CLOSED, TALLIED2. **VS Code:** With Flutter, Python extensions

3. **pgAdmin:** Database management GUI

**POST /api/election/{election_id}/tally** (Admin only)

Triggers decryption and vote counting. Requires t=5 trustees to have submitted decryption shares.---



**GET /api/election/{election_id}/results**## Step-by-Step Implementation

Response: Vote counts per candidate with percentages

### Phase 1: Environment Setup (Days 1-2)

---

#### Step 1.1: Clone and Initialize Project

### Token Service (http://localhost:8002)```bash

# Create project directory

**POST /api/token/request-signature**mkdir e-voting-system

```jsoncd e-voting-system

{

  "election_id": "uuid",# Initialize git

  "user_id": "uuid",git init

  "blinded_token": "base64_encoded_blinded_value"git branch -M main

}```

```

Response: `{ "blinded_signature": "base64_encoded", "public_key_n": "..." }`#### Step 1.2: Create .gitignore

Create `.gitignore` in root directory (already included in structure)

**GET /api/token/public-key**

Response: Server's RSA public key for blind signature verification#### Step 1.3: Environment Variables

Create `.env.example` with all required variables (see separate file)

---

#### Step 1.4: Docker Setup

### Vote Service (http://localhost:8003)Create `docker-compose.yml` for development environment



**POST /api/vote/submit**---

```json

{### Phase 2: Backend Core Services (Days 3-7)

  "election_id": "uuid",

  "encrypted_vote": {#### Step 2.1: Database Schema Design

    "ephemeral_public_key": "hex",Create `scripts/db-init.sql` with complete schema

    "ciphertext": "hex",

    "nonce": "hex",#### Step 2.2: Shared Utilities

    "tag": "hex"Implement shared cryptographic primitives:

  },- X25519 key agreement

  "proof": {- Ed25519 signatures

    "voter_public_key": "hex",- HKDF key derivation

    "commitment": "hex"- AES-256-GCM encryption

  },

  "token_hash": "hex",#### Step 2.3: Authentication Service

  "token_signature": "base64",Implement:

  "candidate_id": "uuid"1. User registration endpoint

}2. WebAuthn registration/authentication

```3. KYC submission

Response: `{ "ballot_hash": "hex", "verification_code": "hex", "vote_hash": "hex" }`4. JWT token generation

5. Session management

---

#### Step 2.4: Token Service (Blind Signatures)

### Bulletin Board Service (http://localhost:8004)Implement:

1. Anonymous token request

**GET /api/bulletin/{election_id}/chain**2. Blind signature generation

Response: Complete hash chain for election (all entries)3. Token verification



**GET /api/bulletin/{election_id}/verify**#### Step 2.5: Vote Service

Response: `{ "valid": true/false, "message": "...", "total_entries": 123 }`Implement:

1. Encrypted ballot submission

**GET /api/bulletin/{election_id}/summary**2. Zero-knowledge proof verification

Response: Statistics by entry type3. Ballot storage



---#### Step 2.6: Bulletin Board Service

Implement:

### Code Sheet Service (http://localhost:8006)1. Hash chain maintenance

2. Public ballot posting

**POST /api/code-sheet/generate-bulk**3. Audit trail generation

```json

{ "election_id": "uuid" }#### Step 2.7: Election Service

```Implement:

Response: Array of voting codes for all KYC-approved voters1. Election CRUD operations

2. Trustee management

**GET /api/code-sheet/election/{election_id}**3. Threshold key generation

Response: All codes for election4. Results tallying



------



## ✅ Implemented Features### Phase 3: Mobile Application (Days 8-12)



### Fully Functional#### Step 3.1: Project Setup

```bash

#### Backend (100% Complete)cd mobile-app

- ✅ User authentication (JWT, bcrypt)flutter create .

- ✅ KYC approval workflowflutter pub get

- ✅ Election CRUD operations```

- ✅ Candidate management with display order

- ✅ Threshold trustee management (t=5, n=9)#### Step 3.2: Dependencies

- ✅ Key ceremony for distributed key generationAdd to `pubspec.yaml`:

- ✅ RSA-2048 blind signature token issuance- http: API calls

- ✅ ECIES ballot encryption support- flutter_secure_storage: Secure key storage

- ✅ Vote submission with anonymous tokens- local_auth: Biometric authentication

- ✅ Double-vote prevention- pointycastle: Cryptography

- ✅ Trustee decryption share submission- provider: State management

- ✅ Threshold decryption and tallying

- ✅ Results calculation with percentages#### Step 3.3: Core Features

- ✅ Voting code generation (bulk & individual)1. **Authentication Flow**

- ✅ Bulletin board with SHA-256 hash chaining   - Login screen with biometric

- ✅ Chain integrity verification   - Registration with KYC

- ✅ Comprehensive audit trail logging   - Session management

- ✅ API documentation (Swagger UI at /api/docs)

2. **Voting Flow**

#### Admin Web (100% Complete)   - Election list

- ✅ Admin login with JWT authentication   - Candidate selection

- ✅ Dashboard with real-time statistics   - Main code entry

- ✅ Election management (create, edit, activate, close)   - Ballot encryption

- ✅ Candidate management (add, edit, remove)   - Vote submission

- ✅ Voter management (view, KYC approve/reject)   - Verification

- ✅ Trustee key ceremony coordination

- ✅ Trustee decryption share collection3. **Profile**

- ✅ Election tallying and results display   - User information

- ✅ Voting code generation and CSV export   - Vote history

- ✅ Bulletin board visualization with chain verification   - Verification receipts

- ✅ Material-UI responsive design

- ✅ Redux state management---



#### Mobile App (100% Complete)### Phase 4: Admin Web Application (Days 13-16)

- ✅ User registration and login

- ✅ JWT token management with secure storage#### Step 4.1: Project Setup

- ✅ X25519 keypair generation (per user)```bash

- ✅ ECIES vote encryption (X25519 + AES-256-GCM)cd admin-web

- ✅ RSA blind signature client implementationnpx create-react-app . --template typescript

- ✅ Election listing (active & past)npm install

- ✅ Candidate viewing with display order```

- ✅ Secure vote casting

- ✅ Vote receipt with QR code#### Step 4.2: Dependencies

- ✅ Receipt verification details- @mui/material: UI components

- ✅ KYC status display- axios: HTTP client

- ✅ Material Design 3 UI- redux-toolkit: State management

- ✅ Secure key storage (Keychain on iOS, Keystore on Android)- elliptic: Cryptography

- recharts: Data visualization

---

#### Step 4.3: Core Features

### Cryptographic Components1. **Election Management**

   - Create elections

| Component | Status | Algorithm | Implementation |   - Add candidates

|-----------|--------|-----------|----------------|   - Configure election parameters

| Ballot Encryption | ✅ Complete | ECIES (X25519 + AES-256-GCM) | Mobile app + Vote service |

| Blind Signatures | ✅ Complete | RSA-2048 | Token service + Mobile app |2. **Trustee Coordination**

| Threshold Keys | ✅ Complete | ElGamal on Curve25519 (t=5, n=9) | Election service |   - Key generation ceremony

| Zero-Knowledge Proofs | ⚠️ MVP | Commitment (Schnorr planned) | Mobile app + Vote service |   - Partial decryption collection

| Hash Chain | ✅ Complete | SHA-256 | Bulletin board service |   - Result computation

| Password Hashing | ✅ Complete | bcrypt (12 rounds) | Auth service |

| JWT Tokens | ✅ Complete | HS256 (HMAC-SHA256) | Auth service |3. **Voter Management**

| Key Derivation | ✅ Complete | HKDF-SHA256 | Mobile app crypto service |   - KYC verification

   - Voter list management

---   - Code sheet generation



## 🗄️ Database Schema4. **Results & Auditing**

   - Live vote counting

### Core Tables (11 tables)   - Results visualization

   - Audit log viewing

1. **users** - Voter and admin accounts

   ```sql---

   user_id UUID PRIMARY KEY

   nic VARCHAR(12) UNIQUE### Phase 5: Integration & Testing (Days 17-19)

   email VARCHAR UNIQUE

   full_name VARCHAR#### Step 5.1: End-to-End Testing

   date_of_birth DATE1. Complete voter journey

   phone_number VARCHAR2. Admin workflows

   password_hash VARCHAR3. Trustee operations

   public_key TEXT  -- X25519 public key

   is_admin BOOLEAN DEFAULT false#### Step 5.2: Security Testing

   is_active BOOLEAN DEFAULT true1. Penetration testing

   kyc_status VARCHAR CHECK IN ('PENDING', 'APPROVED', 'REJECTED')2. Cryptographic verification

   kyc_document_path VARCHAR3. API security testing

   last_login_at TIMESTAMP

   created_at TIMESTAMP#### Step 5.3: Performance Testing

   updated_at TIMESTAMP1. Load testing (concurrent voters)

   ```2. Database optimization

3. API response times

2. **elections** - Election metadata

   ```sql---

   election_id UUID PRIMARY KEY

   title VARCHAR### Phase 6: Documentation & Deployment (Days 20-21)

   description TEXT

   start_time TIMESTAMP#### Step 6.1: Documentation

   end_time TIMESTAMP1. API documentation (OpenAPI/Swagger)

   status VARCHAR CHECK IN ('DRAFT', 'ACTIVE', 'CLOSED', 'TALLIED')2. User manuals

   threshold_t INT  -- Minimum trustees needed3. Security analysis report

   total_trustees_n INT  -- Total trustees4. Deployment guide

   public_key TEXT  -- Election public key (after key ceremony)

   created_by UUID REFERENCES users#### Step 6.2: Production Deployment

   created_at TIMESTAMP1. SSL/TLS certificate setup

   updated_at TIMESTAMP2. Production environment configuration

   ```3. Database backups

4. Monitoring setup

3. **candidates** - Election candidates

   ```sql---

   candidate_id UUID PRIMARY KEY

   election_id UUID REFERENCES elections## Deployment Guide

   name VARCHAR

   party VARCHAR### Development Deployment

   display_order INT  -- Order on ballot```bash

   created_at TIMESTAMP# Start all services

   ```docker-compose up -d



4. **trustees** - Threshold decryption trustees# Check service health

   ```sqldocker-compose ps

   trustee_id UUID PRIMARY KEY

   election_id UUID REFERENCES elections# View logs

   user_id UUID REFERENCES usersdocker-compose logs -f [service-name]

   public_key_share TEXT  -- Trustee's public key share

   shares_submitted BOOLEAN DEFAULT false# Run mobile app

   shares_submitted_at TIMESTAMPcd mobile-app

   decryption_shares JSONB  -- Partial decryptions per ballotflutter run

   created_at TIMESTAMP

   ```# Run admin web

cd admin-web

5. **ballots** - Encrypted votesnpm start

   ```sql```

   ballot_id UUID PRIMARY KEY

   election_id UUID REFERENCES elections### Production Deployment

   encrypted_ballot BYTEA  -- ECIES ciphertextSee `docs/DEPLOYMENT_GUIDE.md` for detailed production deployment instructions.

   zkp_proof JSONB  -- Zero-knowledge proof

   ballot_signature BYTEA  -- Anonymous token signature---

   ballot_hash VARCHAR  -- SHA-256 hash

   verification_code VARCHAR  -- 8-char hex code## Testing & Verification

   token_hash VARCHAR REFERENCES anonymous_tokens

   cast_at TIMESTAMP### Security Verification Checklist

   ```- [ ] TLS 1.3 configured correctly

- [ ] Certificate pinning working in mobile app

6. **anonymous_tokens** - Blind signed tokens- [ ] WebAuthn properly implemented

   ```sql- [ ] Ballot encryption verified

   token_id UUID PRIMARY KEY- [ ] Blind signatures working

   election_id UUID REFERENCES elections- [ ] Zero-knowledge proofs valid

   user_id UUID REFERENCES users- [ ] Hash chain integrity maintained

   token_hash VARCHAR UNIQUE  -- SHA-256(unblinded_token)- [ ] Database encrypted at rest

   is_used BOOLEAN DEFAULT false- [ ] SQL injection prevented

   used_at TIMESTAMP- [ ] XSS protection enabled

   issued_at TIMESTAMP- [ ] CSRF tokens implemented

   ```- [ ] Rate limiting functional (application level)



7. **election_results** - Tally results### Functional Testing

   ```sql- [ ] User registration works

   result_id UUID PRIMARY KEY- [ ] KYC approval flow works

   election_id UUID REFERENCES elections- [ ] Login with biometric works

   candidate_id UUID REFERENCES candidates- [ ] Election creation works

   vote_count INT- [ ] Trustee key generation works

   tallied_at TIMESTAMP- [ ] Vote casting works

   verified BOOLEAN- [ ] Vote verification works

   ```- [ ] Results tallying works

- [ ] Audit trail accessible

8. **voting_codes** - Voter verification codes

   ```sql---

   code_id UUID PRIMARY KEY

   user_id UUID REFERENCES users## Security Measures Summary

   election_id UUID REFERENCES elections

   main_voting_code VARCHAR  -- Main code for authentication### 1. **Defense in Depth**

   candidate_codes JSONB  -- {candidate_id: code}Multiple security layers at every level:

   code_sheet_generated BOOLEAN- Network (TLS)

   main_code_used BOOLEAN- Application (validation, auth)

   created_at TIMESTAMP- Data (encryption)

   ```- Infrastructure (containers, firewalls)



9. **bulletin_board** - Public audit log### 2. **Principle of Least Privilege**

   ```sql- Service-specific database users

   entry_id UUID PRIMARY KEY- Role-based access control

   election_id UUID REFERENCES elections- Minimal container permissions

   entry_type VARCHAR CHECK IN ('ELECTION_CREATED', 'KEY_GENERATED', 

                                 'BALLOT_CAST', 'ELECTION_CLOSED', ### 3. **Zero Trust Architecture**

                                 'TRUSTEE_SHARE', 'RESULT_PUBLISHED')- Verify every request

   entry_hash VARCHAR  -- SHA-256(entry_data + previous_hash)- No implicit trust between services

   previous_hash VARCHAR  -- Links to previous entry- Continuous authentication

   entry_data JSONB

   signature BYTEA### 4. **Cryptographic Excellence**

   sequence_number BIGSERIAL UNIQUE- Modern algorithms (Curve25519, Ed25519)

   created_at TIMESTAMP- Proper key management

   ```- Secure random number generation

- Constant-time implementations

10. **sessions** - JWT session management

    ```sql### 5. **Transparency & Auditability**

    session_id UUID PRIMARY KEY- Public bulletin board

    user_id UUID REFERENCES users- Comprehensive audit logs

    access_token TEXT- Open-source verification tools

    refresh_token TEXT- Mathematical proofs of correctness

    device_info JSONB

    ip_address INET### 6. **Privacy by Design**

    expires_at TIMESTAMP- Ballot secrecy guaranteed cryptographically

    created_at TIMESTAMP- Anonymous credentials

    ```- Mix-net for unlinkability

- No linkage between voter and vote

11. **audit_logs** - System audit trail

    ```sql---

    log_id UUID PRIMARY KEY

    event_type VARCHAR  -- e.g., 'ELECTION_CREATED', 'VOTE_CAST'## Next Steps

    event_description TEXT

    user_id UUID REFERENCES users1. **Review this document completely**

    resource_type VARCHAR  -- e.g., 'ELECTION', 'BALLOT'2. **Set up development environment**

    resource_id UUID3. **Follow implementation phases sequentially**

    ip_address INET4. **Test each component thoroughly**

    user_agent TEXT5. **Document security decisions**

    request_method VARCHAR6. **Prepare for evaluation presentation**

    request_path TEXT

    metadata JSONB---

    severity VARCHAR CHECK IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')

    created_at TIMESTAMP## Support & Documentation

    ```

- **Technical Documentation:** See `docs/` folder

### Indexes (Performance Optimization)- **API Reference:** Available at `/api/docs` when services running

- `idx_bulletin_election` ON bulletin_board(election_id)- **Security Analysis:** See `docs/SECURITY_ANALYSIS.md`

- `idx_bulletin_type` ON bulletin_board(entry_type)- **Architecture Diagrams:** See wireframes below

- `idx_bulletin_sequence` ON bulletin_board(sequence_number)

- `idx_ballot_election` ON ballots(election_id)---

- `idx_ballot_token` ON ballots(token_hash)

- `idx_audit_user` ON audit_logs(user_id)## Evaluation Presentation Preparation

- `idx_audit_event_type` ON audit_logs(event_type)

- `idx_audit_created_at` ON audit_logs(created_at)### Key Points to Emphasize:

1. **Cryptographic rigor:** Modern, standardized algorithms

---2. **Security-first design:** Every decision justified by security requirements

3. **End-to-end verifiability:** Individual + Universal

## 🧪 Testing Guide4. **Privacy guarantees:** Mathematical proofs of anonymity

5. **Practical usability:** Biometric auth, mobile-first design

### 1. Backend Testing6. **Compliance:** Follows Swiss e-voting best practices



**Start All Services**:### Demo Flow:

```powershell1. Admin creates election

# Use 6 separate PowerShell terminals, one for each service2. Trustees generate keys

# See "Getting Started" section for commands3. Voter registers and gets KYC approved

```4. Voter casts vote with biometric auth

5. Vote appears on bulletin board (encrypted)

**Test Health Endpoints**:6. Trustees decrypt results

```powershell7. Voter verifies their vote was counted

curl http://localhost:8001/health  # Auth8. Show audit trail

curl http://localhost:8002/health  # Token

curl http://localhost:8003/health  # Vote---

curl http://localhost:8004/health  # Bulletin

curl http://localhost:8005/health  # Election## License

curl http://localhost:8006/health  # Code SheetThis is an academic project for IS & Cryptography course evaluation.



# All should return: {"status": "healthy"}---

```

**Created by Group F - October 2025**

**Access API Documentation**:

- Auth: http://localhost:8001/api/docs## Wireframes

- Token: http://localhost:8002/api/docs

- Vote: http://localhost:8003/api/docs### Admin Web App

- Bulletin: http://localhost:8004/api/docs

- Election: http://localhost:8005/api/docs```

- Code Sheet: http://localhost:8006/api/docs+---------------------------------------------------------------+

| Sidebar         | Election List                               |

---|-----------------|---------------------------------------------|

| Dashboard       | [Create Election]                           |

### 2. Admin Web Testing| Elections  (*)  | ------------------------------------------- |

| Trustees        | | 2025 University Council Election       | |

**Login**:| Voters          | | Status: ACTIVE | Votes: 124            | |

1. Navigate to http://localhost:5173| Results         | | [Details] [Close]                       | |

2. Email: admin@securevote.com| Audit Log       | ------------------------------------------- |

3. Password: Admin@123| Settings        | | 2025 Student Union Presidential        | |

4. Click "Login"|                 | | Status: DRAFT  | Votes: 0              | |

|                 | | [Edit] [Delete]                         | |

**Create Election**:+-----------------+---------------------------------------------+

1. Dashboard → Elections → Create Election```

2. Fill form:

   - Title: "Test Election 2025"Election Details

   - Start Time: Future date

   - End Time: After start time```

   - Threshold: 5+-----------------------------------------------+

   - Total Trustees: 9| Election: 2025 University Council             |

3. Click "Create"| Status: ACTIVE  | Start: 2025-11-01 09:00     |

4. Election appears in list| End: 2025-11-01 17:00                         |

| Threshold: 5 of 9                             |

**Add Candidates**:|-----------------------------------------------|

1. Click election → Election Details| Candidates                                     |

2. Click "Add Candidate"| 1) Alice Perera    [Edit] [Remove]            |

3. Name: "Alice Perera", Party: "Independent"| 2) Nimal Silva     [Edit] [Remove]            |

4. Repeat for more candidates| 3) Chen Li         [Edit] [Remove]            |

5. Display order auto-increments|-----------------------------------------------|

| Trustees                                        |

**Approve KYC**:| [Invite Trustee]                               |

1. Dashboard → Voters| - Dr. Kapila (KEY_GENERATED)                   |

2. Find voter with "PENDING" KYC| - Ms. Fernando (INVITED)                       |

3. Click "Approve" or "Reject"|-----------------------------------------------|

4. Status updates immediately| Actions                                         |

| [Generate Public Key] [Open Voting]            |

**Generate Voting Codes**:+-----------------------------------------------+

1. Election Details → "Manage Voting Codes"```

2. Click "Generate Codes" (generates for all KYC-approved voters)

3. View codes in table### Mobile App (Flutter)

4. Click "Download All" for CSV export

Login and KYC

**Key Ceremony**:

1. Election Details → "Key Ceremony"```

2. System generates election public key+----------------------------+

3. Distributes shares to 9 trustees| SecureVote                 |

4. Public key stored in election|----------------------------|

| [ Biometric Login ]        |

**Activate Election**:| or                         |

1. Election Details → "Activate"| Email                      |

2. Status changes to ACTIVE| [______________]           |

3. Voters can now vote| Password                   |

| [______________]           |

**Tally Results**:| [ Login ]  [ Register ]    |

1. Close election (status → CLOSED)|                            |

2. Collect trustee decryption shares (min 5/9)| KYC Status: PENDING        |

3. Click "Tally Votes"| [ Upload Document ]        |

4. Results displayed with percentages+----------------------------+

```

**View Bulletin Board**:

1. Election Details → "View Bulletin Board"Election List and Vote

2. See all events in hash chain

3. Click "Verify Chain" → Should show "Chain Valid"```

+----------------------------+

---| Elections                  |

|----------------------------|

### 3. Mobile App Testing| 2025 UC Election  [Open]   |

| 2025 SU President  (Draft) |

**Registration**:|----------------------------|

1. Open app → Register| Enter Main Code            |

2. Fill form with NIC, email, name, DOB, password| [ a1b2-c3d4-e5f6 ]        |

3. Submit| [ Verify ]                 |

4. Cryptographic keys generated automatically|----------------------------|

5. Auto-login after registration| Candidates                 |

| ( ) Alice Perera           |

**Login**:| ( ) Nimal Silva            |

1. Email + password| ( ) Chen Li                |

2. JWT tokens stored securely| [ Encrypt & Submit ]       |

3. Private key retrieved from secure storage+----------------------------+

```

**View Elections**:

1. Home screen shows:Verification Receipt

   - Active elections (can vote)

   - Past elections (already voted)```

2. KYC status displayed+----------------------------+

| Vote Submitted             |

**Cast Vote**:|----------------------------|

1. Tap election card| Your ballot hash:          |

2. View candidates with display order| 9f3a1c...07e2              |

3. Select candidate (radio button)| Verification code:         |

4. Click "Encrypt & Submit"| 419b3fd7                   |

5. Confirmation dialog|                            |

6. Vote encrypted with ECIES locally| Compare with your code     |

7. ZKP generated| sheet for your candidate.  |

8. Submitted with anonymous token| [ Done ]                   |

9. Receipt screen shows:+----------------------------+

   - Receipt ID```

   - Ballot hash (SHA-256)
   - Vote hash
   - QR code
   - Timestamp

**Verify Vote**:
1. From receipt, copy ballot hash
2. Check bulletin board (admin web)
3. Find matching entry (verification in future releases)

---

### 4. End-to-End Workflow Test

**Complete Election Cycle**:

1. **Admin**: Create election
2. **Admin**: Add 3 candidates
3. **Admin**: Invite 9 trustees
4. **Admin**: Run key ceremony (generates election PK, distributes shares)
5. **Admin**: Activate election
6. **Voter 1**: Register via mobile app
7. **Admin**: Approve Voter 1 KYC
8. **Voter 1**: Refresh app, see election
9. **Voter 1**: Request anonymous token (blind signature)
10. **Voter 1**: Unblind token, store securely
11. **Voter 1**: Encrypt vote for Candidate A
12. **Voter 1**: Submit vote with anonymous token
13. **Voter 1**: Receive receipt
14. **Bulletin Board**: Vote entry added to hash chain
15. **Voter 2**: Repeat steps 6-14 for Candidate B
16. **Voter 3**: Repeat steps 6-14 for Candidate A
17. **Admin**: Close election
18. **Trustee 1-5**: Submit decryption shares
19. **Admin**: Tally results
20. **System**: Combines 5 shares, decrypts all ballots, counts votes
21. **Admin**: View results:
    - Candidate A: 2 votes (66.67%)
    - Candidate B: 1 vote (33.33%)
22. **Anyone**: Verify bulletin board hash chain
23. **Voter 1**: Verify ballot hash on bulletin board

---

## 📊 Performance Metrics

### Expected Performance (Single Server)

| Operation | Expected Time | Limit |
|-----------|---------------|-------|
| User Login | < 200ms | 50 req/sec |
| Election Creation | < 100ms | 10 req/sec |
| Vote Submission | < 500ms | 20 votes/sec |
| Bulletin Board Query | < 100ms | 100 req/sec |
| Key Ceremony (9 trustees) | < 5 seconds | 1 req/min |
| Tally (1000 votes) | < 30 seconds | 1 req/election |

### Scalability Considerations
- **Horizontal Scaling**: Each microservice can scale independently
- **Database**: PostgreSQL supports read replicas for high read load
- **Caching**: Redis can be added for session management
- **Load Balancing**: Nginx can distribute requests across service instances

---

## 🔒 Security Audit Checklist

### Pre-Production Security Review

- [ ] All environment variables stored securely (not in code)
- [ ] Database passwords rotated and strong (20+ characters)
- [ ] JWT secret keys rotated and random (32+ bytes)
- [ ] TLS 1.3 configured with valid certificates
- [ ] CORS restricted to production domains only
- [ ] Rate limiting enabled on all public endpoints
- [ ] SQL injection tests passed (all queries parameterized)
- [ ] XSS tests passed (React auto-escaping, CSP headers)
- [ ] CSRF protection enabled (SameSite cookies)
- [ ] Input validation comprehensive (Pydantic models)
- [ ] Error messages don't leak sensitive information
- [ ] Audit logs enabled and monitored
- [ ] Bulletin board hash chain verified daily
- [ ] Trustee key ceremony performed offline
- [ ] Trustee private key shares stored in HSMs
- [ ] Database backups encrypted and tested
- [ ] Disaster recovery plan documented
- [ ] Penetration testing completed
- [ ] Code review by security expert
- [ ] Dependencies scanned for vulnerabilities (npm audit, pip-audit)

---

## 📖 References & Standards

### Cryptographic Standards
1. **NIST FIPS 186-5**: Digital Signature Standard (DSS)
2. **NIST SP 800-56A Rev. 3**: Elliptic Curve Cryptography (ECC)
3. **RFC 8032**: Edwards-Curve Digital Signature Algorithm (EdDSA)
4. **RFC 7748**: Elliptic Curves for Security (Curve25519, X25519)
5. **RFC 5869**: HMAC-based Extract-and-Expand Key Derivation Function (HKDF)

### E-Voting Research
1. **Helios Voting System** - https://heliosvoting.org
2. **Swiss E-Voting Framework** - Federal Chancellery
3. **Scytl Secure Electronic Voting** - Commercial implementation
4. **EstoniaEV** - National e-voting system

### Academic Papers
1. Chaum, D. (1983). "Blind Signatures for Untraceable Payments"
2. Adida, B. (2008). "Helios: Web-based Open-Audit Voting"
3. Benaloh, J. (2006). "Simple Verifiable Elections"
4. Cramer, R., Gennaro, R., Schoenmakers, B. (1997). "A Secure and Optimally Efficient Multi-Authority Election Scheme"

### Web Standards
1. **W3C WebAuthn**: https://www.w3.org/TR/webauthn/
2. **OWASP Top 10**: https://owasp.org/www-project-top-ten/
3. **JWT Best Practices**: RFC 8725

---

## 👥 Team

**Group F**
- MUNASINGHE S.K. - 210396E
- JAYASOORIYA D.D.M. - 210250D

**Course**: Information Security & Cryptography  
**Institution**: University of Moratuwa  
**Supervisor**: [Supervisor Name]  
**Semester**: 7 (2024/2025)

---

## 📄 License

This project is an academic assignment for course evaluation purposes. All rights reserved.

---

## 🙏 Acknowledgments

- PyCA Cryptography Library maintainers
- libsodium developers
- FastAPI and React communities
- PostgreSQL development team
- Flutter and Dart teams
- Material-UI contributors

---

**Last Updated**: October 28, 2025

---

## 📞 Support

For technical questions or issues:
1. Check API documentation at `http://localhost:PORT/api/docs`
2. Review database logs: `psql -U postgres -d evoting_db -c "SELECT * FROM audit_logs ORDER BY created_at DESC LIMIT 10;"`
3. Check service logs in terminal outputs
4. Verify all services are running: `netstat -ano | findstr "800[1-6]"`

---

**End of Documentation**
