import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/app_theme.dart';
import '../../../core/network/dio_client.dart';

class SearchScreen extends StatefulWidget {
  const SearchScreen({super.key});
  @override
  State<SearchScreen> createState() => _SearchScreenState();
}

class _SearchScreenState extends State<SearchScreen> {
  List _hasil = [];
  bool _isLoading = false;
  String _waktu = 'siang', _tujuan = 'kerja', _rombongan = 'berdua';

  Future<void> _cari() async {
    setState(() => _isLoading = true);
    try {
      final r = await DioClient.instance.post('/rekomendasi/', data: {
        'waktu': _waktu,
        'tujuan': _tujuan,
        'rombongan': _rombongan,
        'top_k': 20,
      });
      setState(() => _hasil = r.data['rekomendasi'] ?? []);
    } catch (e) {
      debugPrint('Error: $e');
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Cari Tempat')),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: ElevatedButton(
              onPressed: _cari,
              child: const Text('Cari Rekomendasi'),
            ),
          ),
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : ListView.builder(
                    itemCount: _hasil.length,
                    itemBuilder: (_, i) {
                      final t = _hasil[i];
                      return ListTile(
                        leading:
                            const Icon(Icons.coffee, color: AppColors.primary),
                        title: Text(t['nama_tempat'] ?? ''),
                        subtitle: Text(t['alamat'] ?? ''),
                        onTap: () => context.push('/detail/${t['id_tempat']}'),
                      );
                    },
                  ),
          ),
        ],
      ),
    );
  }
}
