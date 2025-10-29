import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';

class StorageService {
  static final StorageService _instance = StorageService._internal();
  factory StorageService() => _instance;
  StorageService._internal();

  // Secure storage for sensitive data (tokens, keys)
  final _secureStorage = const FlutterSecureStorage(
    aOptions: AndroidOptions(
      encryptedSharedPreferences: true,
    ),
    iOptions: IOSOptions(
      accessibility: KeychainAccessibility.first_unlock,
    ),
  );

  // Keys for secure storage
  static const String _keyAccessToken = 'access_token';
  static const String _keyRefreshToken = 'refresh_token';
  static const String _keyPrivateKey = 'private_key';
  static const String _keyPublicKey = 'public_key';
  static const String _keyUserData = 'user_data';

  // Keys for regular storage
  static const String _keyHasSeenOnboarding = 'has_seen_onboarding';
  static const String _keyVoteReceipts = 'vote_receipts';

  // ============= Token Management =============

  /// Save access token (JWT)
  Future<void> saveAccessToken(String token) async {
    await _secureStorage.write(key: _keyAccessToken, value: token);
  }

  /// Get access token
  Future<String?> getAccessToken() async {
    return await _secureStorage.read(key: _keyAccessToken);
  }

  /// Save refresh token
  Future<void> saveRefreshToken(String token) async {
    await _secureStorage.write(key: _keyRefreshToken, value: token);
  }

  /// Get refresh token
  Future<String?> getRefreshToken() async {
    return await _secureStorage.read(key: _keyRefreshToken);
  }

  /// Clear all tokens (logout)
  Future<void> clearTokens() async {
    await _secureStorage.delete(key: _keyAccessToken);
    await _secureStorage.delete(key: _keyRefreshToken);
  }

  // ============= Cryptographic Keys =============

  /// Save user's private key (X25519 for ECIES)
  Future<void> savePrivateKey(String key) async {
    await _secureStorage.write(key: _keyPrivateKey, value: key);
  }

  /// Get user's private key
  Future<String?> getPrivateKey() async {
    return await _secureStorage.read(key: _keyPrivateKey);
  }

  /// Save user's public key
  Future<void> savePublicKey(String key) async {
    await _secureStorage.write(key: _keyPublicKey, value: key);
  }

  /// Get user's public key
  Future<String?> getPublicKey() async {
    return await _secureStorage.read(key: _keyPublicKey);
  }

  /// Check if user has generated keys
  Future<bool> hasKeys() async {
    final privateKey = await getPrivateKey();
    final publicKey = await getPublicKey();
    return privateKey != null && publicKey != null;
  }

  // ============= User Data =============

  /// Save user data
  Future<void> saveUserData(Map<String, dynamic> userData) async {
    await _secureStorage.write(
      key: _keyUserData,
      value: json.encode(userData),
    );
  }

  /// Get user data
  Future<Map<String, dynamic>?> getUserData() async {
    final data = await _secureStorage.read(key: _keyUserData);
    if (data == null) return null;
    return json.decode(data) as Map<String, dynamic>;
  }

  /// Clear user data
  Future<void> clearUserData() async {
    await _secureStorage.delete(key: _keyUserData);
  }

  // ============= Vote Receipts =============

  /// Save vote receipt
  Future<void> saveVoteReceipt(
      String electionId, Map<String, dynamic> receipt) async {
    final prefs = await SharedPreferences.getInstance();
    final receipts = await getVoteReceipts();
    receipts[electionId] = receipt;
    await prefs.setString(_keyVoteReceipts, json.encode(receipts));
  }

  /// Get all vote receipts
  Future<Map<String, dynamic>> getVoteReceipts() async {
    final prefs = await SharedPreferences.getInstance();
    final data = prefs.getString(_keyVoteReceipts);
    if (data == null) return {};
    return json.decode(data) as Map<String, dynamic>;
  }

  /// Get receipt for specific election
  Future<Map<String, dynamic>?> getVoteReceipt(String electionId) async {
    final receipts = await getVoteReceipts();
    return receipts[electionId] as Map<String, dynamic>?;
  }

  /// Check if user has receipt for election (i.e., has voted)
  Future<bool> hasVoted(String electionId) async {
    final receipt = await getVoteReceipt(electionId);
    return receipt != null;
  }

  // ============= Onboarding =============

  /// Mark onboarding as seen
  Future<void> setOnboardingSeen() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_keyHasSeenOnboarding, true);
  }

  /// Check if user has seen onboarding
  Future<bool> hasSeenOnboarding() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getBool(_keyHasSeenOnboarding) ?? false;
  }

  // ============= Voting Codes =============

  /// Save main voting code for an election
  Future<void> saveMainVotingCode(String electionId, String code) async {
    await _secureStorage.write(key: 'voting_code_$electionId', value: code);
  }

  /// Get main voting code for an election
  Future<String?> getMainVotingCode(String electionId) async {
    return await _secureStorage.read(key: 'voting_code_$electionId');
  }

  // ============= Clear All Data =============

  /// Clear all stored data (use when logging out or resetting)
  Future<void> clearAll() async {
    await _secureStorage.deleteAll();
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();
  }

  // ============= Biometric =============

  /// Check if biometric is enabled
  Future<bool> isBiometricEnabled() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getBool('biometric_enabled') ?? false;
  }

  /// Set biometric enabled
  Future<void> setBiometricEnabled(bool enabled) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('biometric_enabled', enabled);
  }
}
