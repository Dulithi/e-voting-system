# Complete Fix Script

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  SecureVote Backend Fix & Startup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check PostgreSQL
Write-Host "[1/6] Checking PostgreSQL..." -ForegroundColor Yellow
$pgService = Get-Service postgresql* -ErrorAction SilentlyContinue
if ($pgService -and $pgService.Status -eq "Running") {
    Write-Host "[OK] PostgreSQL is running" -ForegroundColor Green
} else {
    Write-Host "[ERROR] PostgreSQL not running. Starting..." -ForegroundColor Red
    Start-Service postgresql-x64-16 -ErrorAction SilentlyContinue
    if ($?) {
        Write-Host "[OK] PostgreSQL started" -ForegroundColor Green
    } else {
        Write-Host "[WARN] Could not start PostgreSQL. Start it manually." -ForegroundColor Yellow
    }
}

# Install python-dotenv in all services
Write-Host ""
Write-Host "[2/6] Installing python-dotenv in all services..." -ForegroundColor Yellow

$services = @("auth-service", "token-service", "vote-service", "election-service")
foreach ($service in $services) {
    $venvPath = "backend\$service\venv\Scripts\activate.ps1"
    if (Test-Path $venvPath) {
        Write-Host "  Installing in $service..." -NoNewline
        & "backend\$service\venv\Scripts\python.exe" -m pip install python-dotenv --quiet 2>$null
        Write-Host " OK" -ForegroundColor Green
    } else {
        Write-Host "  WARNING: Venv not found for $service" -ForegroundColor Yellow
    }
}

# Test database connection
Write-Host ""
Write-Host "[3/6] Testing database connection..." -ForegroundColor Yellow
$env:PGPASSWORD = "StrongDatabase@201"
$dbTest = psql -U postgres -d evoting_db -c "SELECT 1" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "OK - Database connection successful" -ForegroundColor Green
} else {
    Write-Host "ERROR - Database connection failed" -ForegroundColor Red
    Write-Host "  Run: psql -U postgres" -ForegroundColor Yellow
    Write-Host "  Then: CREATE DATABASE evoting_db;" -ForegroundColor Yellow
}

# Get IP address for mobile app
Write-Host ""
Write-Host "[4/6] Detecting IP address for mobile app..." -ForegroundColor Yellow
$ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { 
    $_.InterfaceAlias -notlike "*Loopback*" -and 
    $_.InterfaceAlias -notlike "*VirtualBox*" -and
    $_.IPAddress -like "192.168.*" 
} | Select-Object -First 1).IPAddress

if ($ip) {
    Write-Host "OK - Your IP: $ip" -ForegroundColor Green
    Write-Host "  Update mobile-app/lib/services/api_service.dart line 8:" -ForegroundColor Cyan
    Write-Host "  static const String baseUrl = 'http://$ip';" -ForegroundColor White
} else {
    Write-Host "WARNING - Could not detect IP. Use 'ipconfig' manually" -ForegroundColor Yellow
}

# Check firewall
Write-Host ""
Write-Host "[5/6] Checking firewall rules..." -ForegroundColor Yellow
$fwRule = Get-NetFirewallRule -DisplayName "FastAPI Services" -ErrorAction SilentlyContinue
if ($fwRule) {
    Write-Host "OK - Firewall rule exists" -ForegroundColor Green
} else {
    Write-Host "WARNING - Firewall rule not found. Creating..." -ForegroundColor Yellow
    Write-Host "  Run as Administrator:" -ForegroundColor Cyan
    Write-Host "  New-NetFirewallRule -DisplayName 'FastAPI Services' -Direction Inbound -LocalPort 8001-8006 -Protocol TCP -Action Allow" -ForegroundColor White
}

Write-Host ""
Write-Host "[6/6] Services ready to start!" -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Start Services (4 separate terminals)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Terminal 1 - Auth Service:" -ForegroundColor Yellow
Write-Host "cd backend\auth-service ; .\venv\Scripts\activate ; uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload" -ForegroundColor White
Write-Host ""

Write-Host "Terminal 2 - Token Service:" -ForegroundColor Yellow  
Write-Host "cd backend\token-service ; .\venv\Scripts\activate ; uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload" -ForegroundColor White
Write-Host ""

Write-Host "Terminal 3 - Vote Service:" -ForegroundColor Yellow
Write-Host "cd backend\vote-service ; .\venv\Scripts\activate ; uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload" -ForegroundColor White
Write-Host ""

Write-Host "Terminal 4 - Election Service:" -ForegroundColor Yellow
Write-Host "cd backend\election-service ; .\venv\Scripts\activate ; uvicorn app.main:app --host 0.0.0.0 --port 8005 --reload" -ForegroundColor White
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Database Info" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Username: postgres" -ForegroundColor White
Write-Host "Password: StrongDatabase@201" -ForegroundColor White
Write-Host "Database: evoting_db" -ForegroundColor White
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Admin vs Voter Authentication" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "OK - SAME auth service for both" -ForegroundColor Green
Write-Host "  - Admin: is_admin = TRUE in users table" -ForegroundColor White
Write-Host "  - Voter: is_admin = FALSE (default)" -ForegroundColor White
Write-Host ""
Write-Host "Admin Login (Web):" -ForegroundColor Yellow
Write-Host "  Email: admin@securevote.com" -ForegroundColor White
Write-Host "  Password: Admin@123" -ForegroundColor White
Write-Host ""
Write-Host "Voter Registration (Mobile):" -ForegroundColor Yellow
Write-Host "  Register via mobile app" -ForegroundColor White
Write-Host "  Automatically set as voter (is_admin = FALSE)" -ForegroundColor White
Write-Host ""

Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
