# Mobile App Quick Start

## 🚀 Steps to Run

### 1. Install Dependencies
```powershell
cd "d:\Dulithi\Semester 7\crypto-project\e-voting-system\mobile-app"
flutter pub get
```

### 2. Update API URL
Open `lib/services/api_service.dart` and update line 8:
```dart
static const String baseUrl = 'http://YOUR_IP_HERE'; // Replace with your laptop's IP
```

Find your IP:
```powershell
ipconfig
# Look for IPv4 Address, e.g., 192.168.1.100
```

### 3. Start Backend Services
```powershell
# Auth Service
cd ..\backend\auth-service
.\venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# Election Service (new terminal)
cd ..\election-service
.\venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8005 --reload
```

### 4. Run Mobile App
```powershell
cd ..\..\mobile-app
flutter run
```

**Select device:**
- Android Emulator (easier on Windows)
- Physical Android device via USB
- iPhone (requires macOS - see DEPLOYMENT_GUIDE.md)

## 📱 Test Credentials
- **Email:** admin@securevote.com
- **Password:** Admin@123

Or register a new user in the app.

## ✅ Features Implemented

### Security & Cryptography
- ✅ **X25519 ECDH** - Key agreement for ECIES
- ✅ **AES-256-GCM** - Symmetric encryption
- ✅ **ECIES** - End-to-end vote encryption
- ✅ **SHA-256** - Hashing
- ✅ **HKDF** - Key derivation
- ✅ **RSA-2048** - Blind signature infrastructure
- ✅ **Secure Storage** - Keychain/Keystore integration

### App Features
- ✅ User registration & login
- ✅ JWT authentication
- ✅ View active elections
- ✅ View election candidates
- ✅ Cast encrypted vote
- ✅ Generate vote receipt with QR code
- ✅ Prevent double voting
- ✅ KYC status display

### UI/UX
- ✅ Material Design 3
- ✅ Loading states
- ✅ Error handling
- ✅ Empty states
- ✅ Responsive layout

## 🔐 Security Highlights

All votes are encrypted using **ECIES** (Elliptic Curve Integrated Encryption Scheme):
1. User generates X25519 key pair on first login
2. Private key stored in secure storage (never leaves device)
3. Vote encrypted with user's public key
4. Server cannot decrypt individual votes
5. Threshold trustees needed to decrypt results

## 🐛 Common Issues

**Cannot connect to backend:**
- Check IP address in api_service.dart
- Ensure services run with `--host 0.0.0.0`
- Allow firewall for ports 8001, 8005

**Flutter not found:**
```powershell
flutter doctor
# Fix any issues shown
```

**Android emulator not starting:**
- Open Android Studio → Device Manager
- Create new virtual device (Pixel 6 Pro, API 34)

## 📖 Full Documentation
See `DEPLOYMENT_GUIDE.md` for complete setup instructions including iPhone deployment.

---

**Group F** - MUNASINGHE S.K. (210396E) | JAYASOORIYA D.D.M. (210250D)
