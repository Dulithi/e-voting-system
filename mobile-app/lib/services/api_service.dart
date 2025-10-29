import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:logger/logger.dart';
import 'storage_service.dart';

class ApiService {
  // Change this to your laptop's IP address when testing on iPhone
  // Find it with: ipconfig (Windows) and look for IPv4 Address
  static const String baseUrl = 'http://192.168.1.112'; // CHANGE THIS TO YOUR IP

  // Service ports
  static const String authServiceUrl = '$baseUrl:8001/api';
  static const String electionServiceUrl = '$baseUrl:8005/api/election';
  static const String voteServiceUrl = '$baseUrl:8003/api/vote';
  static const String tokenServiceUrl = '$baseUrl:8002/api/token';

  final logger = Logger();
  final StorageService _storage = StorageService();

  // ============= Auth Service APIs =============

  /// Register new user
  Future<Map<String, dynamic>> register({
    required String nic,
    required String email,
    required String fullName,
    required String dateOfBirth,
    required String password,
    String? phoneNumber,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$authServiceUrl/auth/register'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'nic': nic,
          'email': email,
          'full_name': fullName,
          'date_of_birth': dateOfBirth,
          'phone_number': phoneNumber,
          'password': password,
        }),
      );

      logger.d('Register response: ${response.statusCode}');

      if (response.statusCode == 200) {
        final data = json.decode(response.body);

        // Store tokens
        await _storage.saveAccessToken(data['access_token']);
        await _storage.saveRefreshToken(data['refresh_token']);

        return {'success': true, 'data': data};
      } else {
        final error = json.decode(response.body);
        return {
          'success': false,
          'error': error['detail'] ?? 'Registration failed'
        };
      }
    } catch (e) {
      logger.e('Register error: $e');
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  /// Login user
  Future<Map<String, dynamic>> login({
    required String email,
    required String password,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$authServiceUrl/auth/login'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'email': email,
          'password': password,
        }),
      );

      logger.d('Login response: ${response.statusCode}');

      if (response.statusCode == 200) {
        final data = json.decode(response.body);

        // Store tokens
        await _storage.saveAccessToken(data['access_token']);
        await _storage.saveRefreshToken(data['refresh_token']);

        return {'success': true, 'data': data};
      } else {
        final error = json.decode(response.body);
        return {'success': false, 'error': error['detail'] ?? 'Login failed'};
      }
    } catch (e) {
      logger.e('Login error: $e');
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  /// Get current user info
  Future<Map<String, dynamic>> getCurrentUser() async {
    try {
      final token = await _storage.getAccessToken();
      if (token == null) {
        return {'success': false, 'error': 'Not authenticated'};
      }

      final response = await http.get(
        Uri.parse('$authServiceUrl/auth/me'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      logger.d('Get current user response: ${response.statusCode}');

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return {'success': true, 'data': data};
      } else if (response.statusCode == 401) {
        // Token expired, try refresh
        final refreshed = await refreshToken();
        if (refreshed['success']) {
          return await getCurrentUser(); // Retry
        }
        return {'success': false, 'error': 'Session expired'};
      } else {
        return {'success': false, 'error': 'Failed to get user info'};
      }
    } catch (e) {
      logger.e('Get current user error: $e');
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  /// Refresh access token
  Future<Map<String, dynamic>> refreshToken() async {
    try {
      final token = await _storage.getRefreshToken();
      if (token == null) {
        return {'success': false, 'error': 'No refresh token'};
      }

      final response = await http.post(
        Uri.parse('$authServiceUrl/auth/refresh'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'refresh_token': token}),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        await _storage.saveAccessToken(data['access_token']);
        await _storage.saveRefreshToken(data['refresh_token']);
        return {'success': true, 'data': data};
      } else {
        return {'success': false, 'error': 'Token refresh failed'};
      }
    } catch (e) {
      logger.e('Refresh token error: $e');
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  /// Logout
  Future<void> logout() async {
    await _storage.clearTokens();
  }

  // ============= Election Service APIs =============

  /// Get list of all elections
  Future<Map<String, dynamic>> getElections() async {
    try {
      final response = await http.get(
        Uri.parse('$electionServiceUrl/list'),
        headers: {'Content-Type': 'application/json'},
      );

      logger.d('Get elections response: ${response.statusCode}');

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return {'success': true, 'data': data};
      } else {
        return {'success': false, 'error': 'Failed to fetch elections'};
      }
    } catch (e) {
      logger.e('Get elections error: $e');
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  /// Get single election with candidates
  Future<Map<String, dynamic>> getElection(String electionId) async {
    try {
      final response = await http.get(
        Uri.parse('$electionServiceUrl/$electionId'),
        headers: {'Content-Type': 'application/json'},
      );

      logger.d('Get election response: ${response.statusCode}');

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return {'success': true, 'data': data};
      } else {
        return {'success': false, 'error': 'Failed to fetch election details'};
      }
    } catch (e) {
      logger.e('Get election error: $e');
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  // ============= Vote Service APIs =============

  /// Submit encrypted vote with anonymous token
  Future<Map<String, dynamic>> submitVote({
    required String electionId,
    required Map<String, dynamic> encryptedVote,
    required Map<String, dynamic> proof,
    required String tokenHash,
    required String tokenSignature,
  }) async {
    try {
      final token = await _storage.getAccessToken();
      if (token == null) {
        return {'success': false, 'error': 'Not authenticated'};
      }

      final response = await http.post(
        Uri.parse('$voteServiceUrl/submit'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: json.encode({
          'election_id': electionId,
          'encrypted_vote': encryptedVote,
          'proof': proof,
          'token_hash': tokenHash,
          'token_signature': tokenSignature,
        }),
      );

      logger.d('Submit vote response: ${response.statusCode}');

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return {
          'success': true,
          'data': {
            'ballot_hash': data['ballot_hash'],
            'verification_code': data['verification_code'],
            'vote_hash': data['vote_hash'],
            'message': data['message'] ?? 'Vote submitted successfully'
          }
        };
      } else if (response.statusCode == 401) {
        final refreshed = await refreshToken();
        if (refreshed['success']) {
          return await submitVote(
            electionId: electionId,
            encryptedVote: encryptedVote,
            proof: proof,
            tokenHash: tokenHash,
            tokenSignature: tokenSignature,
          );
        }
        return {'success': false, 'error': 'Session expired'};
      } else {
        try {
          final error = json.decode(response.body);
          return {
            'success': false,
            'error': error['detail'] ?? 'Failed to submit vote'
          };
        } catch (e) {
          return {
            'success': false,
            'error': 'Failed to submit vote: ${response.statusCode}'
          };
        }
      }
    } catch (e) {
      logger.e('Submit vote error: $e');
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  /// Check if user has voted in an election
  Future<Map<String, dynamic>> checkVoteStatus(String electionId) async {
    try {
      final token = await _storage.getAccessToken();
      if (token == null) {
        return {'success': false, 'error': 'Not authenticated'};
      }

      final response = await http.get(
        Uri.parse('$voteServiceUrl/status/$electionId'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      logger.d('Check vote status response: ${response.statusCode}');

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return {'success': true, 'data': data};
      } else if (response.statusCode == 401) {
        final refreshed = await refreshToken();
        if (refreshed['success']) {
          return await checkVoteStatus(electionId);
        }
        return {'success': false, 'error': 'Session expired'};
      } else {
        return {
          'success': false,
          'data': {'has_voted': false}
        };
      }
    } catch (e) {
      logger.e('Check vote status error: $e');
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  // ============= Token Service APIs (Blind Signatures) =============

  /// Create anonymous token directly (simplified MVP approach)
  Future<Map<String, dynamic>> createAnonymousToken({
    required String electionId,
    required String tokenHash,
  }) async {
    try {
      final token = await _storage.getAccessToken();
      if (token == null) {
        return {'success': false, 'error': 'Not authenticated'};
      }

      final response = await http.post(
        Uri.parse('$tokenServiceUrl/create-direct'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: json.encode({
          'election_id': electionId,
          'token_hash': tokenHash,
        }),
      );

      logger.d('Create anonymous token response: ${response.statusCode}');

      if (response.statusCode == 200 || response.statusCode == 201) {
        final data = json.decode(response.body);
        return {'success': true, 'data': data};
      } else if (response.statusCode == 401) {
        final refreshed = await refreshToken();
        if (refreshed['success']) {
          return await createAnonymousToken(
            electionId: electionId,
            tokenHash: tokenHash,
          );
        }
        return {'success': false, 'error': 'Session expired'};
      } else {
        try {
          final error = json.decode(response.body);
          return {
            'success': false,
            'error': error['detail'] ?? 'Failed to create token'
          };
        } catch (e) {
          return {'success': false, 'error': 'Failed to create token'};
        }
      }
    } catch (e) {
      logger.e('Create anonymous token error: $e');
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  /// Get token service public key for blind signing
  Future<Map<String, dynamic>> getTokenServicePublicKey() async {
    try {
      final response = await http.get(
        Uri.parse('$tokenServiceUrl/public-key'),
      );

      logger.d('Get public key response: ${response.statusCode}');

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return {'success': true, 'data': data};
      } else {
        return {'success': false, 'error': 'Failed to get public key'};
      }
    } catch (e) {
      logger.e('Get public key error: $e');
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  /// Request blind signature for anonymous voting token
  Future<Map<String, dynamic>> requestBlindSignature({
    required String electionId,
    required String mainVotingCode,
    required String blindedMessage,
  }) async {
    try {
      final token = await _storage.getAccessToken();
      if (token == null) {
        return {'success': false, 'error': 'Not authenticated'};
      }

      final response = await http.post(
        Uri.parse('$tokenServiceUrl/request-signature'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: json.encode({
          'election_id': electionId,
          'main_voting_code': mainVotingCode,
          'blinded_token': blindedMessage,
        }),
      );

      logger.d('Request blind signature response: ${response.statusCode}');

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return {'success': true, 'data': data};
      } else if (response.statusCode == 401) {
        final refreshed = await refreshToken();
        if (refreshed['success']) {
          return await requestBlindSignature(
            electionId: electionId,
            mainVotingCode: mainVotingCode,
            blindedMessage: blindedMessage,
          );
        }
        return {'success': false, 'error': 'Session expired'};
      } else {
        final error = json.decode(response.body);
        return {
          'success': false,
          'error': error['detail'] ?? 'Failed to get signature'
        };
      }
    } catch (e) {
      logger.e('Request blind signature error: $e');
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  // ============= Helper Methods =============

  /// Check if user is authenticated
  Future<bool> isAuthenticated() async {
    final token = await _storage.getAccessToken();
    return token != null;
  }

  /// Get health status of all services
  Future<Map<String, bool>> checkServicesHealth() async {
    final services = {
      'auth': '$baseUrl:8001/docs',
      'election': '$baseUrl:8005/docs',
      'vote': '$baseUrl:8003/docs',
      'token': '$baseUrl:8002/docs',
    };

    final health = <String, bool>{};

    for (final entry in services.entries) {
      try {
        final response = await http.get(Uri.parse(entry.value)).timeout(
              const Duration(seconds: 3),
            );
        health[entry.key] = response.statusCode == 200;
      } catch (e) {
        health[entry.key] = false;
      }
    }

    return health;
  }
}
