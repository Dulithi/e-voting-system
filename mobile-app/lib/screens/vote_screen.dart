import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/election_provider.dart';

class VoteScreen extends StatefulWidget {
  const VoteScreen({super.key});

  @override
  State<VoteScreen> createState() => _VoteScreenState();
}

class _VoteScreenState extends State<VoteScreen> {
  String? _selectedCandidateId; // Changed from int? to String?
  bool _isSubmitting = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final electionId = ModalRoute.of(context)?.settings.arguments as String?;
      if (electionId != null) {
        Provider.of<ElectionProvider>(context, listen: false)
            .fetchElection(electionId);
      }
    });
  }

  Future<void> _submitVote() async {
    if (_selectedCandidateId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please select a candidate'),
          backgroundColor: Colors.orange,
        ),
      );
      return;
    }

    // Show confirmation dialog
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Confirm Your Vote'),
        content: const Text(
          'Are you sure you want to submit this vote? This action cannot be undone.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Confirm'),
          ),
        ],
      ),
    );

    if (confirmed != true) return;

    setState(() {
      _isSubmitting = true;
    });

    final electionProvider =
        Provider.of<ElectionProvider>(context, listen: false);
    final electionId = electionProvider.currentElection!['election_id'];

    final result = await electionProvider.submitVote(
      electionId: electionId,
      candidateId: _selectedCandidateId!,
    );

    setState(() {
      _isSubmitting = false;
    });

    if (mounted) {
      if (result['success']) {
        // Navigate to receipt screen
        Navigator.pushReplacementNamed(
          context,
          '/receipt',
          arguments: electionId,
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(result['error'] ?? 'Failed to submit vote'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Cast Your Vote'),
      ),
      body: Consumer<ElectionProvider>(
        builder: (context, electionProvider, _) {
          if (electionProvider.isLoading) {
            return const Center(child: CircularProgressIndicator());
          }

          final election = electionProvider.currentElection;
          if (election == null) {
            return const Center(child: Text('Election not found'));
          }

          final candidates = election['candidates'] as List<dynamic>? ?? [];

          return Column(
            children: [
              // Election Info
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(16),
                color: Theme.of(context).primaryColor.withOpacity(0.1),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      election['title'] ?? 'Election',
                      style: const TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    if (election['description'] != null) ...[
                      const SizedBox(height: 8),
                      Text(
                        election['description'],
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.grey[700],
                        ),
                      ),
                    ],
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        Icon(Icons.security, size: 16, color: Colors.green),
                        const SizedBox(width: 4),
                        Text(
                          'Encrypted & Anonymous',
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.grey[700],
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),

              // Candidates List
              Expanded(
                child: candidates.isEmpty
                    ? const Center(child: Text('No candidates available'))
                    : ListView.builder(
                        padding: const EdgeInsets.all(16),
                        itemCount: candidates.length,
                        itemBuilder: (context, index) {
                          final candidate = candidates[index];
                          final candidateId = candidate['candidate_id'];
                          final isSelected =
                              _selectedCandidateId == candidateId;

                          return Card(
                            margin: const EdgeInsets.only(bottom: 12),
                            elevation: isSelected ? 4 : 1,
                            color: isSelected
                                ? Theme.of(context)
                                    .primaryColor
                                    .withOpacity(0.1)
                                : null,
                            child: RadioListTile<String>(
                              // Changed from int to String
                              value: candidateId
                                  .toString(), // Ensure it's a String
                              groupValue: _selectedCandidateId,
                              onChanged: _isSubmitting
                                  ? null
                                  : (value) {
                                      setState(() {
                                        _selectedCandidateId = value;
                                      });
                                    },
                              title: Text(
                                candidate['name'] ?? 'Candidate',
                                style: TextStyle(
                                  fontWeight: isSelected
                                      ? FontWeight.bold
                                      : FontWeight.normal,
                                ),
                              ),
                              subtitle: candidate['party'] != null
                                  ? Text(candidate['party'])
                                  : null,
                              secondary: Container(
                                width: 40,
                                height: 40,
                                decoration: BoxDecoration(
                                  color: isSelected
                                      ? Theme.of(context).primaryColor
                                      : Colors.grey[300],
                                  shape: BoxShape.circle,
                                ),
                                child: Center(
                                  child: Text(
                                    '${candidate['display_order'] ?? index + 1}',
                                    style: TextStyle(
                                      color: isSelected
                                          ? Colors.white
                                          : Colors.black87,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ),
                              ),
                            ),
                          );
                        },
                      ),
              ),

              // Submit Button
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white,
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.1),
                      blurRadius: 4,
                      offset: const Offset(0, -2),
                    ),
                  ],
                ),
                child: SafeArea(
                  child: SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: _isSubmitting || _selectedCandidateId == null
                          ? null
                          : _submitVote,
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                      child: _isSubmitting
                          ? const SizedBox(
                              height: 20,
                              width: 20,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                valueColor:
                                    AlwaysStoppedAnimation<Color>(Colors.white),
                              ),
                            )
                          : const Text(
                              'Submit Vote',
                              style: TextStyle(fontSize: 16),
                            ),
                    ),
                  ),
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}
