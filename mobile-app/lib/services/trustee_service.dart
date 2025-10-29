import 'dart:convert';
import 'package:http/http.dart' as http;
import '../services/storage_service.dart';

class TrusteeService {
  static const String baseUrl = 'http://192.168.1.112:8005/api/trustee';

  Future<List<Map<String, dynamic>>> getMyElections() async {
    try {
      final storageService = StorageService();
      final userData = await storageService.getUserData();
      if (userData == null || userData['user_id'] == null) {
        throw Exception('User not logged in');
      }

      final userId = userData['user_id'];
      print('📋 [TrusteeService] Fetching elections for user: $userId');

      final response = await http.get(
        Uri.parse('$baseUrl/my-elections/$userId'),
        headers: {'Content-Type': 'application/json'},
      );

      print('📋 [TrusteeService] Response status: ${response.statusCode}');

      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        print('📋 [TrusteeService] Found ${data.length} trustee elections');
        return data.cast<Map<String, dynamic>>();
      } else {
        print('❌ [TrusteeService] Error: ${response.body}');
        throw Exception('Failed to load trustee elections: ${response.body}');
      }
    } catch (e) {
      print('❌ [TrusteeService] Exception: $e');
      rethrow;
    }
  }

  Future<List<Map<String, dynamic>>> getElectionBallots(
      String electionId) async {
    try {
      print('🗳️ [TrusteeService] Fetching ballots for election: $electionId');

      final response = await http.get(
        Uri.parse('$baseUrl/election/$electionId/ballots'),
        headers: {'Content-Type': 'application/json'},
      );

      print('🗳️ [TrusteeService] Response status: ${response.statusCode}');

      if (response.statusCode == 200) {
        final Map<String, dynamic> responseData = json.decode(response.body);
        final List<dynamic> ballots = responseData['ballots'] ?? [];
        print('🗳️ [TrusteeService] Found ${ballots.length} ballots');
        return ballots.cast<Map<String, dynamic>>();
      } else {
        print('❌ [TrusteeService] Error: ${response.body}');
        throw Exception('Failed to load ballots: ${response.body}');
      }
    } catch (e) {
      print('❌ [TrusteeService] Exception: $e');
      rethrow;
    }
  }

  Future<Map<String, dynamic>> submitDecryptionShares({
    required String trusteeId,
    required Map<String, String> decryptionShares,
  }) async {
    try {
      print('🔐 [TrusteeService] Submitting decryption shares');
      print('   Trustee ID: $trusteeId');
      print('   Shares count: ${decryptionShares.length}');

      final response = await http.post(
        Uri.parse('$baseUrl/submit-decryption-share'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'trustee_id': trusteeId,
          'decryption_shares': decryptionShares,
        }),
      );

      print('🔐 [TrusteeService] Response status: ${response.statusCode}');

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        print('✅ [TrusteeService] Shares submitted successfully');
        return data;
      } else {
        print('❌ [TrusteeService] Error: ${response.body}');
        throw Exception('Failed to submit shares: ${response.body}');
      }
    } catch (e) {
      print('❌ [TrusteeService] Exception: $e');
      rethrow;
    }
  }

  Future<Map<String, dynamic>> getDecryptionStatus(String electionId) async {
    try {
      print('📊 [TrusteeService] Fetching decryption status for: $electionId');

      final response = await http.get(
        Uri.parse('$baseUrl/election/$electionId/decryption-status'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        print(
            '📊 [TrusteeService] Decryption status: ${data['trustees_submitted']}/${data['threshold']}');
        return data;
      } else {
        throw Exception('Failed to get decryption status: ${response.body}');
      }
    } catch (e) {
      print('❌ [TrusteeService] Exception: $e');
      rethrow;
    }
  }
}
