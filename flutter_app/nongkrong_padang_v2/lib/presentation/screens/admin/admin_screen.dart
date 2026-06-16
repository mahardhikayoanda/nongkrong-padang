import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/app_theme.dart';
import '../../../core/utils/storage_helper.dart';

class AdminScreen extends StatelessWidget {
  const AdminScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Admin Panel'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () async {
              await StorageHelper.clearAll();
              if (context.mounted) context.go('/');
            },
          ),
        ],
      ),
      body: const Padding(
        padding: EdgeInsets.all(20),
        child: Column(
          children: [
            Card(
              child: ListTile(
                leading: Icon(Icons.monitor, color: AppColors.primary),
                title: Text('Monitoring Pipeline'),
                subtitle: Text('Status DAG Airflow'),
                trailing: Icon(Icons.chevron_right),
              ),
            ),
            SizedBox(height: 8),
            Card(
              child: ListTile(
                leading: Icon(Icons.bar_chart, color: AppColors.primary),
                title: Text('Statistik Performa'),
                subtitle: Text('Metrik ABSA & Rekomendasi'),
                trailing: Icon(Icons.chevron_right),
              ),
            ),
          ],
        ),
      ),
    );
  }
}