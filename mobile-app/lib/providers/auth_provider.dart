import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../services/storage_service.dart';
import '../services/crypto_service.dart';

class AuthProvider with ChangeNotifier {
  final ApiService _apiService = ApiService();
  final StorageService _storage = StorageService();
  final CryptoService _crypto = CryptoService();

  bool _isLoading = false;
  bool _isAuthenticated = false;
  Map<String, dynamic>? _currentUser;
  String? _error;

  bool get isLoading => _isLoading;
  bool get isAuthenticated => _isAuthenticated;
  Map<String, dynamic>? get currentUser => _currentUser;
  String? get error => _error;

  /// Initialize auth state on app start
  Future<void> initialize() async {
    _isLoading = true;
    notifyListeners();

    try {
      // Check if user has valid token
      final hasToken = await _apiService.isAuthenticated();

      if (hasToken) {
        // Fetch current user info
        final result = await _apiService.getCurrentUser();
        if (result['success']) {
          _isAuthenticated = true;
          _currentUser = result['data'];
          await _storage.saveUserData(result['data']);

          // Generate crypto keys if not exists
          await _ensureCryptoKeys();
        } else {
          _isAuthenticated = false;
          _currentUser = null;
        }
      } else {
        _isAuthenticated = false;
        _currentUser = null;
      }
    } catch (e) {
      _error = 'Initialization error: $e';
      _isAuthenticated = false;
    }

    _isLoading = false;
    notifyListeners();
  }

  /// Register new user
  Future<bool> register({
    required String nic,
    required String email,
    required String fullName,
    required String dateOfBirth,
    required String password,
    String? phoneNumber,
  }) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final result = await _apiService.register(
        nic: nic,
        email: email,
        fullName: fullName,
        dateOfBirth: dateOfBirth,
        password: password,
        phoneNumber: phoneNumber,
      );

      if (result['success']) {
        _isAuthenticated = true;

        // Fetch user data
        await _fetchCurrentUser();

        // Generate crypto keys
        await _ensureCryptoKeys();

        _isLoading = false;
        notifyListeners();
        return true;
      } else {
        _error = result['error'];
        _isLoading = false;
        notifyListeners();
        return false;
      }
    } catch (e) {
      _error = 'Registration error: $e';
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  /// Login user
  Future<bool> login({
    required String email,
    required String password,
  }) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final result = await _apiService.login(
        email: email,
        password: password,
      );

      if (result['success']) {
        _isAuthenticated = true;

        // Fetch user data
        await _fetchCurrentUser();

        // Generate crypto keys if not exists
        await _ensureCryptoKeys();

        _isLoading = false;
        notifyListeners();
        return true;
      } else {
        _error = result['error'];
        _isLoading = false;
        notifyListeners();
        return false;
      }
    } catch (e) {
      _error = 'Login error: $e';
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  /// Logout user
  Future<void> logout() async {
    await _apiService.logout();
    await _storage.clearAll();

    _isAuthenticated = false;
    _currentUser = null;
    _error = null;

    notifyListeners();
  }

  /// Fetch current user data
  Future<void> _fetchCurrentUser() async {
    final result = await _apiService.getCurrentUser();
    if (result['success']) {
      _currentUser = result['data'];
      await _storage.saveUserData(result['data']);
    }
  }

  /// Ensure user has cryptographic keys
  Future<void> _ensureCryptoKeys() async {
    final hasKeys = await _storage.hasKeys();

    if (!hasKeys) {
      // Generate X25519 key pair for ECIES
      final keyPair = _crypto.generateX25519KeyPair();

      // Store keys securely
      await _storage.savePrivateKey(
        _crypto.base64Encode(keyPair['private_key']!),
      );
      await _storage.savePublicKey(
        _crypto.base64Encode(keyPair['public_key']!),
      );
    }
  }

  /// Get user's public key
  Future<String?> getPublicKey() async {
    return await _storage.getPublicKey();
  }

  /// Clear error
  void clearError() {
    _error = null;
    notifyListeners();
  }
}
