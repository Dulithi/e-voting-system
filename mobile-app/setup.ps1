# SecureVote Mobile App Setup Script
# Run this script to prepare the mobile app for testing

Write-Host "================================" -ForegroundColor Cyan
Write-Host "SecureVote Mobile App Setup" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if Flutter is installed
Write-Host "[1/5] Checking Flutter installation..." -ForegroundColor Yellow
try {
    $flutterVersion = flutter --version 2>&1 | Select-String "Flutter"
    Write-Host "✓ Flutter found: $flutterVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Flutter not found!" -ForegroundColor Red
    Write-Host "Please install Flutter from: https://docs.flutter.dev/get-started/install/windows" -ForegroundColor Yellow
    exit 1
}

# Get network IP
Write-Host ""
Write-Host "[2/5] Detecting your IP address..." -ForegroundColor Yellow
$ipAddress = (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias "Wi-Fi*","Ethernet*" | Where-Object { $_.IPAddress -like "192.168.*" -or $_.IPAddress -like "10.*" }).IPAddress | Select-Object -First 1

if ($ipAddress) {
    Write-Host "✓ Your IP address: $ipAddress" -ForegroundColor Green
    Write-Host "  → Update this in lib/services/api_service.dart line 8" -ForegroundColor Yellow
} else {
    Write-Host "✗ Could not detect IP address" -ForegroundColor Red
    Write-Host "  → Run 'ipconfig' manually and update lib/services/api_service.dart" -ForegroundColor Yellow
}

# Navigate to mobile app directory
Write-Host ""
Write-Host "[3/5] Navigating to mobile app directory..." -ForegroundColor Yellow
$mobileAppPath = "d:\Dulithi\Semester 7\crypto-project\e-voting-system\mobile-app"
if (Test-Path $mobileAppPath) {
    Set-Location $mobileAppPath
    Write-Host "✓ Directory found: $mobileAppPath" -ForegroundColor Green
} else {
    Write-Host "✗ Directory not found: $mobileAppPath" -ForegroundColor Red
    exit 1
}

# Install Flutter dependencies
Write-Host ""
Write-Host "[4/5] Installing Flutter dependencies..." -ForegroundColor Yellow
Write-Host "  This may take a few minutes..." -ForegroundColor Cyan
flutter pub get
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Check for devices
Write-Host ""
Write-Host "[5/5] Checking for connected devices..." -ForegroundColor Yellow
flutter devices
Write-Host ""

# Setup complete
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Update API URL in lib/services/api_service.dart:" -ForegroundColor White
Write-Host "   static const String baseUrl = 'http://$ipAddress';" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Start backend services (4 terminals):" -ForegroundColor White
Write-Host "   Terminal 1: cd backend\auth-service; .\venv\Scripts\activate; uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload" -ForegroundColor Cyan
Write-Host "   Terminal 2: cd backend\election-service; .\venv\Scripts\activate; uvicorn app.main:app --host 0.0.0.0 --port 8005 --reload" -ForegroundColor Cyan
Write-Host "   Terminal 3: cd backend\vote-service; .\venv\Scripts\activate; uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload" -ForegroundColor Cyan
Write-Host "   Terminal 4: cd backend\token-service; .\venv\Scripts\activate; uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Configure firewall (run as Administrator):" -ForegroundColor White
Write-Host "   New-NetFirewallRule -DisplayName 'FastAPI Services' -Direction Inbound -LocalPort 8001-8006 -Protocol TCP -Action Allow" -ForegroundColor Cyan
Write-Host ""
Write-Host "4. Run the mobile app:" -ForegroundColor White
Write-Host "   flutter run" -ForegroundColor Cyan
Write-Host ""
Write-Host "For detailed instructions, see:" -ForegroundColor White
Write-Host "  - QUICKSTART.md" -ForegroundColor Cyan
Write-Host "  - DEPLOYMENT_GUIDE.md" -ForegroundColor Cyan
Write-Host ""

Write-Host "Test Credentials:" -ForegroundColor Yellow
Write-Host "  Email: admin@securevote.com" -ForegroundColor White
Write-Host "  Password: Admin@123" -ForegroundColor White
Write-Host ""
