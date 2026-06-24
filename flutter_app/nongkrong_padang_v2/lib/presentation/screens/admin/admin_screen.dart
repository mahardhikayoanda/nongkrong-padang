import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/app_theme.dart';
import '../../../core/utils/storage_helper.dart';
import '../../../core/network/dio_client.dart';

class AdminScreen extends StatefulWidget {
  const AdminScreen({super.key});

  @override
  State<AdminScreen> createState() => _AdminScreenState();
}

class _AdminScreenState extends State<AdminScreen> {
  bool isLoading = false;
  List<dynamic> dags = [];
  Map<String, dynamic>? absaStats;
  Map<String, dynamic>? recStats;

  @override
  void initState() {
    super.initState();
    _refreshAll();
  }

  Future<void> _refreshAll() async {
    await Future.wait([
      _fetchDags(),
      _fetchStats(),
    ]);
  }

  Future<void> _fetchStats() async {
    try {
      final info = await StorageHelper.getUserInfo();
      final userId = info['id_user'];

      final absaResponse = await DioClient.instance.get('/admin/stats/absa');
      final recResponse = await DioClient.instance
          .get('/admin/stats/recommendation?user_id=$userId');

      setState(() {
        absaStats = absaResponse.data;
        recStats = recResponse.data;
      });
    } catch (e) {
      debugPrint('Error fetch stats: $e');
    }
  }

  Future<void> _fetchDags() async {
    setState(() => isLoading = true);
    try {
      final response = await DioClient.instance.get('/admin/airflow/dags');
      setState(() {
        dags = response.data;
      });
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Gagal memuat pipeline: $e')),
        );
      }
    } finally {
      if (mounted) setState(() => isLoading = false);
    }
  }

  Future<void> _triggerDag(String dagId) async {
    try {
      await DioClient.instance.post('/admin/airflow/dags/$dagId/trigger');

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Berhasil memicu pipeline: $dagId')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Gagal memicu pipeline: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Admin Panel'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () {
            if (context.canPop()) {
              context.pop();
            } else {
              context.go('/home');
            }
          },
        ),
        actions: [
          TextButton.icon(
            onPressed: () => context.go('/home'),
            icon: const Icon(Icons.person, color: Colors.white, size: 18),
            label: const Text('Mode User',
                style: TextStyle(color: Colors.white, fontSize: 12)),
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _refreshAll,
            tooltip: 'Refresh Semua Data',
          ),
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () async {
              await StorageHelper.clearAll();
              if (context.mounted) context.go('/');
            },
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _refreshAll,
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Statistik Performa Sistem',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: _buildMetricCard(
                      'ABSA F1-Score',
                      '${((absaStats?['ate_f1'] ?? 0) * 100).toStringAsFixed(1)}%',
                      Icons.analytics,
                      Colors.blue,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: _buildMetricCard(
                      'NDCG@10',
                      '${(recStats?['ndcg'] ?? 0).toStringAsFixed(3)}',
                      Icons.ads_click,
                      Colors.orange,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              _buildMetricCard(
                'Precision@10 (Recommendation)',
                '${((recStats?['precision'] ?? 0) * 100).toStringAsFixed(1)}%',
                Icons.check_circle,
                Colors.green,
                fullWidth: true,
              ),
              const SizedBox(height: 24),
              const Text(
                'Monitoring Pipeline (Airflow)',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 12),
              if (isLoading)
                const Center(
                    child: Padding(
                  padding: EdgeInsets.all(20.0),
                  child: CircularProgressIndicator(),
                ))
              else if (dags.isEmpty)
                const Center(child: Text('Tidak ada data pipeline.'))
              else
                ListView.builder(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: dags.length,
                  itemBuilder: (context, index) {
                    final dag = dags[index];
                    return Card(
                      margin: const EdgeInsets.only(bottom: 8),
                      child: ListTile(
                        leading: Icon(
                          Icons.account_tree,
                          color: dag['is_active'] != null && dag['is_active']
                              ? Colors.green
                              : Colors.grey,
                        ),
                        title: Text(dag['dag_id'],
                            style: const TextStyle(
                                fontWeight: FontWeight.bold, fontSize: 13)),
                        subtitle: Text(dag['is_active']
                            ? 'Status: Aktif'
                            : 'Status: Non-aktif'),
                        trailing: ElevatedButton(
                          style: ElevatedButton.styleFrom(
                            backgroundColor: AppColors.primary,
                            foregroundColor: Colors.white,
                          ),
                          onPressed: () => _triggerDag(dag['dag_id']),
                          child: const Text('Trigger'),
                        ),
                      ),
                    );
                  },
                ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildMetricCard(
      String title, String value, IconData icon, Color color,
      {bool fullWidth = false}) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment:
              fullWidth ? CrossAxisAlignment.center : CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(icon, color: color, size: 20),
                const SizedBox(width: 8),
                Text(title,
                    style: const TextStyle(
                        fontSize: 12, color: AppColors.textSecondary)),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              value,
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
