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

  @override
  void initState() {
    super.initState();
    _fetchDags();
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
            onPressed: _fetchDags,
            tooltip: 'Refresh Status Pipeline',
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
        onRefresh: _fetchDags,
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Card(
                child: ListTile(
                  leading:
                      const Icon(Icons.bar_chart, color: AppColors.primary),
                  title: const Text('Statistik Performa'),
                  subtitle: const Text('Metrik ABSA & Rekomendasi'),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: () {
                    // Fitur statistik bisa ditambahkan di sini nanti
                  },
                ),
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
                          color: dag['is_active'] ? Colors.green : Colors.grey,
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
}
