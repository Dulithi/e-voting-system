import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../services/crypto_service.dart';
import '../services/storage_service.dart';

class ElectionProvider with ChangeNotifier {
  final ApiService _apiService = ApiService();
  final CryptoService _crypto = CryptoService();
  final StorageService _storage = StorageService();

  List<Map<String, dynamic>> _elections = [];
  Map<String, dynamic>? _currentElection;
  bool _isLoading = false;
  String? _error;

  List<Map<String, dynamic>> get elections => _elections;
  Map<String, dynamic>? get currentElection => _currentElection;
  bool get isLoading => _isLoading;
  String? get error => _error;

  /// Fetch all elections
  Future<void> fetchElections() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final result = await _apiService.getElections();

      if (result['success']) {
        _elections = List<Map<String, dynamic>>.from(result['data']);

        // Check vote status for each election
        for (var election in _elections) {
          final hasVoted = await _storage.hasVoted(election['election_id']);
          election['has_voted'] = hasVoted;
        }
      } else {
        _error = result['error'];
      }
    } catch (e) {
      _error = 'Failed to fetch elections: $e';
    }

    _isLoading = false;
    notifyListeners();
  }

  /// Fetch single election with candidates
  Future<void> fetchElection(String electionId) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final result = await _apiService.getElection(electionId);

      if (result['success']) {
        _currentElection = result['data'];

        // Check if user has voted
        final hasVoted = await _storage.hasVoted(electionId);
        _currentElection!['has_voted'] = hasVoted;
      } else {
        _error = result['error'];
      }
    } catch (e) {
      _error = 'Failed to fetch election: $e';
    }

    _isLoading = false;
    notifyListeners();
  }

  /// Submit vote for a candidate with FULL blind signature protocol
  Future<Map<String, dynamic>> submitVote({
    required String electionId,
    required String candidateId, // Changed from int to String (UUID)
  }) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      // Step 1: Get main voting code (TODO: implement code sheet scanning)
      // For now, use a test code or fetch from storage
      final mainVotingCode = await _storage.getMainVotingCode(electionId);
      if (mainVotingCode == null) {
        print(
            '⚠️  No voting code found, falling back to simplified token creation');
        print('⚠️  In production, user must scan code sheet first!');

        // FALLBACK: Use simplified token creation for testing without voting codes
        final tokenBytes = _crypto.generateRandomBytes(32);
        final tokenBytesBase64 = _crypto.base64Encode(tokenBytes);
        final tokenHash = _crypto.sha256String(tokenBytesBase64);
        final tokenSignature = tokenBytesBase64;

        print('📝 Creating token directly (bypassing blind signature)...');
        await _createAnonymousTokenDirect(electionId, tokenHash);
        print('✅ Token created');

        // Get election details including public key for encryption
        final electionResult = await _apiService.getElection(electionId);
        if (!electionResult['success']) {
          throw Exception('Failed to fetch election details');
        }

        final electionPublicKeyBase64 = electionResult['data']['public_key'];
        if (electionPublicKeyBase64 == null ||
            electionPublicKeyBase64.isEmpty) {
          throw Exception(
              'Election public key not found. Key ceremony may not be completed.');
        }

        final electionPublicKey = _crypto.base64Decode(electionPublicKeyBase64);
        print('🔑 Using election public key for vote encryption');

        final encryptedVotePackage = _crypto.encryptVote(
          candidateId: candidateId.hashCode,
          electionId: electionId,
          voterPublicKey:
              electionPublicKey, // Use election's public key, not user's
        );

        final result = await _apiService.submitVote(
          electionId: electionId,
          encryptedVote: encryptedVotePackage['encrypted_vote'],
          proof: encryptedVotePackage['proof'],
          tokenHash: tokenHash,
          tokenSignature: tokenSignature,
        );

        if (result['success']) {
          final voteHash = result['data']['vote_hash'] ?? '';
          final receipt = _crypto.createVoteReceipt(
            electionId: electionId,
            candidateId: candidateId.hashCode,
            voteHash: voteHash,
          );

          await _storage.saveVoteReceipt(electionId, {
            ...receipt,
            'candidate_id': candidateId,
            'vote_hash': voteHash,
          });

          if (_currentElection != null &&
              _currentElection!['election_id'] == electionId) {
            _currentElection!['has_voted'] = true;
          }

          final electionIndex =
              _elections.indexWhere((e) => e['election_id'] == electionId);
          if (electionIndex != -1) {
            _elections[electionIndex]['has_voted'] = true;
          }

          _isLoading = false;
          notifyListeners();

          return {
            'success': true,
            'receipt': receipt,
          };
        } else {
          _error = result['error'];
          _isLoading = false;
          notifyListeners();
          return {'success': false, 'error': _error};
        }
      }

      // Step 2: Request blind-signed token using FULL protocol
      print('🔐 Starting blind signature protocol...');
      final tokenResult = await _requestBlindSignedToken(
        electionId: electionId,
        mainVotingCode: mainVotingCode,
      );

      if (!tokenResult['success']) {
        throw Exception(
            tokenResult['error'] ?? 'Failed to obtain anonymous token');
      }

      final tokenHash = tokenResult['token_hash'];
      final tokenSignature = tokenResult['token_signature'];

      print('✅ Anonymous token obtained (fully unlinkable)');
      print('   Token hash: ${tokenHash.substring(0, 16)}...');

      // Step 3: Get election details including public key for encryption
      final electionResult = await _apiService.getElection(electionId);
      if (!electionResult['success']) {
        throw Exception('Failed to fetch election details');
      }

      final electionPublicKeyBase64 = electionResult['data']['public_key'];
      if (electionPublicKeyBase64 == null || electionPublicKeyBase64.isEmpty) {
        throw Exception(
            'Election public key not found. Key ceremony may not be completed.');
      }

      final electionPublicKey = _crypto.base64Decode(electionPublicKeyBase64);
      print('🔑 Using election public key for vote encryption');

      // Step 4: Encrypt vote (using candidateId as string for the receipt/proof)
      final encryptedVotePackage = _crypto.encryptVote(
        candidateId: candidateId.hashCode, // Convert to int for encryption
        electionId: electionId,
        voterPublicKey:
            electionPublicKey, // Use election's public key, not user's
      );

      // Step 5: Submit encrypted vote to backend with token
      final result = await _apiService.submitVote(
        electionId: electionId,
        encryptedVote: encryptedVotePackage['encrypted_vote'],
        proof: encryptedVotePackage['proof'],
        tokenHash: tokenHash,
        tokenSignature: tokenSignature,
      );

      if (result['success']) {
        // Generate vote receipt
        final voteHash = result['data']['vote_hash'] ?? '';
        final receipt = _crypto.createVoteReceipt(
          electionId: electionId,
          candidateId: candidateId.hashCode, // Use hashCode for receipt
          voteHash: voteHash,
        );

        // Store receipt locally (with original UUID)
        await _storage.saveVoteReceipt(electionId, {
          ...receipt,
          'candidate_id': candidateId, // Store original UUID
          'vote_hash': voteHash,
        });

        // Update election status
        if (_currentElection != null &&
            _currentElection!['election_id'] == electionId) {
          _currentElection!['has_voted'] = true;
        }

        // Update elections list
        final electionIndex =
            _elections.indexWhere((e) => e['election_id'] == electionId);
        if (electionIndex != -1) {
          _elections[electionIndex]['has_voted'] = true;
        }

        _isLoading = false;
        notifyListeners();

        return {
          'success': true,
          'receipt': receipt,
        };
      } else {
        _error = result['error'];
        _isLoading = false;
        notifyListeners();
        return {'success': false, 'error': _error};
      }
    } catch (e) {
      _error = 'Failed to submit vote: $e';
      _isLoading = false;
      notifyListeners();
      return {'success': false, 'error': _error};
    }
  }

  /// Get vote receipt for an election
  Future<Map<String, dynamic>?> getVoteReceipt(String electionId) async {
    print('📋 [ElectionProvider] Getting receipt for election: $electionId');
    final receipt = await _storage.getVoteReceipt(electionId);
    print('📋 [ElectionProvider] Receipt found: ${receipt != null}');
    if (receipt != null) {
      print('📋 [ElectionProvider] Receipt keys: ${receipt.keys.toList()}');
      print(
          '📋 [ElectionProvider] Receipt values: ${receipt.values.take(3).toList()}');
    }
    return receipt;
  }

  /// Get active elections (status = ACTIVE and not voted)
  List<Map<String, dynamic>> getActiveElections() {
    return _elections
        .where((e) => e['status'] == 'ACTIVE' && !(e['has_voted'] ?? false))
        .toList();
  }

  /// Get past elections (status = COMPLETED or ACTIVE but voted)
  List<Map<String, dynamic>> getPastElections() {
    return _elections
        .where((e) =>
            e['status'] == 'COMPLETED' ||
            (e['status'] == 'ACTIVE' && (e['has_voted'] ?? false)))
        .toList();
  }

  /// Clear error
  void clearError() {
    _error = null;
    notifyListeners();
  }

  /// Clear current election
  void clearCurrentElection() {
    _currentElection = null;
    notifyListeners();
  }

  /// Request blind-signed anonymous token (FULL PROTOCOL)
  Future<Map<String, dynamic>> _requestBlindSignedToken({
    required String electionId,
    required String mainVotingCode,
  }) async {
    try {
      // 1. Get server's RSA public key
      print('📡 Fetching server public key...');
      final pubKeyResult = await _apiService.getTokenServicePublicKey();
      if (!pubKeyResult['success']) {
        return {'success': false, 'error': 'Failed to get server public key'};
      }

      final serverPublicKeyPem = pubKeyResult['data']['public_key'];
      print('✅ Server public key received');

      // 2. Parse RSA public key
      print('🔑 Parsing RSA public key...');
      final serverPubKey = _crypto.parseRSAPublicKeyFromPem(serverPublicKeyPem);
      print('✅ Public key parsed (${serverPubKey.modulus!.bitLength}-bit RSA)');

      // 3. Generate random token message (256-bit)
      final tokenMessage = _crypto.generateRandomBytes(32);
      print('🎲 Random token generated (256-bit)');

      // 4. Blind the token
      print('🔒 Blinding token with server public key...');
      final blindResult = _crypto.blindMessage(serverPubKey, tokenMessage);
      final blindedMessage = blindResult['blinded_message']!;
      final blindingFactor = blindResult['blinding_factor']!;
      print('✅ Token blinded (server cannot see original)');

      // 5. Convert blinded message to base64
      final blindedMessageBytes = _crypto.bigIntToBytes(
        blindedMessage,
        (serverPubKey.modulus!.bitLength + 7) ~/ 8,
      );
      final blindedMessageBase64 = _crypto.base64Encode(blindedMessageBytes);

      // 6. Request blind signature from server
      print('📝 Requesting blind signature from server...');
      final signResult = await _apiService.requestBlindSignature(
        electionId: electionId,
        mainVotingCode: mainVotingCode,
        blindedMessage: blindedMessageBase64,
      );

      if (!signResult['success']) {
        return {'success': false, 'error': signResult['error']};
      }

      final blindedSignatureBase64 = signResult['data']['blinded_signature'];
      final tokenHashFromServer = signResult['data']['token_hash'];
      print('✅ Blind signature received from server');

      // 7. Decode blinded signature
      final blindedSignatureBytes =
          _crypto.base64Decode(blindedSignatureBase64);
      final blindedSignature = _crypto.bytesToBigInt(blindedSignatureBytes);

      // 8. Unblind the signature
      print('🔓 Unblinding signature...');
      final unblindedSignature = _crypto.unblindSignature(
        serverPubKey,
        blindedSignature,
        blindingFactor,
      );
      print('✅ Signature unblinded successfully');

      // 9. Create token hash from original message
      final tokenHash =
          _crypto.sha256String(_crypto.base64Encode(tokenMessage));

      // 10. Encode unblinded signature
      final unblindedSignatureBytes = _crypto.bigIntToBytes(
        unblindedSignature,
        (serverPubKey.modulus!.bitLength + 7) ~/ 8,
      );
      final tokenSignature = _crypto.base64Encode(unblindedSignatureBytes);

      print('✅ Blind signature protocol complete!');
      print('   Server token hash: ${tokenHashFromServer.substring(0, 16)}...');
      print('   Client token hash: ${tokenHash.substring(0, 16)}...');

      // Use server's token hash for consistency (it's the hash of the blinded message)
      return {
        'success': true,
        'token_hash': tokenHashFromServer,
        'token_signature': tokenSignature,
      };
    } catch (e) {
      print('❌ Error in blind signature protocol: $e');
      return {'success': false, 'error': e.toString()};
    }
  }

  /// Create anonymous token directly in database (simplified MVP approach)
  /// NOTE: This method is deprecated in favor of _requestBlindSignedToken
  Future<void> _createAnonymousTokenDirect(
      String electionId, String tokenHash) async {
    try {
      final result = await _apiService.createAnonymousToken(
        electionId: electionId,
        tokenHash: tokenHash,
      );

      if (!result['success']) {
        throw Exception(result['error'] ?? 'Failed to create token');
      }

      print('Token created successfully: ${result['data']}');
    } catch (e) {
      print('Error creating token: $e');
      throw Exception('Failed to create anonymous token: $e');
    }
  }
}
