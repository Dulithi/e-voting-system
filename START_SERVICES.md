# How to Start All Services Locally

## Prerequisites Check

1. ✅ PostgreSQL installed and running
2. ✅ Python 3.11+ installed
3. ✅ Node.js 20+ installed

## One-Time Database Setup

### Create Database
```powershell
# Open psql (adjust path to your PostgreSQL version)
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres

# In psql console:
CREATE DATABASE evoting_db;
\q
```

### Initialize Database Schema
```powershell
# Run the initialization script
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d evoting_db -f "scripts\db-init.sql"
```

You should see lots of "CREATE TABLE", "CREATE INDEX" messages. ✅

### Verify Database
```powershell
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d evoting_db -c "SELECT email FROM users WHERE is_admin=true;"
```

Should show: `admin@securevote.com` ✅

---

## Step-by-Step Startup

### Open 7 PowerShell Terminals

Open PowerShell 7 times (or use Windows Terminal with multiple tabs)

---

### Terminal 1: Auth Service
```powershell
cd "D:\Dulithi\Semester 7\crypto-project\e-voting-system\backend\auth-service"

# First time only: Create virtual environment and install dependencies
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Set environment variables
$env:DATABASE_URL="postgresql://postgres:StrongDatabase%40201@localhost:5432/evoting_db"
$env:JWT_SECRET_KEY="XXDN41u505T0mk2uiPeqw4Lm6wa3ByNZ3V9B9iRF8Jq1RsePaLk7sDH8VogoJgTH2cy7ZcF"

# Start service
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

Wait for: "Application startup complete" ✅

---

### Terminal 2: Token Service
```powershell
cd "D:\Dulithi\Semester 7\crypto-project\e-voting-system\backend\token-service"

# First time only
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Set environment
$env:DATABASE_URL="postgresql://postgres:StrongDatabase%40201@localhost:5432/evoting_db"

# Start
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

Wait for: "Application startup complete" ✅

---

### Terminal 3: Vote Service
```powershell
cd "D:\Dulithi\Semester 7\crypto-project\e-voting-system\backend\vote-service"

# First time only
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Set environment
$env:DATABASE_URL="postgresql://postgres:StrongDatabase%40201@localhost:5432/evoting_db"

# Start
uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload
```

Wait for: "Application startup complete" ✅

---

### Terminal 4: Bulletin Board Service
```powershell
cd "D:\Dulithi\Semester 7\crypto-project\e-voting-system\backend\bulletin-board-service"

# First time only
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Set environment
$env:DATABASE_URL="postgresql://postgres:StrongDatabase%40201@localhost:5432/evoting_db"

# Start
uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload
```

Wait for: "Application startup complete" ✅

---

### Terminal 5: Election Service
```powershell
cd "D:\Dulithi\Semester 7\crypto-project\e-voting-system\backend\election-service"

# First time only
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Set environment
$env:DATABASE_URL="postgresql://postgres:StrongDatabase%40201@localhost:5432/evoting_db"

# Start
uvicorn app.main:app --host 0.0.0.0 --port 8005 --reload
```

Wait for: "Application startup complete" ✅

---

### Terminal 6: Code Sheet Service
```powershell
cd "D:\Dulithi\Semester 7\crypto-project\e-voting-system\backend\code-sheet-service"

# First time only
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Set environment
$env:DATABASE_URL="postgresql://postgres:StrongDatabase%40201@localhost:5432/evoting_db"

# Start
uvicorn app.main:app --host 0.0.0.0 --port 8006 --reload
```

Wait for: "Application startup complete" ✅

---

### Terminal 7: Admin Web
```powershell
cd "D:\Dulithi\Semester 7\crypto-project\e-voting-system\admin-web"

# First time only
npm install

# Start
npm run dev
```

Wait for: "Local: http://localhost:5173/" ✅

---

## Verify Everything Works

### 1. Check All Services Running
Open these URLs in browser (should show API docs):
- http://localhost:8001/docs ✅ Auth Service
- http://localhost:8002/docs ✅ Token Service
- http://localhost:8003/docs ✅ Vote Service
- http://localhost:8004/docs ✅ Bulletin Board
- http://localhost:8005/docs ✅ Election Service
- http://localhost:8006/docs ✅ Code Sheet Service

### 2. Test Admin Web
- Open: http://localhost:5173
- Login with:
  - Email: `admin@securevote.com`
  - Password: `Admin@123`
- Should see Dashboard ✅

### 3. Test Database
```powershell
psql -U postgres -d evoting_db -c "SELECT email FROM users WHERE is_admin=true;"
```
Should show: `admin@securevote.com` ✅

---

## Quick Restart (After First Setup)

For each service, just activate venv and run uvicorn:

```powershell
# Auth Service (Terminal 1)
cd backend\auth-service; .\venv\Scripts\Activate.ps1; $env:DATABASE_URL="postgresql://postgres:StrongDatabase%40201@localhost:5432/evoting_db"; $env:JWT_SECRET_KEY="XXDN41u505T0mk2uiPeqw4Lm6wa3ByNZ3V9B9iRF8Jq1RsePaLk7sDH8VogoJgTH2cy7ZcF"; uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# Token Service (Terminal 2)
cd backend\token-service; .\venv\Scripts\Activate.ps1; $env:DATABASE_URL="postgresql://postgres:StrongDatabase%40201@localhost:5432/evoting_db"; uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload

# Vote Service (Terminal 3)
cd backend\vote-service; .\venv\Scripts\Activate.ps1; $env:DATABASE_URL="postgresql://postgres:StrongDatabase%40201@localhost:5432/evoting_db"; uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload

# Bulletin Service (Terminal 4)
cd backend\bulletin-board-service; .\venv\Scripts\Activate.ps1; $env:DATABASE_URL="postgresql://postgres:StrongDatabase%40201@localhost:5432/evoting_db"; uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload

# Election Service (Terminal 5)
cd backend\election-service; .\venv\Scripts\Activate.ps1; $env:DATABASE_URL="postgresql://postgres:StrongDatabase%40201@localhost:5432/evoting_db"; uvicorn app.main:app --host 0.0.0.0 --port 8005 --reload

# Code Sheet Service (Terminal 6)
cd backend\code-sheet-service; .\venv\Scripts\Activate.ps1; $env:DATABASE_URL="postgresql://postgres:StrongDatabase%40201@localhost:5432/evoting_db"; uvicorn app.main:app --host 0.0.0.0 --port 8006 --reload

# Admin Web (Terminal 7)
cd admin-web; npm run dev
```

---

## Common Issues

### "Module 'shared' not found"
**Fix:** Make sure you're in the right directory and `backend/shared/` folder exists

### "Port already in use"
**Fix:** Kill the process:
```powershell
Get-Process -Id (Get-NetTCPConnection -LocalPort 8001).OwningProcess | Stop-Process
```

### "Database connection refused"
**Fix:** Start PostgreSQL service:
```powershell
# Check if running
Get-Service -Name postgresql*

# Start if stopped
Start-Service postgresql-x64-15  # (adjust name for your version)
```

### Admin login fails
**Fix:** Check admin user exists:
```powershell
psql -U postgres -d evoting_db -c "SELECT * FROM users WHERE email='admin@securevote.com';"
```

---

## Stop All Services

Press `Ctrl+C` in each terminal window.

---

## Demo Day Checklist

Before presenting:
- [ ] All 7 terminals open and services running
- [ ] Can access http://localhost:5173
- [ ] Can login with admin credentials
- [ ] Can see empty elections list
- [ ] All /docs endpoints accessible
- [ ] PostgreSQL running
- [ ] No error messages in any terminal

**You're ready to demo!** 🎉
