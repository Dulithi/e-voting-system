Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  SecureVote Backend Quick Start" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get IP
$ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { 
    $_.InterfaceAlias -notlike "*Loopback*" -and 
    $_.IPAddress -like "192.168.*" 
} | Select-Object -First 1).IPAddress

Write-Host "Your IP Address: $ip" -ForegroundColor Green
Write-Host "Update mobile app with this IP!" -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Run These Commands (4 terminals)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Terminal 1:" -ForegroundColor Yellow
Write-Host "cd backend\auth-service ; .\venv\Scripts\activate ; uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload" -ForegroundColor White
Write-Host ""

Write-Host "Terminal 2:" -ForegroundColor Yellow
Write-Host "cd backend\election-service ; .\venv\Scripts\activate ; uvicorn app.main:app --host 0.0.0.0 --port 8005 --reload" -ForegroundColor White
Write-Host ""

Write-Host "Terminal 3:" -ForegroundColor Yellow
Write-Host "cd backend\vote-service ; .\venv\Scripts\activate ; uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload" -ForegroundColor White
Write-Host ""

Write-Host "Terminal 4:" -ForegroundColor Yellow
Write-Host "cd backend\token-service ; .\venv\Scripts\activate ; uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload" -ForegroundColor White
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Database: postgres / StrongDatabase@201" -ForegroundColor Cyan
Write-Host "  Admin: admin@securevote.com / Admin@123" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
