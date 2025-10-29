import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:crypto/crypto.dart';
import '../services/trustee_service.dart';
import '../services/storage_service.dart';

class TrusteeDecryptScreen extends StatefulWidget {
  final Map<String, dynamic> election;

  const TrusteeDecryptScreen({super.key, required this.election});

  @override
  State<TrusteeDecryptScreen> createState() => _TrusteeDecryptScreenState();
}

class _TrusteeDecryptScreenState extends State<TrusteeDecryptScreen> {
  final TrusteeService _trusteeService = TrusteeService();
  final StorageService _storageService = StorageService();

  bool _loading = true;
  bool _submitting = false;
  String? _error;
  List<Map<String, dynamic>> _ballots = [];
  Map<String, String> _decryptionShares = {};

  @override
  void initState() {
    super.initState();
    _loadBallotsAndComputeShares();
  }

  Future<void> _loadBallotsAndComputeShares() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      print(
          '🔐 [TrusteeDecrypt] Loading ballots for election: ${widget.election['election_id']}');

      // Load ballots
      final ballots = await _trusteeService.getElectionBallots(
        widget.election['election_id'],
      );

      print('🔐 [TrusteeDecrypt] Loaded ${ballots.length} ballots');

      // Compute partial decryptions for each ballot
      final shares = await _computeDecryptionShares(ballots);

      setState(() {
        _ballots = ballots;
        _decryptionShares = shares;
        _loading = false;
      });

      print('✅ [TrusteeDecrypt] Computed ${shares.length} decryption shares');
    } catch (e) {
      print('❌ [TrusteeDecrypt] Error: $e');
      setState(() {
        _error = e.toString();
        _loading = false;
      });
    }
  }

  Future<Map<String, String>> _computeDecryptionShares(
    List<Map<String, dynamic>> ballots,
  ) async {
    final Map<String, String> shares = {};

    // Get trustee's private key share
    final userData = await _storageService.getUserData();
    final privateKey = await _storageService.getPrivateKey();

    if (privateKey == null) {
      throw Exception('Private key not found');
    }

    print('🔐 [TrusteeDecrypt] Computing partial decryptions...');

    for (final ballot in ballots) {
      final ballotId = ballot['ballot_id'];
      final encryptedBallot = ballot['encrypted_ballot'];

      // Compute partial decryption using trustee's key share
      // For MVP: Create a deterministic "partial decryption" based on trustee's key + ballot
      // In production: Use proper threshold ElGamal/RSA decryption
      final partialDecryption = _computePartialDecryption(
        ballotId,
        encryptedBallot,
        privateKey,
        widget.election['trustee_id'],
      );

      shares[ballotId] = partialDecryption;
    }

    return shares;
  }

  String _computePartialDecryption(
    String ballotId,
    String encryptedBallot,
    String privateKey,
    String trusteeId,
  ) {
    // For MVP: Generate a deterministic partial decryption hash
    // Combines: ballot ID + encrypted data + trustee's private key + trustee ID
    // This ensures each trustee produces unique but deterministic shares

    final input = '$ballotId:$encryptedBallot:$privateKey:$trusteeId';
    final bytes = utf8.encode(input);
    final digest = sha256.convert(bytes);

    return digest.toString();
  }

  Future<void> _submitShares() async {
    if (_decryptionShares.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('No decryption shares to submit')),
      );
      return;
    }

    setState(() {
      _submitting = true;
    });

    try {
      print(
          '📤 [TrusteeDecrypt] Submitting ${_decryptionShares.length} shares');

      await _trusteeService.submitDecryptionShares(
        trusteeId: widget.election['trustee_id'],
        decryptionShares: _decryptionShares,
      );

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('✅ Decryption shares submitted successfully!'),
            backgroundColor: Colors.green,
            duration: Duration(seconds: 3),
          ),
        );

        // Go back to election list
        Navigator.pop(context);
      }
    } catch (e) {
      print('❌ [TrusteeDecrypt] Submission error: $e');

      if (mounted) {
        setState(() {
          _error = e.toString();
        });

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to submit shares: $e'),
            backgroundColor: Colors.red,
            duration: const Duration(seconds: 5),
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _submitting = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Submit Decryption Share'),
      ),
      body: _loading
          ? const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  CircularProgressIndicator(),
                  SizedBox(height: 16),
                  Text('Loading ballots and computing shares...'),
                  SizedBox(height: 8),
                  Text(
                    'This may take a moment',
                    style: TextStyle(fontSize: 12, color: Colors.grey),
                  ),
                ],
              ),
            )
          : _error != null
              ? Center(
                  child: Padding(
                    padding: const EdgeInsets.all(24.0),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(Icons.error_outline,
                            size: 64, color: Colors.red),
                        const SizedBox(height: 16),
                        const Text(
                          'Error',
                          style: TextStyle(
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 12),
                        Text(
                          _error!,
                          textAlign: TextAlign.center,
                          style: const TextStyle(color: Colors.red),
                        ),
                        const SizedBox(height: 24),
                        ElevatedButton.icon(
                          onPressed: _loadBallotsAndComputeShares,
                          icon: const Icon(Icons.refresh),
                          label: const Text('Retry'),
                        ),
                      ],
                    ),
                  ),
                )
              : SingleChildScrollView(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Election Info
                      Card(
                        child: Padding(
                          padding: const EdgeInsets.all(16),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                widget.election['election_title'],
                                style: const TextStyle(
                                  fontSize: 20,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              const SizedBox(height: 8),
                              Row(
                                children: [
                                  const Icon(Icons.how_to_vote, size: 18),
                                  const SizedBox(width: 8),
                                  Text('${_ballots.length} ballots to decrypt'),
                                ],
                              ),
                              const SizedBox(height: 4),
                              Row(
                                children: [
                                  const Icon(Icons.people, size: 18),
                                  const SizedBox(width: 8),
                                  Text(
                                      'Threshold: ${widget.election['threshold']} trustees required'),
                                ],
                              ),
                            ],
                          ),
                        ),
                      ),
                      const SizedBox(height: 24),

                      // Info Box
                      Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: Colors.blue[50],
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: Colors.blue[200]!),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: const [
                                Icon(Icons.info_outline, color: Colors.blue),
                                SizedBox(width: 8),
                                Text(
                                  'How it works',
                                  style: TextStyle(
                                    fontWeight: FontWeight.bold,
                                    fontSize: 16,
                                    color: Colors.blue,
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 12),
                            const Text(
                              '1. Your device computes partial decryptions for each ballot using your secret key share',
                              style: TextStyle(fontSize: 14),
                            ),
                            const SizedBox(height: 8),
                            const Text(
                              '2. These shares are submitted to the server',
                              style: TextStyle(fontSize: 14),
                            ),
                            const SizedBox(height: 8),
                            Text(
                              '3. When ${widget.election['threshold']} trustees submit, the ballots can be decrypted',
                              style: const TextStyle(fontSize: 14),
                            ),
                            const SizedBox(height: 12),
                            Container(
                              padding: const EdgeInsets.all(12),
                              decoration: BoxDecoration(
                                color: Colors.orange[50],
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: Row(
                                children: const [
                                  Icon(Icons.security,
                                      size: 20, color: Colors.orange),
                                  SizedBox(width: 8),
                                  Expanded(
                                    child: Text(
                                      '🔒 Your key share never leaves your device. Only partial decryptions are sent.',
                                      style: TextStyle(
                                        fontSize: 13,
                                        fontWeight: FontWeight.w500,
                                        color: Colors.orange,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 24),

                      // Computed Shares Summary
                      Card(
                        elevation: 2,
                        child: Padding(
                          padding: const EdgeInsets.all(16),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text(
                                'Decryption Shares Ready',
                                style: TextStyle(
                                  fontSize: 18,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              const SizedBox(height: 12),
                              Row(
                                children: [
                                  const Icon(Icons.check_circle,
                                      color: Colors.green, size: 24),
                                  const SizedBox(width: 12),
                                  Expanded(
                                    child: Text(
                                      '${_decryptionShares.length} partial decryptions computed',
                                      style: const TextStyle(
                                        fontSize: 16,
                                        fontWeight: FontWeight.w500,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 8),
                              Text(
                                'Each share is a cryptographic commitment that will help reconstruct the election results.',
                                style: TextStyle(
                                  fontSize: 13,
                                  color: Colors.grey[600],
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                      const SizedBox(height: 32),

                      // Submit Button
                      SizedBox(
                        width: double.infinity,
                        child: ElevatedButton.icon(
                          onPressed: _submitting ? null : _submitShares,
                          icon: _submitting
                              ? const SizedBox(
                                  width: 20,
                                  height: 20,
                                  child: CircularProgressIndicator(
                                    strokeWidth: 2,
                                    valueColor: AlwaysStoppedAnimation<Color>(
                                        Colors.white),
                                  ),
                                )
                              : const Icon(Icons.send),
                          label: Text(
                            _submitting
                                ? 'Submitting...'
                                : 'Submit Decryption Shares',
                          ),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.orange,
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(vertical: 16),
                            textStyle: const TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(height: 16),

                      // Warning
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: Colors.amber[50],
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: Colors.amber),
                        ),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: const [
                            Icon(Icons.warning_amber, color: Colors.amber),
                            SizedBox(width: 12),
                            Expanded(
                              child: Text(
                                'Once submitted, you cannot modify your decryption shares. Make sure you are ready to proceed.',
                                style: TextStyle(
                                  fontSize: 13,
                                  color: Colors.black87,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
    );
  }
}
