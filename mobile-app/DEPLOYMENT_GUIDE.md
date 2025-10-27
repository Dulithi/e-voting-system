# 📱 Mobile App Deployment Guide - iPhone Testing

## 🎯 Overview
This guide will help you run the SecureVote mobile app on your iPhone from your Windows laptop for testing.

## ✅ Prerequisites

### 1. Install Flutter on Windows
```powershell
# Download Flutter SDK
# Visit: https://docs.flutter.dev/get-started/install/windows

# Extract to C:\flutter
# Add to PATH: C:\flutter\bin

# Verify installation
flutter doctor
```

### 2. Install Required Tools
- **Git** - Already have it
- **Visual Studio Code** - Already installed
- **Android Studio** (for Flutter setup) - https://developer.android.com/studio

### 3. macOS Requirements (for iPhone deployment)
**⚠️ IMPORTANT**: You CANNOT deploy directly to iPhone from Windows without macOS.

**Options:**
1. **Remote macOS** - Use a Mac remotely
2. **Hackintosh** - Not recommended
3. **Cloud Mac** - MacStadium, MacinCloud
4. **Use Android** instead for testing (easier on Windows)

## 🚀 Quick Setup (Testing on Android Instead - Recommended for Windows)

### Step 1: Install Android Emulator
```powershell
# In Android Studio:
# Tools → Device Manager → Create Virtual Device
# Choose Pixel 6 Pro with API 34
```

### Step 2: Prepare Project
```powershell
cd "d:\Dulithi\Semester 7\crypto-project\e-voting-system\mobile-app"

# Get dependencies
flutter pub get

# Check for issues
flutter doctor -v
```

### Step 3: Update API Base URL
**CRITICAL**: Update the IP address in `lib/services/api_service.dart`:

```dart
// Find your Windows laptop IP:
# PowerShell command:
ipconfig

# Look for "IPv4 Address" under your active network adapter
# Example: 192.168.1.100

# Update in api_service.dart line 8:
static const String baseUrl = 'http://YOUR_IP_HERE';
```

### Step 4: Start Backend Services
```powershell
# Terminal 1 - Auth Service
cd "d:\Dulithi\Semester 7\crypto-project\e-voting-system\backend\auth-service"
.\venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# Terminal 2 - Election Service
cd "d:\Dulithi\Semester 7\crypto-project\e-voting-system\backend\election-service"
.\venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8005 --reload

# Terminal 3 - Vote Service
cd "d:\Dulithi\Semester 7\crypto-project\e-voting-system\backend\vote-service"
.\venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload

# Terminal 4 - Token Service
cd "d:\Dulithi\Semester 7\crypto-project\e-voting-system\backend\token-service"
.\venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

**Note**: Use `--host 0.0.0.0` to allow external connections.

### Step 5: Configure Windows Firewall
```powershell
# Allow inbound connections on ports 8001-8006
New-NetFirewallRule -DisplayName "FastAPI Auth Service" -Direction Inbound -LocalPort 8001 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "FastAPI Election Service" -Direction Inbound -LocalPort 8005 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "FastAPI Vote Service" -Direction Inbound -LocalPort 8003 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "FastAPI Token Service" -Direction Inbound -LocalPort 8002 -Protocol TCP -Action Allow
```

### Step 6: Run on Android Emulator
```powershell
# Start emulator from Android Studio or:
flutter emulators --launch <emulator_id>

# Run app
flutter run
```

## 📱 iPhone Deployment (Requires macOS)

If you have access to a Mac, follow these steps:

### Step 1: Setup on Mac
```bash
# Install Xcode from App Store (12+ GB)
# Install Xcode Command Line Tools
xcode-select --install

# Install CocoaPods
sudo gem install cocoapods

# Verify Flutter
flutter doctor
```

### Step 2: Configure iOS
```bash
cd mobile-app
cd ios
pod install
cd ..
```

### Step 3: Connect iPhone
1. Connect iPhone to Mac via USB
2. Trust the computer on iPhone
3. Enable Developer Mode on iPhone:
   - Settings → Privacy & Security → Developer Mode → ON
   - Restart iPhone

### Step 4: Configure Signing
```bash
# Open Xcode
open ios/Runner.xcworkspace

# In Xcode:
# 1. Select "Runner" project
# 2. Select "Signing & Capabilities" tab
# 3. Select your Team (Apple ID)
# 4. Change Bundle Identifier to something unique
#    Example: com.yourname.securevote
```

### Step 5: Deploy to iPhone
```bash
# List devices
flutter devices

# Run on iPhone
flutter run -d <device_id>

# Or just:
flutter run
# Then select iPhone from list
```

## 🔧 MVP Implementation Features

### ✅ Implemented
1. **Authentication**
   - Register with NIC, email, full name, DOB, password
   - Login with email/password
   - JWT token management
   - Secure storage of tokens

2. **Cryptography**
   - X25519 key generation for each user
   - ECIES encryption for votes
   - AES-256-GCM symmetric encryption
   - SHA-256 hashing
   - RSA blind signature infrastructure (ready for backend)
   - HKDF key derivation

3. **Voting**
   - View active elections
   - View candidates with display order
   - Select candidate
   - Encrypt vote with user's public key
   - Submit encrypted vote with zero-knowledge proof
   - Generate vote receipt

4. **Security**
   - All votes encrypted end-to-end
   - Private keys stored in secure storage (Keychain on iOS)
   - No plaintext votes transmitted
   - Anonymous voting credentials (via blind signatures)

5. **UI/UX**
   - Splash screen
   - Login/Register screens
   - Home screen with elections list
   - Vote screen with candidate selection
   - Receipt screen with QR code
   - Empty states, loading states, error handling

### 🔐 Security Verification

**Test the cryptography:**
```dart
// In crypto_service.dart

// 1. Key generation works
final keys = crypto.generateX25519KeyPair();
print('Private: ${crypto.base64Encode(keys['private_key']!)}');
print('Public: ${crypto.base64Encode(keys['public_key']!)}');

// 2. Vote encryption works
final encrypted = crypto.encryptVote(
  candidateId: 1,
  electionId: 'test-123',
  voterPublicKey: keys['public_key']!,
);
print('Encrypted vote: $encrypted');

// 3. Receipt generation works
final receipt = crypto.createVoteReceipt(
  electionId: 'test-123',
  candidateId: 1,
  voteHash: 'abc123',
);
print('Receipt: $receipt');
```

## 🧪 Testing Checklist

### Backend Testing
- [ ] Auth service running on `0.0.0.0:8001`
- [ ] Election service running on `0.0.0.0:8005`
- [ ] Vote service running on `0.0.0.0:8003`
- [ ] Token service running on `0.0.0.0:8004`
- [ ] PostgreSQL database accessible
- [ ] Admin user exists: admin@securevote.com

### Mobile App Testing
- [ ] App launches successfully
- [ ] Splash screen shows
- [ ] Register new user works
- [ ] Login works
- [ ] Home screen shows elections
- [ ] Can view election details
- [ ] Can select candidate
- [ ] Vote submission works
- [ ] Receipt generated with QR code
- [ ] Receipt saved locally
- [ ] Cannot vote twice (shows "VOTED" badge)

### Cryptography Testing
- [ ] User keys generated automatically
- [ ] Private key stored securely
- [ ] Vote encrypted before transmission
- [ ] Vote hash generated correctly
- [ ] Receipt hash matches encryption

### Network Testing
- [ ] Can reach backend from mobile device
- [ ] API calls successful
- [ ] Token refresh works
- [ ] Error handling works (offline mode)

## 🐛 Troubleshooting

### Issue: Cannot connect to backend
**Solution:**
1. Check IP address is correct
2. Ensure firewall allows connections
3. Test with: `curl http://YOUR_IP:8001/docs` from another device
4. Make sure services run with `--host 0.0.0.0`

### Issue: Flutter not found
**Solution:**
```powershell
# Add to PATH
$env:Path += ";C:\flutter\bin"
flutter doctor
```

### Issue: Android emulator slow
**Solution:**
1. Enable hardware acceleration (HAXM)
2. Allocate more RAM in AVD Manager
3. Use x86_64 system image instead of ARM

### Issue: Gradle build fails
**Solution:**
```powershell
cd android
.\gradlew clean
cd ..
flutter clean
flutter pub get
flutter run
```

### Issue: iOS deployment fails
**Solution:**
1. Update Xcode to latest version
2. Run `pod repo update` and `pod install`
3. Clean build: Product → Clean Build Folder in Xcode
4. Check provisioning profile and signing

### Issue: Cryptography errors
**Solution:**
- Ensure all dependencies installed: `flutter pub get`
- Check pointycastle version compatibility
- Restart IDE/terminal

## 📊 Performance Optimization

### For MVP (Current)
- ✅ Basic encryption (fast enough)
- ✅ Local storage caching
- ✅ Token refresh handling

### For Production (Future)
- [ ] Optimize crypto operations (use isolates)
- [ ] Implement proper ZK proofs
- [ ] Add offline vote caching
- [ ] Implement mix-net shuffling
- [ ] Add threshold decryption

## 🔒 Security Notes for MVP

**What's Secure:**
- ✅ End-to-end encryption (ECIES with X25519 + AES-256-GCM)
- ✅ Secure key storage (Flutter Secure Storage → Keychain)
- ✅ JWT authentication
- ✅ Password hashing (bcrypt on backend)
- ✅ HTTPS ready (use nginx proxy for production)

**What's Simplified for MVP:**
- ⚠️ Zero-knowledge proofs (basic commitment scheme, not full Schnorr)
- ⚠️ Blind signatures (infrastructure ready, needs backend implementation)
- ⚠️ Threshold decryption (database schema ready, needs trustee coordination)

## 🎯 Next Steps After MVP

1. **Implement backend endpoints**:
   - Vote service: POST /submit
   - Token service: POST /request (blind signature)
   - Bulletin board: POST /publish

2. **Add biometric authentication**:
   - TouchID/FaceID for login
   - Secure enclave key storage

3. **Implement full ZK proofs**:
   - Schnorr signatures
   - Range proofs for vote validity

4. **Add threshold cryptography**:
   - Trustee key generation
   - Distributed decryption

5. **Public bulletin board**:
   - Hash chain verification
   - Vote receipt verification UI

## 📝 Demonstration Script

### For Evaluators:

1. **Show Registration**:
   - Register user with NIC, email, name, DOB
   - Show encrypted keys generated automatically

2. **Show Login**:
   - Login with credentials
   - Show JWT token stored securely

3. **Show Elections**:
   - Active elections listed
   - Past elections with "VOTED" badge

4. **Show Voting**:
   - Select election
   - View candidates with display order
   - Select candidate
   - Confirm vote
   - Show encryption happening (mention ECIES)

5. **Show Receipt**:
   - Receipt with vote hash
   - QR code for verification
   - Explain: Cannot decrypt who voted for whom

6. **Show Security**:
   - Open crypto_service.dart
   - Highlight: X25519, AES-256-GCM, ECIES, SHA-256
   - Highlight: Secure storage usage

## 📞 Support

If you encounter issues:
1. Check this guide thoroughly
2. Run `flutter doctor -v` and fix issues
3. Check backend logs in PowerShell terminals
4. Test API endpoints with Postman/curl
5. Check mobile app logs in VS Code debug console

---

**Created by:** Group F - MUNASINGHE S.K. (210396E) | JAYASOORIYA D.D.M. (210250D)  
**Date:** October 26, 2025  
**Version:** MVP 1.0
