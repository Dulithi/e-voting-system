import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import '../providers/election_provider.dart';
import '../screens/trustee_elections_screen.dart';
import '../services/trustee_service.dart';
import 'package:intl/intl.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> with WidgetsBindingObserver {
  final TrusteeService _trusteeService = TrusteeService();
  bool _isTrustee = false;
  bool _checkingTrustee = true;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      Provider.of<ElectionProvider>(context, listen: false).fetchElections();
      _checkIfTrustee();
    });
  }

  Future<void> _checkIfTrustee() async {
    try {
      final elections = await _trusteeService.getMyElections();
      if (mounted) {
        setState(() {
          _isTrustee = elections.isNotEmpty;
          _checkingTrustee = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isTrustee = false;
          _checkingTrustee = false;
        });
      }
    }
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    super.didChangeAppLifecycleState(state);

    // Refresh elections when app resumes
    if (state == AppLifecycleState.resumed) {
      print('🔄 [HomeScreen] App resumed, refreshing elections...');
      Provider.of<ElectionProvider>(context, listen: false).fetchElections();
    }
  }

  @override
  Widget build(BuildContext context) {
    final authProvider = Provider.of<AuthProvider>(context);
    final electionProvider = Provider.of<ElectionProvider>(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('E-Vote'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () async {
              await authProvider.logout();
              if (context.mounted) {
                Navigator.pushReplacementNamed(context, '/login');
              }
            },
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () => electionProvider.fetchElections(),
        child: Column(
          children: [
            // User Info Card
            Container(
              margin: const EdgeInsets.all(16),
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Theme.of(context).primaryColor.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Row(
                children: [
                  CircleAvatar(
                    radius: 30,
                    backgroundColor: Theme.of(context).primaryColor,
                    child: Text(
                      authProvider.currentUser?['full_name']?[0] ?? 'U',
                      style: const TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          authProvider.currentUser?['full_name'] ?? 'User',
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          authProvider.currentUser?['email'] ?? '',
                          style: TextStyle(
                            fontSize: 14,
                            color: Colors.grey[600],
                          ),
                        ),
                        const SizedBox(height: 4),
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 8,
                            vertical: 4,
                          ),
                          decoration: BoxDecoration(
                            color: _getKycColor(
                                authProvider.currentUser?['kyc_status']),
                            borderRadius: BorderRadius.circular(4),
                          ),
                          child: Text(
                            'KYC: ${authProvider.currentUser?['kyc_status'] ?? 'UNKNOWN'}',
                            style: const TextStyle(
                              fontSize: 12,
                              color: Colors.white,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),

            // Elections Tab Bar
            _checkingTrustee
                ? const Expanded(
                    child: Center(child: CircularProgressIndicator()),
                  )
                : DefaultTabController(
                    length: _isTrustee ? 3 : 2,
                    child: Expanded(
                      child: Column(
                        children: [
                          TabBar(
                            tabs: [
                              const Tab(text: 'Active Elections'),
                              const Tab(text: 'Past Elections'),
                              if (_isTrustee)
                                const Tab(
                                  icon: Icon(Icons.verified_user, size: 20),
                                  text: 'Trustee',
                                ),
                            ],
                          ),
                          Expanded(
                            child: electionProvider.isLoading
                                ? const Center(
                                    child: CircularProgressIndicator())
                                : TabBarView(
                                    children: [
                                      _buildElectionsList(
                                        electionProvider.getActiveElections(),
                                        'active',
                                      ),
                                      _buildElectionsList(
                                        electionProvider.getPastElections(),
                                        'past',
                                      ),
                                      if (_isTrustee)
                                        const TrusteeElectionsScreen(),
                                    ],
                                  ),
                          ),
                        ],
                      ),
                    ),
                  ),
          ],
        ),
      ),
    );
  }

  Widget _buildElectionsList(
      List<Map<String, dynamic>> elections, String type) {
    if (elections.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.inbox,
              size: 64,
              color: Colors.grey[400],
            ),
            const SizedBox(height: 16),
            Text(
              type == 'active' ? 'No active elections' : 'No past elections',
              style: TextStyle(
                fontSize: 18,
                color: Colors.grey[600],
              ),
            ),
          ],
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: elections.length,
      itemBuilder: (context, index) {
        final election = elections[index];
        return _buildElectionCard(election, type);
      },
    );
  }

  Widget _buildElectionCard(Map<String, dynamic> election, String type) {
    final hasVoted = election['has_voted'] ?? false;

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        onTap: () {
          if (!hasVoted && type == 'active') {
            Navigator.pushNamed(
              context,
              '/vote',
              arguments: election['election_id'],
            );
          } else {
            _showElectionDetails(election);
          }
        },
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Text(
                      election['title'] ?? 'Election',
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  if (hasVoted)
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 8,
                        vertical: 4,
                      ),
                      decoration: BoxDecoration(
                        color: Colors.green,
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: const Text(
                        'VOTED',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                ],
              ),
              if (election['description'] != null) ...[
                const SizedBox(height: 8),
                Text(
                  election['description'],
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey[700],
                  ),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
              const SizedBox(height: 12),
              Row(
                children: [
                  Icon(Icons.calendar_today, size: 16, color: Colors.grey[600]),
                  const SizedBox(width: 4),
                  Text(
                    _formatDate(election['start_time']),
                    style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                  ),
                  const SizedBox(width: 12),
                  Icon(Icons.arrow_forward, size: 16, color: Colors.grey[600]),
                  const SizedBox(width: 4),
                  Text(
                    _formatDate(election['end_time']),
                    style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                  ),
                ],
              ),
              if (!hasVoted && type == 'active') ...[
                const SizedBox(height: 12),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: () {
                      Navigator.pushNamed(
                        context,
                        '/vote',
                        arguments: election['election_id'],
                      );
                    },
                    child: const Text('Cast Your Vote'),
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  void _showElectionDetails(Map<String, dynamic> election) {
    showModalBottomSheet(
      context: context,
      builder: (context) => Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              election['title'] ?? 'Election',
              style: const TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            if (election['description'] != null) Text(election['description']),
            const SizedBox(height: 16),
            Text('Status: ${election['status']}'),
            Text('Start: ${_formatDate(election['start_time'])}'),
            Text('End: ${_formatDate(election['end_time'])}'),
            if (election['has_voted'] ?? false) ...[
              const SizedBox(height: 16),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: () {
                    Navigator.pop(context);
                    Navigator.pushNamed(
                      context,
                      '/receipt',
                      arguments: election['election_id'],
                    );
                  },
                  icon: const Icon(Icons.receipt),
                  label: const Text('View Receipt'),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Color _getKycColor(String? status) {
    switch (status) {
      case 'APPROVED':
        return Colors.green;
      case 'PENDING':
        return Colors.orange;
      case 'REJECTED':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  String _formatDate(dynamic dateStr) {
    try {
      final date = DateTime.parse(dateStr.toString());
      return DateFormat('MMM dd, yyyy HH:mm').format(date);
    } catch (e) {
      return dateStr.toString();
    }
  }
}
