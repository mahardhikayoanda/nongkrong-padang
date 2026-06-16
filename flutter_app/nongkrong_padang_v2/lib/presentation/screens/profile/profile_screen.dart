import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/app_theme.dart';
import '../../../core/utils/storage_helper.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});
  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  String _nama = '', _email = '', _role = 'user';

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final info = await StorageHelper.getUserInfo();
    setState(() {
      _nama = info['nama'] ?? '';
      _role = info['role'] ?? 'user';
    });
  }

  Future<void> _logout() async {
    await StorageHelper.clearAll();
    if (mounted) context.go('/');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Profil')),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            const CircleAvatar(
              radius: 48,
              backgroundColor: AppColors.primary,
              child: Icon(Icons.person, size: 48, color: Colors.white),
            ),
            const SizedBox(height: 16),
            Text(_nama,
                style:
                    const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
            const SizedBox(height: 32),
            ListTile(
              leading: const Icon(Icons.history),
              title: const Text('Riwayat Kunjungan'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () {},
            ),
            if (_role == 'admin') ...[
              ListTile(
                leading: const Icon(Icons.admin_panel_settings,
                    color: AppColors.primary),
                title: const Text('Admin Panel'),
                subtitle: const Text('Kelola Pipeline & Data'),
                trailing: const Icon(Icons.chevron_right),
                onTap: () => context.push('/admin'),
              ),
              const Divider(),
            ],
            ListTile(
              leading: const Icon(Icons.settings),
              title: const Text('Pengaturan Akun'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () {},
            ),
            const Divider(),
            ListTile(
              leading: const Icon(Icons.logout, color: Colors.red),
              title: const Text('Logout', style: TextStyle(color: Colors.red)),
              onTap: _logout,
            ),
          ],
        ),
      ),
    );
  }
}
