# Team Collaboration - Project Handoff

## 📋 Current Implementation Status

### ✅ Completed (MVP Phase 1)
- Backend microservices architecture (6 services)
- PostgreSQL database with complete schema (11 tables)
- User authentication with JWT tokens
- Admin web dashboard (React + TypeScript + Material-UI)
- Election management (Create, Read, Update)
- Candidate management with auto-incrementing display_order
- Voter/User management with KYC approval/rejection
- Dashboard with real-time statistics from database
- CORS configuration for local development
- Python 3.13 compatibility resolved

### 🎯 What Works Right Now
1. **Login** - admin@securevote.com / Admin@123
2. **Dashboard** - Shows real stats (elections, voters, KYC pending)
3. **Elections** - Create, list, view details
4. **Candidates** - Add candidates to elections
5. **Voters** - View all registered users, approve/reject KYC

### 🔧 Ready for Development
- All 6 backend services have structure
- Database schema complete
- Shared crypto utilities in place
- Frontend routing and state management setup

---

## 🚀 How to Get Started (New Team Member)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd e-voting-system
```

### 2. Install Prerequisites
- Python 3.13+
- Node.js 20+
- PostgreSQL 18
- Git

### 3. Database Setup
```powershell
# Create database
psql -U postgres -c "CREATE DATABASE evoting_db;"

# Initialize schema
psql -U postgres -d evoting_db -f scripts\db-init.sql
```

### 4. Start Services
**See [START_SERVICES.md](./START_SERVICES.md)** for detailed instructions.

Quick version:
- Open 7 PowerShell terminals
- Start 6 backend services (ports 8001-8006)
- Start admin-web (port 5173)

### 5. Test It Works
- Open http://localhost:5173
- Login with admin@securevote.com / Admin@123
- Create an election, add candidates
- Check voters page

---

## 📚 Understanding the Codebase

### Backend Structure
```
backend/
├── auth-service/          # JWT auth, login, KYC, user management
├── token-service/         # Blind signatures (RSA-2048)
├── vote-service/          # Vote submission, ZK proofs
├── bulletin-board-service/# Public audit trail
├── election-service/      # Elections, candidates, trustees
├── code-sheet-service/    # PDF generation
└── shared/                # Common utilities (DB, crypto, constants)
```

Each service has:
- `app/main.py` - FastAPI app entry point
- `app/api/routes/` - API endpoints
- `requirements.txt` - Python dependencies
- `venv/` - Virtual environment (gitignored)

### Frontend Structure
```
admin-web/src/
├── pages/          # Dashboard, Elections, Voters, Results
├── services/       # API clients (authApi, electionApi, etc.)
└── store/          # Redux state management
```

### Database
11 tables in PostgreSQL:
- `users` - Voter/admin accounts
- `sessions` - JWT sessions
- `elections` - Election metadata
- `candidates` - Election candidates
- `trustees` - Trustee key shares
- `votes` - Encrypted ballots
- (+ 5 more for verification, audit, mix-net)

---

## 🔑 Key Cryptographic Concepts

### Threshold Encryption (t-of-n)
- **n = Total Trustees** (e.g., 9 officials)
- **t = Threshold** (e.g., 5 minimum required)
- Private key split into n shares
- Need t shares to decrypt results
- Prevents single authority tampering
- **Used in:** Election results decryption

### Blind Signatures (Anonymous Voting)
- **RSA-2048** implementation in token-service
- Voter blinds identity, gets signature, unblinds
- Server never sees actual credential
- **Used in:** Breaking link between voter and ballot

### Display Order
- Order candidates appear on ballot (1, 2, 3...)
- Auto-increments when adding candidates
- **Used in:** Ballot UI, code sheets

---

## 🛠️ Development Workflow

### Working on a Feature

1. **Create Feature Branch**
```bash
git checkout -b feature/your-feature-name
```

2. **Make Changes**
- Edit code
- Test locally
- Commit frequently

3. **Commit with Meaningful Messages**
```bash
git add .
git commit -m "feat: Add ballot encryption endpoint"
```

4. **Push and Create Pull Request**
```bash
git push origin feature/your-feature-name
```
Then create PR on GitHub

### Commit Message Convention
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `refactor:` - Code refactoring
- `test:` - Tests
- `chore:` - Maintenance

### Example Commits
```
feat: Add WebAuthn biometric authentication
fix: Resolve timezone issue in token expiry
docs: Update API documentation for election endpoints
refactor: Simplify database connection logic
test: Add unit tests for blind signature
chore: Update dependencies to Python 3.13
```

---

## 🎯 Next Development Tasks

### Priority 1 (Critical for Demo)
1. **WebAuthn Implementation** - Biometric auth
   - File: `backend/auth-service/app/api/routes/webauthn.py`
   - Test with TouchID/FaceID

2. **Vote Encryption** - ECIES implementation
   - File: `backend/vote-service/app/utils/encryption.py`
   - Use cryptography library

3. **Results Page** - Show tallied results
   - File: `admin-web/src/pages/Results.tsx`
   - Display vote counts, charts

### Priority 2 (Important)
4. **Threshold Key Generation** - Trustees collaborate
   - File: `backend/election-service/app/services/threshold_crypto_service.py`
   - Implement Shamir Secret Sharing

5. **Zero-Knowledge Proofs** - Ballot validity
   - File: `backend/vote-service/app/services/zkp_service.py`
   - Schnorr protocol

6. **Code Sheet PDF** - Generate verification codes
   - File: `backend/code-sheet-service/app/services/pdf_generator.py`
   - Use ReportLab

### Priority 3 (Nice to Have)
7. **Mix-Net** - Anonymize votes
8. **Bulletin Board** - Public hash chain
9. **Mobile App** - Flutter voter interface

---

## 🐛 Common Issues & Solutions

### "Module 'shared' not found"
**Fix:** Make sure you're in service directory and `backend/shared/` exists.
The `sys.path` fix is already in all `main.py` files.

### "Port already in use"
**Fix:** Kill the process:
```powershell
Get-Process -Id (Get-NetTCPConnection -LocalPort 8001).OwningProcess | Stop-Process
```

### "Database connection refused"
**Fix:** Start PostgreSQL:
```powershell
Get-Service postgresql* | Start-Service
```

### "401 Unauthorized" on API calls
**Fix:** Check if you're logged in. Token might have expired (15 min).

### Auth service not auto-reloading
**Fix:** Restart with `--reload` flag:
```powershell
uvicorn app.main:app --port 8001 --reload
```

---

## 📞 Code Locations (Quick Reference)

### Need to add an API endpoint?
- **Auth:** `backend/auth-service/app/api/routes/auth.py`
- **Election:** `backend/election-service/app/api/routes/election.py`
- **Vote:** `backend/vote-service/app/api/routes/vote_submission.py`

### Need to add a frontend page?
- **New page:** `admin-web/src/pages/YourPage.tsx`
- **Add route:** `admin-web/src/App.tsx`
- **API call:** `admin-web/src/services/api.ts`

### Need to change database?
- **Schema:** `scripts/db-init.sql`
- **Connection:** `backend/shared/database.py`
- **SQL queries:** Use `text()` wrapper in route files

### Need to add crypto function?
- **Backend shared:** `backend/shared/crypto_utils.py`
- **Service specific:** `backend/[service]/app/utils/`

---

## 🎓 Learning Resources

### FastAPI
- Official Docs: https://fastapi.tiangao.com/
- Tutorial: https://fastapi.tiangao.com/tutorial/

### React + TypeScript
- React Docs: https://react.dev/
- TypeScript: https://www.typescriptlang.org/docs/

### Cryptography
- Python cryptography: https://cryptography.io/
- Threshold Cryptography: Shamir Secret Sharing
- Blind Signatures: Chaum 1983 paper

### E-Voting
- Helios Voting: https://heliosvoting.org
- Swiss E-Voting Standards

---

## ✅ Pre-Demo Checklist

Before presenting to evaluators:

- [ ] All services running without errors
- [ ] Can create election and add candidates
- [ ] Can approve/reject voter KYC
- [ ] Dashboard shows correct stats
- [ ] No console errors in browser
- [ ] Database has test data
- [ ] README.md updated
- [ ] Git repo clean (no secrets committed)
- [ ] API docs accessible at /docs endpoints

---

## 🤝 Team Communication

### When Making Changes
1. **Communicate** - Tell team what you're working on
2. **Branch** - Always work in feature branches
3. **Test** - Test locally before pushing
4. **Document** - Update docs if you add features
5. **Review** - Ask for code review on PRs

### Before Merging
- Code works locally
- No merge conflicts
- Tests pass (if any)
- Documentation updated
- Teammate reviewed code

---

## 📝 Notes for Next Steps

### Database
- All tables created, populated with admin user
- Connection string uses `postgresql+psycopg://`
- Auto-commits after INSERT/UPDATE

### Backend
- All services support `--reload` for dev
- CORS configured for `localhost:5173`
- JWT tokens expire in 15 minutes
- Admin authorization enforced on `/users/*` endpoints

### Frontend
- Material-UI v5 components
- Redux Toolkit for state
- Axios interceptors handle auth tokens
- Auto-logout on 401 errors

---

**Good luck with development! 🚀**

**Questions?** Check the main [README.md](./README.md) or [START_SERVICES.md](./START_SERVICES.md)

---

**Group F:** MUNASINGHE S.K. (210396E) | JAYASOORIYA D.D.M. (210250D)
