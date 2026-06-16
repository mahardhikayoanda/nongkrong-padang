import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/app_theme.dart';
import '../../../core/network/dio_client.dart';
import '../../../core/utils/storage_helper.dart';
import '../../../data/models/rekomendasi_model.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  String _waktu     = 'malam';
  String _tujuan    = 'hangout';
  String _rombongan = 'kecil';

  List<RekomendasiItem> _rekomendasi = [];
  bool _isLoading = false;
  String _userName = '';

  @override
  void initState() {
    super.initState();
    _loadUser();
    _fetchRekomendasi();
  }

  Future<void> _loadUser() async {
    final info = await StorageHelper.getUserInfo();
    setState(() => _userName = info['nama'] ?? 'Pengguna');
  }

  Future<void> _fetchRekomendasi() async {
    setState(() => _isLoading = true);
    try {
      final response = await DioClient.instance.post(
        '/rekomendasi/',
        data: {
          'waktu':     _waktu,
          'tujuan':    _tujuan,
          'rombongan': _rombongan,
          'top_k':     10,
        },
      );
      final hasil = RekomendasiResponse.fromJson(response.data);
      setState(() => _rekomendasi = hasil.rekomendasi);
    } catch (e) {
      debugPrint('Error fetch rekomendasi: $e');
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            // ── Header ──────────────────────────────────
            _buildHeader(),

            // ── Chip Konteks ────────────────────────────
            _buildKonteksChips(),

            // ── List Rekomendasi ────────────────────────
            Expanded(
              child: _isLoading
                  ? const Center(child: CircularProgressIndicator())
                  : _rekomendasi.isEmpty
                      ? _buildEmpty()
                      : _buildRekomendasiList(),
            ),
          ],
        ),
      ),
      bottomNavigationBar: _buildBottomNav(),
    );
  }

  Widget _buildHeader() => Container(
    padding: const EdgeInsets.all(20),
    color: AppColors.primary,
    child: Row(
      children: [
        const Icon(Icons.location_on, color: Colors.white, size: 20),
        const SizedBox(width: 8),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Halo, $_userName!',
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const Text(
                'Padang, Sumatera Barat',
                style: TextStyle(color: Colors.white70, fontSize: 12),
              ),
            ],
          ),
        ),
        IconButton(
          icon: const Icon(Icons.search, color: Colors.white),
          onPressed: () => context.go('/search'),
        ),
      ],
    ),
  );

  Widget _buildKonteksChips() => Container(
    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
    color: AppColors.primary.withOpacity(0.05),
    child: Row(
      children: [
        _konteksChip(
          icon: Icons.nightlight,
          label: _waktu[0].toUpperCase() + _waktu.substring(1),
          onTap: _showWaktuPicker,
        ),
        const SizedBox(width: 8),
        _konteksChip(
          icon: Icons.people,
          label: _tujuan[0].toUpperCase() + _tujuan.substring(1),
          onTap: _showTujuanPicker,
        ),
        const SizedBox(width: 8),
        _konteksChip(
          icon: Icons.group,
          label: _rombongan[0].toUpperCase() + _rombongan.substring(1),
          onTap: _showRombonganPicker,
        ),
      ],
    ),
  );

  Widget _konteksChip({
    required IconData icon,
    required String label,
    required VoidCallback onTap,
  }) => GestureDetector(
    onTap: onTap,
    child: Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: AppColors.primary,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, color: Colors.white, size: 14),
          const SizedBox(width: 4),
          Text(
            label,
            style: const TextStyle(color: Colors.white, fontSize: 12),
          ),
        ],
      ),
    ),
  );

  Widget _buildRekomendasiList() => ListView.builder(
    padding: const EdgeInsets.all(16),
    itemCount: _rekomendasi.length,
    itemBuilder: (_, i) => _buildTempatCard(_rekomendasi[i]),
  );

  Widget _buildTempatCard(RekomendasiItem item) => GestureDetector(
    onTap: () => context.go('/detail/${item.idTempat}'),
    child: Card(
      margin: const EdgeInsets.only(bottom: 16),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      elevation: 3,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Foto
          ClipRRect(
            borderRadius: const BorderRadius.vertical(top: Radius.circular(16)),
            child: item.fotoUrl != null
                ? Image.network(
                    item.fotoUrl!,
                    height: 180,
                    width: double.infinity,
                    fit: BoxFit.cover,
                    errorBuilder: (_, __, ___) => _placeholderImage(),
                  )
                : _placeholderImage(),
          ),

          Padding(
            padding: const EdgeInsets.all(14),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Nama & Rating
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        item.namaTempat,
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                    if (item.ratingGoogle != null) ...[
                      const Icon(Icons.star, color: Colors.amber, size: 16),
                      const SizedBox(width: 4),
                      Text(
                        item.ratingGoogle!.toStringAsFixed(1),
                        style: const TextStyle(fontWeight: FontWeight.w600),
                      ),
                    ],
                  ],
                ),
                const SizedBox(height: 4),

                // Alamat
                if (item.alamat != null)
                  Row(
                    children: [
                      const Icon(Icons.location_on,
                          size: 14, color: AppColors.textSecondary),
                      const SizedBox(width: 4),
                      Expanded(
                        child: Text(
                          item.alamat!,
                          style: const TextStyle(
                            color: AppColors.textSecondary,
                            fontSize: 12,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ],
                  ),
                const SizedBox(height: 8),

                // Tag Konteks
                if (item.tagKonteks.isNotEmpty)
                  Wrap(
                    spacing: 6,
                    children: item.tagKonteks.map((tag) => Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(
                        color: AppColors.primary.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Text(
                        tag,
                        style: const TextStyle(
                          color: AppColors.primary,
                          fontSize: 11,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    )).toList(),
                  ),
                const SizedBox(height: 8),

                // Ringkasan Sentimen
                const Text(
                  'Ringkasan Sentimen',
                  style: TextStyle(
                    fontSize: 11,
                    color: AppColors.textSecondary,
                  ),
                ),
                const SizedBox(height: 4),
                Row(
                  children: [
                    _sentimenChip('Suasana',
                        item.profilSentimen.suasanaPos),
                    const SizedBox(width: 6),
                    _sentimenChip('Harga',
                        item.profilSentimen.hargaPos),
                    const SizedBox(width: 6),
                    _sentimenChip('Fasilitas',
                        item.profilSentimen.fasilitasPos),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    ),
  );

  Widget _sentimenChip(String label, double skor) {
    final isPositif = skor > 0.5;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: (isPositif ? AppColors.positif : AppColors.netral)
            .withOpacity(0.15),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(
          color: (isPositif ? AppColors.positif : AppColors.netral)
              .withOpacity(0.4),
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            isPositif ? Icons.thumb_up : Icons.thumbs_up_down,
            size: 10,
            color: isPositif ? AppColors.positif : AppColors.netral,
          ),
          const SizedBox(width: 3),
          Text(
            label,
            style: TextStyle(
              fontSize: 10,
              color: isPositif ? AppColors.positif : AppColors.netral,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  Widget _placeholderImage() => Container(
    height: 180,
    color: Colors.grey[200],
    child: const Center(
      child: Icon(Icons.coffee, size: 48, color: Colors.grey),
    ),
  );

  Widget _buildEmpty() => Center(
    child: Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        const Icon(Icons.search_off, size: 64, color: Colors.grey),
        const SizedBox(height: 16),
        const Text('Belum ada rekomendasi tersedia'),
        const SizedBox(height: 8),
        ElevatedButton(
          onPressed: _fetchRekomendasi,
          child: const Text('Coba Lagi'),
        ),
      ],
    ),
  );

  Widget _buildBottomNav() => BottomNavigationBar(
    currentIndex: 0,
    selectedItemColor: AppColors.primary,
    unselectedItemColor: Colors.grey,
    type: BottomNavigationBarType.fixed,
    onTap: (i) {
      switch (i) {
        case 0: break;
        case 1: context.go('/search'); break;
        case 2: context.go('/favorites'); break;
        case 3: context.go('/profile'); break;
      }
    },
    items: const [
      BottomNavigationBarItem(icon: Icon(Icons.home), label: 'Home'),
      BottomNavigationBarItem(icon: Icon(Icons.search), label: 'Cari'),
      BottomNavigationBarItem(icon: Icon(Icons.favorite), label: 'Favorit'),
      BottomNavigationBarItem(icon: Icon(Icons.person), label: 'Profil'),
    ],
  );

  void _showWaktuPicker() => _showPicker(
    title: 'Waktu Kunjungan',
    options: ['pagi', 'siang', 'sore', 'malam'],
    selected: _waktu,
    onSelect: (v) { setState(() => _waktu = v); _fetchRekomendasi(); },
  );

  void _showTujuanPicker() => _showPicker(
    title: 'Tujuan Kunjungan',
    options: ['kerja', 'hangout', 'kencan', 'meeting'],
    selected: _tujuan,
    onSelect: (v) { setState(() => _tujuan = v); _fetchRekomendasi(); },
  );

  void _showRombonganPicker() => _showPicker(
    title: 'Ukuran Rombongan',
    options: ['sendiri', 'berdua', 'kecil', 'besar'],
    selected: _rombongan,
    onSelect: (v) { setState(() => _rombongan = v); _fetchRekomendasi(); },
  );

  void _showPicker({
    required String title,
    required List<String> options,
    required String selected,
    required Function(String) onSelect,
  }) {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (_) => Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title,
                style: const TextStyle(
                    fontSize: 16, fontWeight: FontWeight.bold)),
            const SizedBox(height: 16),
            Wrap(
              spacing: 8,
              children: options.map((opt) => ChoiceChip(
                label: Text(opt[0].toUpperCase() + opt.substring(1)),
                selected: selected == opt,
                selectedColor: AppColors.primary,
                labelStyle: TextStyle(
                  color: selected == opt ? Colors.white : Colors.black,
                ),
                onSelected: (_) {
                  onSelect(opt);
                  Navigator.pop(context);
                },
              )).toList(),
            ),
          ],
        ),
      ),
    );
  }
}