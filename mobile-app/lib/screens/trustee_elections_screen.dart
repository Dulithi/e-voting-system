import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../services/trustee_service.dart';
import 'trustee_decrypt_screen.dart';

class TrusteeElectionsScreen extends StatefulWidget {
  const TrusteeElectionsScreen({super.key});

  @override
  State<TrusteeElectionsScreen> createState() => _TrusteeElectionsScreenState();
}

class _TrusteeElectionsScreenState extends State<TrusteeElectionsScreen> {
  final TrusteeService _trusteeService = TrusteeService();
  List<Map<String, dynamic>> _elections = [];
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadElections();
  }

  Future<void> _loadElections() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final elections = await _trusteeService.getMyElections();
      setState(() {
        _elections = elections;
        _loading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _loading = false;
      });
    }
  }

  Color _getStatusColor(String status) {
    switch (status.toUpperCase()) {
      case 'ACTIVE':
        return Colors.green;
      case 'CLOSED':
        return Colors.orange;
      case 'TALLIED':
        return Colors.blue;
      case 'DRAFT':
      default:
        return Colors.grey;
    }
  }

  IconData _getStatusIcon(String status) {
    switch (status.toUpperCase()) {
      case 'ACTIVE':
        return Icons.how_to_vote;
      case 'CLOSED':
        return Icons.lock_clock;
      case 'TALLIED':
        return Icons.bar_chart;
      case 'DRAFT':
      default:
        return Icons.edit;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Trustee Elections'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadElections,
            tooltip: 'Refresh',
          ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(Icons.error_outline,
                            size: 64, color: Colors.red),
                        const SizedBox(height: 16),
                        Text(
                          'Error loading elections',
                          style: Theme.of(context).textTheme.headlineSmall,
                        ),
                        const SizedBox(height: 8),
                        Text(_error!,
                            textAlign: TextAlign.center,
                            style: const TextStyle(color: Colors.red)),
                        const SizedBox(height: 16),
                        ElevatedButton.icon(
                          onPressed: _loadElections,
                          icon: const Icon(Icons.refresh),
                          label: const Text('Retry'),
                        ),
                      ],
                    ),
                  ),
                )
              : _elections.isEmpty
                  ? Center(
                      child: Padding(
                        padding: const EdgeInsets.all(32.0),
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(Icons.verified_user,
                                size: 80, color: Colors.grey[400]),
                            const SizedBox(height: 24),
                            Text(
                              'No Trustee Elections',
                              style: Theme.of(context)
                                  .textTheme
                                  .headlineSmall
                                  ?.copyWith(color: Colors.grey[600]),
                            ),
                            const SizedBox(height: 12),
                            Text(
                              'You are not assigned as a trustee for any elections yet.',
                              textAlign: TextAlign.center,
                              style: TextStyle(
                                  fontSize: 16, color: Colors.grey[600]),
                            ),
                          ],
                        ),
                      ),
                    )
                  : RefreshIndicator(
                      onRefresh: _loadElections,
                      child: ListView.builder(
                        padding: const EdgeInsets.all(16),
                        itemCount: _elections.length,
                        itemBuilder: (context, index) {
                          final election = _elections[index];
                          return _buildElectionCard(election);
                        },
                      ),
                    ),
    );
  }

  Widget _buildElectionCard(Map<String, dynamic> election) {
    final String status = election['election_status'];
    final bool hasKeyShare = election['has_key_share'] ?? false;
    final bool sharesSubmitted = election['shares_submitted'] ?? false;
    final int threshold = election['threshold'] ?? 0;
    final int trusteesSubmitted = election['trustees_submitted'] ?? 0;

    final bool canSubmitShares =
        status.toUpperCase() == 'CLOSED' && hasKeyShare && !sharesSubmitted;

    return Card(
      elevation: 3,
      margin: const EdgeInsets.only(bottom: 16),
      child: InkWell(
        onTap: canSubmitShares ? () => _navigateToDecrypt(election) : null,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Title and Status
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(
                    child: Text(
                      election['election_title'],
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Chip(
                    avatar: Icon(
                      _getStatusIcon(status),
                      size: 18,
                      color: Colors.white,
                    ),
                    label: Text(
                      status.toUpperCase(),
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    backgroundColor: _getStatusColor(status),
                    padding: const EdgeInsets.symmetric(horizontal: 8),
                  ),
                ],
              ),
              const SizedBox(height: 12),

              // Dates
              Row(
                children: [
                  const Icon(Icons.calendar_today,
                      size: 16, color: Colors.grey),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      '${_formatDate(election['start_time'])} - ${_formatDate(election['end_time'])}',
                      style: const TextStyle(fontSize: 13, color: Colors.grey),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),

              // Trustee Status
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.grey[100],
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(
                          hasKeyShare ? Icons.vpn_key : Icons.key_off,
                          size: 20,
                          color: hasKeyShare ? Colors.green : Colors.grey,
                        ),
                        const SizedBox(width: 8),
                        Text(
                          hasKeyShare
                              ? 'Key Share: Received'
                              : 'Key Share: Pending',
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            color: hasKeyShare ? Colors.green : Colors.grey,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        Icon(
                          sharesSubmitted ? Icons.check_circle : Icons.pending,
                          size: 20,
                          color: sharesSubmitted ? Colors.blue : Colors.orange,
                        ),
                        const SizedBox(width: 8),
                        Text(
                          sharesSubmitted
                              ? 'Decryption Share: Submitted'
                              : 'Decryption Share: Not Submitted',
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            color:
                                sharesSubmitted ? Colors.blue : Colors.orange,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        const Icon(Icons.people,
                            size: 20, color: Colors.purple),
                        const SizedBox(width: 8),
                        Text(
                          'Shares Submitted: $trusteesSubmitted / $threshold required',
                          style: const TextStyle(
                            fontSize: 13,
                            color: Colors.purple,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),

              // Action Button
              if (canSubmitShares) ...[
                const SizedBox(height: 16),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    onPressed: () => _navigateToDecrypt(election),
                    icon: const Icon(Icons.lock_open),
                    label: const Text('Submit Decryption Share'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.orange,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 12),
                    ),
                  ),
                ),
              ] else if (status.toUpperCase() == 'ACTIVE') ...[
                const SizedBox(height: 12),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.blue[50],
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.blue[200]!),
                  ),
                  child: Row(
                    children: const [
                      Icon(Icons.info_outline, size: 20, color: Colors.blue),
                      SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          'Election is active. Wait until it closes to submit decryption share.',
                          style: TextStyle(fontSize: 13, color: Colors.blue),
                        ),
                      ),
                    ],
                  ),
                ),
              ] else if (sharesSubmitted) ...[
                const SizedBox(height: 12),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.green[50],
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.green[200]!),
                  ),
                  child: Row(
                    children: const [
                      Icon(Icons.check_circle, size: 20, color: Colors.green),
                      SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          '✅ You have already submitted your decryption share.',
                          style: TextStyle(fontSize: 13, color: Colors.green),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  String _formatDate(String dateStr) {
    try {
      final date = DateTime.parse(dateStr);
      return DateFormat('MMM d, yyyy').format(date);
    } catch (e) {
      return dateStr;
    }
  }

  void _navigateToDecrypt(Map<String, dynamic> election) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => TrusteeDecryptScreen(election: election),
      ),
    ).then((_) => _loadElections()); // Refresh when returning
  }
}
