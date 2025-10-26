# SecureVote E-Voting System

**Group F - IS & Cryptography Project**  
MUNASINGHE S.K. (210396E) | JAYASOORIYA D.D.M. (210250D)

## 🎯 Project Overview

A secure, end-to-end verifiable e-voting system implementing modern cryptographic protocols including:
- **WebAuthn/FIDO2** biometric authentication
- **RSA Blind Signatures** for anonymous voting credentials
- **Threshold ElGamal** homomorphic encryption
- **Zero-Knowledge Proofs** for ballot validity
- **Public Bulletin Board** for universal verifiability

---

## 🏗️ Architecture

### Microservices Backend (Python FastAPI)
```
┌─────────────────┬─────────────────┬─────────────────┬─────────────────┐
│  Auth Service   │  Token Service  │  Vote Service   │ Bulletin Board  │
│   (Port 8001)   │   (Port 8002)   │   (Port 8003)   │   (Port 8004)   │
├─────────────────┼─────────────────┼─────────────────┼─────────────────┤
│ • User Auth     │ • Blind RSA-2048│ • Vote Storage  │ • Hash Chain    │
│ • JWT Tokens    │   Signatures    │ • Ballot Verify │ • Public Audit  │
│ • KYC Management│ • Anonymous     │ • ZK Proofs     │ • Vote Receipts │
│ • WebAuthn      │   Credentials   │ • Encryption    │                 │
└─────────────────┴─────────────────┴─────────────────┴─────────────────┘
┌─────────────────┬─────────────────────────────────────────────────────┐
│ Election Service│              Code Sheet Service                     │
│   (Port 8005)   │                (Port 8006)                          │
├─────────────────┼─────────────────────────────────────────────────────┤
│ • Election CRUD │ • PDF Generation                                    │
│ • Candidate Mgmt│ • Voter Code Sheets (verification codes)            │
│ • Threshold t/n │ • Secure Distribution                               │
│ • Results Tally │                                                     │
└─────────────────┴─────────────────────────────────────────────────────┘
```

### Frontend Applications
- **Admin Web** (React + TypeScript + Material-UI) - Port 5173
- **Mobile App** (Flutter) - *Coming Soon*

### Database
- **PostgreSQL 18** with 11 tables for complete election lifecycle

---

## 🔐 Cryptographic Concepts Explained

### 1. Threshold Encryption (t-of-n)
**What it means:**
- **n = Total Trustees** (e.g., 9 election officials)
- **t = Threshold** (e.g., 5 minimum required)
- Election results are encrypted so that **at least `t` out of `n` trustees** must collaborate to decrypt
- Prevents any single authority from tampering with results
- Even if `t-1` trustees collude, they cannot decrypt votes

**Example:** With t=5, n=9:
- Private key is split into 9 shares
- Any 5 trustees can combine their shares to decrypt results
- 4 trustees alone cannot decrypt anything
- This is **Threshold ElGamal** on Curve25519

### 2. Blind Signatures (Anonymous Voting)
**RSA-2048 Blind Signatures:**
1. Voter blinds their identity using random factor
2. Token service signs the blinded value (without seeing identity)
3. Voter unblinds the signature
4. Result: Valid signature on voter's credential, but server never saw the actual credential
5. Voter uses this anonymous credential to vote
6. **Breaks the link between voter identity and ballot**

### 3. Display Order
**What it means:**
- The order in which candidates appear on the ballot (1, 2, 3, ...)
- Auto-increments when adding candidates
- Used for ballot layout in mobile app and code sheets
- Important for consistent user experience

---

## 📁 Project Structure

```
e-voting-system/
├── backend/
│   ├── auth-service/          # User authentication, KYC, JWT tokens
│   ├── token-service/         # Blind signatures for anonymous credentials
│   ├── vote-service/          # Vote submission and storage
│   ├── bulletin-board-service/# Public bulletin with hash chain
│   ├── election-service/      # Election management, candidates, trustees
│   ├── code-sheet-service/    # Generate PDF verification code sheets
│   └── shared/                # Common utilities (database, security, crypto)
│
├── admin-web/                 # React admin dashboard
│   ├── src/
│   │   ├── pages/            # Dashboard, Elections, Voters, Results
│   │   ├── services/         # API clients for each backend service
│   │   └── store/            # Redux state management
│   └── package.json
│
├── mobile-app/                # Flutter voter app (coming soon)
├── infrastructure/            # Nginx, SSL configs
├── scripts/
│   └── db-init.sql           # Complete PostgreSQL schema
├── docs/                     # Project documentation
├── .gitignore
├── README.md                 # This file
└── START_SERVICES.md         # How to run the system
```

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.13+** (with pip, venv)
- **Node.js 20+** (with npm)
- **PostgreSQL 18** (local installation)
- **Git**

### 1. Clone Repository
```bash
git clone <repository-url>
cd e-voting-system
```

### 2. Database Setup
```bash
# Create database
psql -U postgres -c "CREATE DATABASE evoting_db;"

# Initialize schema
psql -U postgres -d evoting_db -f scripts/db-init.sql

# Create admin user
psql -U postgres -d evoting_db -c "
INSERT INTO users (nic, email, full_name, date_of_birth, is_admin, kyc_status, password_hash)
VALUES ('ADMIN001', 'admin@securevote.com', 'System Admin', '1990-01-01', true, 'APPROVED', '\$2b\$12\$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzNx7Z7rMu');
"
# Password: Admin@123
```

### 3. Start Backend Services
See **[START_SERVICES.md](./START_SERVICES.md)** for detailed instructions.

**Quick version:**
```bash
# Terminal 1 - Auth Service
cd backend/auth-service
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # Linux/Mac
pip install -r requirements.txt
$env:DATABASE_URL="postgresql://postgres:YourPassword@localhost:5432/evoting_db"
uvicorn app.main:app --port 8001 --reload

# Terminal 2 - Election Service
cd backend/election-service
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:DATABASE_URL="postgresql://postgres:YourPassword@localhost:5432/evoting_db"
uvicorn app.main:app --port 8005 --reload

# Repeat for other services (ports 8002-8004, 8006)
```

### 4. Start Admin Web
```bash
cd admin-web
npm install
npm run dev
# Opens on http://localhost:5173
```

### 5. Login
- **URL:** http://localhost:5173
- **Email:** admin@securevote.com
- **Password:** Admin@123

---

## 📚 API Documentation

### Auth Service (Port 8001)
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login with email/password
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/users/list` - List all voters (admin only)
- `POST /api/users/kyc/approve/{user_id}` - Approve KYC (admin only)
- `POST /api/users/kyc/reject/{user_id}` - Reject KYC (admin only)

### Election Service (Port 8005)
- `GET /api/election/list` - List all elections
- `GET /api/election/{id}` - Get election details with candidates
- `POST /api/election/create` - Create new election
- `POST /api/election/candidate/add` - Add candidate to election
- `GET /api/election/stats/dashboard` - Get dashboard statistics

### Token Service (Port 8002)
- `POST /api/token/request` - Request blind token
- `POST /api/token/verify` - Verify anonymous credential

### Vote Service (Port 8003)
- `POST /api/vote/submit` - Submit encrypted ballot
- `POST /api/vote/verify` - Verify ZK proof

### Bulletin Board (Port 8004)
- `GET /api/bulletin/list` - View public bulletin board
- `POST /api/bulletin/post` - Post ballot to bulletin (internal)

### Code Sheet Service (Port 8006)
- `POST /api/codesheet/generate` - Generate PDF code sheets

---

## 🗄️ Database Schema

**11 Core Tables:**
1. **users** - Voter/admin accounts with WebAuthn credentials
2. **sessions** - JWT session management
3. **elections** - Election metadata (title, dates, threshold_t, total_trustees_n)
4. **candidates** - Election candidates with m_value for encryption
5. **trustees** - Trustee key shares for threshold decryption
6. **votes** - Encrypted ballots
7. **ballots** - Vote commitments
8. **bulletin_board_entries** - Public audit trail
9. **mix_servers** - Mix-net for anonymity
10. **verification_codes** - Code sheets for voter verification
11. **audit_logs** - System audit trail

---

## 🛡️ Security Features

### ✅ Implemented
- **JWT Authentication** with 15-minute access tokens
- **PostgreSQL** with parameterized queries (SQL injection prevention)
- **CORS** configured for localhost:5173
- **Password Hashing** with bcrypt (12 rounds)
- **Admin Authorization** middleware
- **Timezone-aware** token expiry (UTC)
- **Error Handling** with proper HTTP status codes

### 🔜 Coming Soon
- WebAuthn biometric authentication
- RSA-2048 blind signature implementation
- Threshold ElGamal encryption
- Zero-knowledge proofs (Schnorr, Chaum-Pedersen)
- Mix-net with 7+ servers
- TLS 1.3 with certificate pinning

---

## 🧪 Testing

### Current Status
- ✅ Auth service endpoints tested
- ✅ Election CRUD operations working
- ✅ Dashboard real-time stats working
- ✅ KYC approval/rejection working
- ✅ Candidate management working

### Test User
```
Email: admin@securevote.com
Password: Admin@123
```

---

## 📝 Development Status

### ✅ Completed (MVP Phase 1)
- [x] Backend microservices architecture
- [x] PostgreSQL database schema
- [x] User authentication (password-based)
- [x] Admin web dashboard
- [x] Election management (CRUD)
- [x] Candidate management
- [x] Voter management with KYC
- [x] Dashboard statistics
- [x] Real-time data from database

### 🚧 In Progress (Phase 2)
- [ ] WebAuthn/FIDO2 implementation
- [ ] RSA blind signatures
- [ ] Threshold ElGamal key generation
- [ ] Vote encryption/decryption
- [ ] Zero-knowledge proofs
- [ ] Mobile app (Flutter)

### 📅 Planned (Phase 3)
- [ ] Mix-net implementation
- [ ] Public bulletin board
- [ ] Code sheet PDF generation
- [ ] Results tallying with threshold decryption
- [ ] End-to-end verification
- [ ] Audit log visualization

---

## 👥 Team Collaboration Guide

### Git Workflow
```bash
# Always pull latest before working
git pull origin main

# Create feature branch
git checkout -b feature/your-feature-name

# Make changes, commit frequently
git add .
git commit -m "feat: descriptive message"

# Push to remote
git push origin feature/your-feature-name

# Create Pull Request on GitHub
```

### Branch Naming Convention
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring

### Commit Message Format
```
feat: Add blind signature endpoint
fix: Resolve timezone issue in token expiry
docs: Update API documentation
refactor: Simplify database connection logic
```

---

## 📞 Support & Contact

**Group F:**
- MUNASINGHE S.K. - 210396E
- JAYASOORIYA D.D.M. - 210250D

**Course:** Information Security & Cryptography  
**Institution:** University of Moratuwa  
**Date:** October 2025

---

## 📄 License

This is an academic project for course evaluation purposes.

---

## 🎓 References

1. Helios Voting System - https://heliosvoting.org
2. Swiss E-Voting Standards - https://www.post.ch/evoting
3. WebAuthn Specification - https://www.w3.org/TR/webauthn/
4. Threshold Cryptography - Shamir Secret Sharing
5. Blind Signatures - Chaum 1983

---

**Last Updated:** October 26, 2025

### Project Overview
This is a secure, end-to-end verifiable e-voting system implementing modern cryptographic protocols including WebAuthn/FIDO2 authentication, ECIES ballot encryption, threshold ElGamal homomorphic encryption, and mix-net privacy protection.

**Group Members:**
- MUNASINGHE S.K. - 210396E
- JAYASOORIYA D.D.M. - 210250D

---

## Table of Contents
1. [Tech Stack & Justification](#tech-stack--justification)
2. [Security Architecture](#security-architecture)
3. [System Architecture](#system-architecture)
4. [Project Structure](#project-structure)
5. [Prerequisites](#prerequisites)
6. [Step-by-Step Implementation](#step-by-step-implementation)
7. [Deployment Guide](#deployment-guide)
8. [Testing & Verification](#testing--verification)
9. [Security Measures](#security-measures)

---

## Tech Stack & Justification

### Backend Services (Microservices Architecture)
**Technology:** Python FastAPI + PostgreSQL

**Why FastAPI?**
- **Performance:** ASGI-based, async/await support for high concurrency
- **Security:** Built-in OAuth2, JWT, and input validation
- **Documentation:** Auto-generated OpenAPI documentation
- **Type Safety:** Pydantic models prevent injection attacks
- **Microservices Ready:** Easy service isolation for security boundaries

**Why PostgreSQL?**
- **ACID Compliance:** Critical for election data integrity
- **Strong Security:** Row-level security, SSL connections, audit logging
- **Cryptographic Extensions:** pgcrypto for additional security layers
- **Reliability:** Battle-tested for critical applications

### Mobile Application
**Technology:** Flutter (Dart)

**Why Flutter?**
- **Cross-Platform:** Single codebase for iOS & Android (cost-effective for MVP)
- **Security:** Secure storage plugins, biometric authentication support
- **Cryptography:** pointycastle library for client-side encryption
- **Performance:** Compiled to native code
- **UI/UX:** Material Design and Cupertino widgets for native feel

### Admin Web Platform
**Technology:** React.js + TypeScript + Material-UI

**Why React?**
- **Component Reusability:** Faster development of admin features
- **TypeScript:** Type safety prevents common vulnerabilities
- **Ecosystem:** Rich cryptography libraries (Web Crypto API, elliptic.js)
- **Security:** Virtual DOM prevents XSS attacks
- **State Management:** Redux for complex election management workflows

### Cryptography Libraries

**Backend (Python):**
- **cryptography:** Industry-standard, maintained by PyCA
- **pynacl:** libsodium bindings for modern cryptography
- **ecdsa:** Elliptic curve signatures (Ed25519)
- **Justification:** FIPS 140-2 validated, constant-time implementations

**Frontend (Flutter):**
- **pointycastle:** Pure Dart crypto library
- **crypto:** Dart's official crypto package
- **Justification:** No native dependencies, cross-platform compatibility

**Web Admin (React):**
- **Web Crypto API:** Browser-native, hardware-accelerated
- **elliptic:** Pure JavaScript ECC implementation
- **Justification:** Secure, audited, widely used

### Infrastructure & DevOps
- **Docker + Docker Compose:** Service isolation and reproducible deployments
- **Nginx:** Reverse proxy with TLS 1.3 termination
- **GitHub Actions:** CI/CD with automated security scanning

---

## Security Architecture

### 1. Transport Security
- **TLS 1.3** with forward secrecy
- **Certificate Pinning** in mobile app
- **HSTS** headers on all web endpoints

### 2. Authentication & Authorization
- **WebAuthn/FIDO2** for passwordless authentication
- **Biometric Verification** (TouchID, FaceID, fingerprint)
- **JWT Tokens** with short expiry (15 minutes)
- **Refresh Tokens** in httpOnly cookies
- **Why:** Phishing-resistant, no password database to breach

### 3. Ballot Encryption (Privacy)
- **ECIES (Elliptic Curve Integrated Encryption Scheme)**
  - Key Agreement: X25519
  - Symmetric: AES-256-GCM
  - KDF: HKDF-SHA256
- **Why:** Ensures ballot secrecy, prevents server from reading votes

### 4. Homomorphic Tallying
- **Threshold ElGamal on Curve25519**
- **Threshold:** t=5 of n=9 trustees
- **Why:** No single entity can decrypt votes, enables encrypted tallying

### 5. Anonymity Protection
- **Blind Signatures** for anonymous credentials
- **Mix-Net** with 7+ servers for vote shuffling
- **Zero-Knowledge Proofs** for ballot validity
- **Why:** Breaks link between voter identity and ballot

### 6. Verifiability
- **Individual Verifiability:** Ed25519 signatures on vote receipts
- **Universal Verifiability:** Public bulletin board with hash chain
- **Why:** Voters can verify their vote was counted, anyone can audit results

### 7. Database Security
- **Encryption at Rest:** AES-256 for sensitive fields
- **Prepared Statements:** Prevents SQL injection
- **Row-Level Security:** Postgres RLS policies
- **Audit Logging:** All access logged with timestamps

### 8. Application Security
- **Input Validation:** Pydantic models, schema validation
- **Rate Limiting:** Redis-based, prevents DoS
- **CORS:** Strict origin policies
- **CSP Headers:** Prevents XSS attacks
- **Dependency Scanning:** Automated vulnerability checks

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Layer                              │
├─────────────────────────────┬───────────────────────────────────┤
│   Flutter Mobile App        │   React Admin Web App             │
│   (Voter Interface)         │   (Admin Dashboard)               │
│   - Biometric Auth          │   - Election Management           │
│   - Ballot Encryption       │   - Trustee Coordination          │
│   - Vote Verification       │   - Results Visualization         │
└──────────────┬──────────────┴────────────────┬──────────────────┘
               │                                │
               │        TLS 1.3 + Cert Pinning │
               │                                │
┌──────────────┴────────────────────────────────┴──────────────────┐
│                     API Gateway (Nginx)                           │
│              - TLS Termination                                    │
│              - Rate Limiting                                      │
│              - Load Balancing                                     │
└──────────────┬────────────────────────────────────────────────────┘
               │
    ┌──────────┴──────────┐
    │   FastAPI Services  │
    │   (Microservices)   │
    └──────────┬──────────┘
               │
┌──────────────┴────────────────────────────────────────────────┐
│                   Service Layer                                │
├───────────────┬──────────────┬──────────────┬─────────────────┤
│  Auth Service │ Token Service│ Vote Service │ Bulletin Board  │
│               │              │              │   Service       │
│  - WebAuthn   │ - Blind Sig  │ - ZK Verify  │ - Hash Chain   │
│  - KYC        │ - Anonymous  │ - Encrypted  │ - Public Audit │
│  - JWT        │   Credential │   Storage    │                │
└───────┬───────┴──────┬───────┴──────┬───────┴────────┬────────┘
        │              │              │                │
┌──────────────┴────────────────────────────────────────────────┐
│                    Data Layer                                  │
├────────────────────┬───────────────────────────────────────────┤
│   PostgreSQL       │              File Storage                 │
│   - Users          │           - Code Sheets                   │
│   - Elections      │           - Audit Logs                    │
│   - Ballots        │                                           │
│   - Trustees       │                                           │
│   - Sessions       │                                           │
└────────────────────┴───────────────────────────────────────────┘
```

### Service Isolation
Each microservice runs in a separate container with:
- Dedicated database schema
- Service-specific API keys
- Network isolation (internal Docker network)
- Resource limits (CPU, memory)

---

## Project Structure

```
e-voting-system/
├── backend/
│   ├── auth-service/
│   │   ├── app/
│   │   │   ├── api/
│   │   │   │   ├── routes/
│   │   │   │   │   ├── auth.py
│   │   │   │   │   ├── kyc.py
│   │   │   │   │   └── webauthn.py
│   │   │   │   └── dependencies.py
│   │   │   ├── models/
│   │   │   │   ├── user.py
│   │   │   │   └── session.py
│   │   │   ├── schemas/
│   │   │   │   └── auth_schemas.py
│   │   │   ├── services/
│   │   │   │   ├── auth_service.py
│   │   │   │   └── webauthn_service.py
│   │   │   ├── utils/
│   │   │   │   ├── crypto.py
│   │   │   │   └── jwt_handler.py
│   │   │   ├── config.py
│   │   │   └── main.py
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── token-service/
│   │   ├── app/
│   │   │   ├── api/
│   │   │   │   └── routes/
│   │   │   │       └── blind_signing.py
│   │   │   ├── models/
│   │   │   │   └── token.py
│   │   │   ├── services/
│   │   │   │   └── blind_signature_service.py
│   │   │   ├── utils/
│   │   │   │   └── blind_crypto.py
│   │   │   └── main.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── vote-service/
│   │   ├── app/
│   │   │   ├── api/
│   │   │   │   └── routes/
│   │   │   │       └── vote_submission.py
│   │   │   ├── models/
│   │   │   │   └── ballot.py
│   │   │   ├── services/
│   │   │   │   ├── vote_service.py
│   │   │   │   └── zkp_service.py
│   │   │   ├── utils/
│   │   │   │   ├── elgamal.py
│   │   │   │   └── zkp.py
│   │   │   └── main.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── bulletin-board-service/
│   │   ├── app/
│   │   │   ├── api/
│   │   │   │   └── routes/
│   │   │   │       └── bulletin.py
│   │   │   ├── models/
│   │   │   │   └── bulletin_entry.py
│   │   │   ├── services/
│   │   │   │   └── hash_chain_service.py
│   │   │   └── main.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── election-service/
│   │   ├── app/
│   │   │   ├── api/
│   │   │   │   └── routes/
│   │   │   │       ├── election.py
│   │   │   │       └── trustee.py
│   │   │   ├── models/
│   │   │   │   ├── election.py
│   │   │   │   └── trustee.py
│   │   │   ├── services/
│   │   │   │   ├── election_service.py
│   │   │   │   └── threshold_crypto_service.py
│   │   │   └── main.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── code-sheet-service/
│   │   ├── app/
│   │   │   ├── api/
│   │   │   │   └── routes/
│   │   │   │       └── code_sheet.py
│   │   │   ├── services/
│   │   │   │   └── pdf_generator.py
│   │   │   └── main.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── shared/
│   │   ├── database.py
│   │   ├── security.py
│   │   └── constants.py
│   │
│   └── docker-compose.yml
│
├── mobile-app/
│   ├── android/
│   ├── ios/
│   ├── lib/
│   │   ├── main.dart
│   │   ├── core/
│   │   │   ├── config/
│   │   │   │   └── app_config.dart
│   │   │   ├── network/
│   │   │   │   └── api_client.dart
│   │   │   └── utils/
│   │   │       ├── crypto_utils.dart
│   │   │       └── secure_storage.dart
│   │   ├── features/
│   │   │   ├── auth/
│   │   │   │   ├── data/
│   │   │   │   ├── domain/
│   │   │   │   └── presentation/
│   │   │   │       ├── pages/
│   │   │   │       │   ├── login_page.dart
│   │   │   │       │   ├── register_page.dart
│   │   │   │       │   └── kyc_page.dart
│   │   │   │       └── widgets/
│   │   │   ├── voting/
│   │   │   │   ├── data/
│   │   │   │   ├── domain/
│   │   │   │   └── presentation/
│   │   │   │       ├── pages/
│   │   │   │       │   ├── election_list_page.dart
│   │   │   │       │   ├── voting_page.dart
│   │   │   │       │   └── verification_page.dart
│   │   │   │       └── widgets/
│   │   │   └── profile/
│   │   │       └── presentation/
│   │   │           └── pages/
│   │   │               └── profile_page.dart
│   │   └── shared/
│   │       └── widgets/
│   ├── test/
│   ├── pubspec.yaml
│   └── README.md
│
├── admin-web/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── common/
│   │   │   ├── elections/
│   │   │   │   ├── ElectionForm.tsx
│   │   │   │   ├── ElectionList.tsx
│   │   │   │   └── ElectionDetails.tsx
│   │   │   ├── trustees/
│   │   │   │   ├── TrusteeManagement.tsx
│   │   │   │   └── KeyGeneration.tsx
│   │   │   ├── voters/
│   │   │   │   ├── VoterList.tsx
│   │   │   │   └── KYCVerification.tsx
│   │   │   └── results/
│   │   │       ├── ResultsDashboard.tsx
│   │   │       └── AuditLog.tsx
│   │   ├── services/
│   │   │   ├── api.ts
│   │   │   ├── crypto.ts
│   │   │   └── auth.ts
│   │   ├── store/
│   │   │   ├── store.ts
│   │   │   └── slices/
│   │   ├── utils/
│   │   │   └── crypto-helpers.ts
│   │   ├── App.tsx
│   │   └── index.tsx
│   ├── package.json
│   ├── tsconfig.json
│   └── README.md
│
├── infrastructure/
│   ├── nginx/
│   │   ├── nginx.conf
│   │   └── ssl/
│   ├── docker/
│   │   └── docker-compose.prod.yml
│   └── kubernetes/
│       ├── deployments/
│       └── services/
│
├── docs/
│   ├── API_DOCUMENTATION.md
│   ├── SECURITY_ANALYSIS.md
│   ├── DEPLOYMENT_GUIDE.md
│   └── USER_MANUAL.md
│
├── tests/
│   ├── integration/
│   ├── security/
│   └── performance/
│
├── scripts/
│   ├── setup.sh
│   ├── db-init.sql
│   └── generate-keys.py
│
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── security-scan.yml
│
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

---

## Prerequisites

### Development Environment
1. **Operating System:** Windows 10/11, macOS, or Linux
2. **Docker Desktop:** Version 20.10+
3. **Docker Compose:** Version 2.0+
4. **Git:** Latest version

### Backend Development
1. **Python:** 3.11+
2. **pip:** Latest version
3. **Virtual Environment:** venv or conda

### Mobile Development
1. **Flutter SDK:** 3.16+
2. **Android Studio:** Latest (for Android development)
3. **Xcode:** Latest (for iOS development, macOS only)
4. **Android SDK:** API Level 33+
5. **iOS Simulator:** iOS 15+ (macOS only)

### Web Development
1. **Node.js:** 20 LTS+
2. **npm or yarn:** Latest version
3. **Web Browser:** Chrome/Firefox (with dev tools)

### Database
1. **PostgreSQL:** 15+ (via Docker)

### Optional (Recommended)
1. **Postman:** API testing
2. **VS Code:** With Flutter, Python extensions
3. **pgAdmin:** Database management GUI

---

## Step-by-Step Implementation

### Phase 1: Environment Setup (Days 1-2)

#### Step 1.1: Clone and Initialize Project
```bash
# Create project directory
mkdir e-voting-system
cd e-voting-system

# Initialize git
git init
git branch -M main
```

#### Step 1.2: Create .gitignore
Create `.gitignore` in root directory (already included in structure)

#### Step 1.3: Environment Variables
Create `.env.example` with all required variables (see separate file)

#### Step 1.4: Docker Setup
Create `docker-compose.yml` for development environment

---

### Phase 2: Backend Core Services (Days 3-7)

#### Step 2.1: Database Schema Design
Create `scripts/db-init.sql` with complete schema

#### Step 2.2: Shared Utilities
Implement shared cryptographic primitives:
- X25519 key agreement
- Ed25519 signatures
- HKDF key derivation
- AES-256-GCM encryption

#### Step 2.3: Authentication Service
Implement:
1. User registration endpoint
2. WebAuthn registration/authentication
3. KYC submission
4. JWT token generation
5. Session management

#### Step 2.4: Token Service (Blind Signatures)
Implement:
1. Anonymous token request
2. Blind signature generation
3. Token verification

#### Step 2.5: Vote Service
Implement:
1. Encrypted ballot submission
2. Zero-knowledge proof verification
3. Ballot storage

#### Step 2.6: Bulletin Board Service
Implement:
1. Hash chain maintenance
2. Public ballot posting
3. Audit trail generation

#### Step 2.7: Election Service
Implement:
1. Election CRUD operations
2. Trustee management
3. Threshold key generation
4. Results tallying

---

### Phase 3: Mobile Application (Days 8-12)

#### Step 3.1: Project Setup
```bash
cd mobile-app
flutter create .
flutter pub get
```

#### Step 3.2: Dependencies
Add to `pubspec.yaml`:
- http: API calls
- flutter_secure_storage: Secure key storage
- local_auth: Biometric authentication
- pointycastle: Cryptography
- provider: State management

#### Step 3.3: Core Features
1. **Authentication Flow**
   - Login screen with biometric
   - Registration with KYC
   - Session management

2. **Voting Flow**
   - Election list
   - Candidate selection
   - Main code entry
   - Ballot encryption
   - Vote submission
   - Verification

3. **Profile**
   - User information
   - Vote history
   - Verification receipts

---

### Phase 4: Admin Web Application (Days 13-16)

#### Step 4.1: Project Setup
```bash
cd admin-web
npx create-react-app . --template typescript
npm install
```

#### Step 4.2: Dependencies
- @mui/material: UI components
- axios: HTTP client
- redux-toolkit: State management
- elliptic: Cryptography
- recharts: Data visualization

#### Step 4.3: Core Features
1. **Election Management**
   - Create elections
   - Add candidates
   - Configure election parameters

2. **Trustee Coordination**
   - Key generation ceremony
   - Partial decryption collection
   - Result computation

3. **Voter Management**
   - KYC verification
   - Voter list management
   - Code sheet generation

4. **Results & Auditing**
   - Live vote counting
   - Results visualization
   - Audit log viewing

---

### Phase 5: Integration & Testing (Days 17-19)

#### Step 5.1: End-to-End Testing
1. Complete voter journey
2. Admin workflows
3. Trustee operations

#### Step 5.2: Security Testing
1. Penetration testing
2. Cryptographic verification
3. API security testing

#### Step 5.3: Performance Testing
1. Load testing (concurrent voters)
2. Database optimization
3. API response times

---

### Phase 6: Documentation & Deployment (Days 20-21)

#### Step 6.1: Documentation
1. API documentation (OpenAPI/Swagger)
2. User manuals
3. Security analysis report
4. Deployment guide

#### Step 6.2: Production Deployment
1. SSL/TLS certificate setup
2. Production environment configuration
3. Database backups
4. Monitoring setup

---

## Deployment Guide

### Development Deployment
```bash
# Start all services
docker-compose up -d

# Check service health
docker-compose ps

# View logs
docker-compose logs -f [service-name]

# Run mobile app
cd mobile-app
flutter run

# Run admin web
cd admin-web
npm start
```

### Production Deployment
See `docs/DEPLOYMENT_GUIDE.md` for detailed production deployment instructions.

---

## Testing & Verification

### Security Verification Checklist
- [ ] TLS 1.3 configured correctly
- [ ] Certificate pinning working in mobile app
- [ ] WebAuthn properly implemented
- [ ] Ballot encryption verified
- [ ] Blind signatures working
- [ ] Zero-knowledge proofs valid
- [ ] Hash chain integrity maintained
- [ ] Database encrypted at rest
- [ ] SQL injection prevented
- [ ] XSS protection enabled
- [ ] CSRF tokens implemented
- [ ] Rate limiting functional (application level)

### Functional Testing
- [ ] User registration works
- [ ] KYC approval flow works
- [ ] Login with biometric works
- [ ] Election creation works
- [ ] Trustee key generation works
- [ ] Vote casting works
- [ ] Vote verification works
- [ ] Results tallying works
- [ ] Audit trail accessible

---

## Security Measures Summary

### 1. **Defense in Depth**
Multiple security layers at every level:
- Network (TLS)
- Application (validation, auth)
- Data (encryption)
- Infrastructure (containers, firewalls)

### 2. **Principle of Least Privilege**
- Service-specific database users
- Role-based access control
- Minimal container permissions

### 3. **Zero Trust Architecture**
- Verify every request
- No implicit trust between services
- Continuous authentication

### 4. **Cryptographic Excellence**
- Modern algorithms (Curve25519, Ed25519)
- Proper key management
- Secure random number generation
- Constant-time implementations

### 5. **Transparency & Auditability**
- Public bulletin board
- Comprehensive audit logs
- Open-source verification tools
- Mathematical proofs of correctness

### 6. **Privacy by Design**
- Ballot secrecy guaranteed cryptographically
- Anonymous credentials
- Mix-net for unlinkability
- No linkage between voter and vote

---

## Next Steps

1. **Review this document completely**
2. **Set up development environment**
3. **Follow implementation phases sequentially**
4. **Test each component thoroughly**
5. **Document security decisions**
6. **Prepare for evaluation presentation**

---

## Support & Documentation

- **Technical Documentation:** See `docs/` folder
- **API Reference:** Available at `/api/docs` when services running
- **Security Analysis:** See `docs/SECURITY_ANALYSIS.md`
- **Architecture Diagrams:** See wireframes below

---

## Evaluation Presentation Preparation

### Key Points to Emphasize:
1. **Cryptographic rigor:** Modern, standardized algorithms
2. **Security-first design:** Every decision justified by security requirements
3. **End-to-end verifiability:** Individual + Universal
4. **Privacy guarantees:** Mathematical proofs of anonymity
5. **Practical usability:** Biometric auth, mobile-first design
6. **Compliance:** Follows Swiss e-voting best practices

### Demo Flow:
1. Admin creates election
2. Trustees generate keys
3. Voter registers and gets KYC approved
4. Voter casts vote with biometric auth
5. Vote appears on bulletin board (encrypted)
6. Trustees decrypt results
7. Voter verifies their vote was counted
8. Show audit trail

---

## License
This is an academic project for IS & Cryptography course evaluation.

---

**Created by Group F - October 2025**

## Wireframes

### Admin Web App

```
+---------------------------------------------------------------+
| Sidebar         | Election List                               |
|-----------------|---------------------------------------------|
| Dashboard       | [Create Election]                           |
| Elections  (*)  | ------------------------------------------- |
| Trustees        | | 2025 University Council Election       | |
| Voters          | | Status: ACTIVE | Votes: 124            | |
| Results         | | [Details] [Close]                       | |
| Audit Log       | ------------------------------------------- |
| Settings        | | 2025 Student Union Presidential        | |
|                 | | Status: DRAFT  | Votes: 0              | |
|                 | | [Edit] [Delete]                         | |
+-----------------+---------------------------------------------+
```

Election Details

```
+-----------------------------------------------+
| Election: 2025 University Council             |
| Status: ACTIVE  | Start: 2025-11-01 09:00     |
| End: 2025-11-01 17:00                         |
| Threshold: 5 of 9                             |
|-----------------------------------------------|
| Candidates                                     |
| 1) Alice Perera    [Edit] [Remove]            |
| 2) Nimal Silva     [Edit] [Remove]            |
| 3) Chen Li         [Edit] [Remove]            |
|-----------------------------------------------|
| Trustees                                        |
| [Invite Trustee]                               |
| - Dr. Kapila (KEY_GENERATED)                   |
| - Ms. Fernando (INVITED)                       |
|-----------------------------------------------|
| Actions                                         |
| [Generate Public Key] [Open Voting]            |
+-----------------------------------------------+
```

### Mobile App (Flutter)

Login and KYC

```
+----------------------------+
| SecureVote                 |
|----------------------------|
| [ Biometric Login ]        |
| or                         |
| Email                      |
| [______________]           |
| Password                   |
| [______________]           |
| [ Login ]  [ Register ]    |
|                            |
| KYC Status: PENDING        |
| [ Upload Document ]        |
+----------------------------+
```

Election List and Vote

```
+----------------------------+
| Elections                  |
|----------------------------|
| 2025 UC Election  [Open]   |
| 2025 SU President  (Draft) |
|----------------------------|
| Enter Main Code            |
| [ a1b2-c3d4-e5f6 ]        |
| [ Verify ]                 |
|----------------------------|
| Candidates                 |
| ( ) Alice Perera           |
| ( ) Nimal Silva            |
| ( ) Chen Li                |
| [ Encrypt & Submit ]       |
+----------------------------+
```

Verification Receipt

```
+----------------------------+
| Vote Submitted             |
|----------------------------|
| Your ballot hash:          |
| 9f3a1c...07e2              |
| Verification code:         |
| 419b3fd7                   |
|                            |
| Compare with your code     |
| sheet for your candidate.  |
| [ Done ]                   |
+----------------------------+
```
