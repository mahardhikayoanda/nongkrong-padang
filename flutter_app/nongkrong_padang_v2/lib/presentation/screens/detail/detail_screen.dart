import 'package:flutter/material.dart';
import '../../../core/theme/app_theme.dart';
import '../../../core/network/dio_client.dart';
import '../../../data/models/tempat_model.dart';

class DetailScreen extends StatefulWidget {
  final String idTempat;
  const DetailScreen({super.key, required this.idTempat});

  @override
  State<DetailScreen> createState() => _DetailScreenState();
}

class _DetailScreenState extends State<DetailScreen> {
  TempatModel? _tempat;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _fetchDetail();
  }

  Future<void> _fetchDetail() async {
    try {
      final response = await DioClient.instance.get(
        '/tempat/${widget.idTempat}/detail',
      );
      setState(() => _tempat = TempatModel.fromJson(response.data));
    } catch (e) {
      debugPrint('Error fetch detail: $e');
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _tempat == null
              ? const Center(child: Text('Tempat tidak ditemukan'))
              : _buildDetail(),
    );
  }

  Widget _buildDetail() {
    final t = _tempat!;
    final s = t.profilSentimen;

    return CustomScrollView(
      slivers: [
        // App Bar dengan foto
        SliverAppBar(
          expandedHeight: 250,
          pinned: true,
          backgroundColor: AppColors.primary,
          flexibleSpace: FlexibleSpaceBar(
            title: Text(t.namaTempat,
                style: const TextStyle(fontSize: 14)),
            background: t.fotoUrl != null
                ? Image.network(t.fotoUrl!, fit: BoxFit.cover,
                    errorBuilder: (_, __, ___) => Container(
                      color: AppColors.primary.withOpacity(0.3),
                      child: const Icon(Icons.coffee,
                          size: 64, color: Colors.white),
                    ))
                : Container(
                    color: AppColors.primary.withOpacity(0.3),
                    child: const Icon(Icons.coffee,
                        size: 64, color: Colors.white),
                  ),
          ),
        ),

        SliverToBoxAdapter(
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Info dasar
                Row(
                  children: [
                    const Icon(Icons.star, color: Colors.amber, size: 20),
                    const SizedBox(width: 4),
                    Text(
                      t.ratingGoogle?.toStringAsFixed(1) ?? '-',
                      style: const TextStyle(
                          fontSize: 18, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(width: 8),
                    Text('(${t.totalUlasan} ulasan)',
                        style: const TextStyle(color: AppColors.textSecondary)),
                  ],
                ),
                const SizedBox(height: 8),
                if (t.alamat != null)
                  Row(
                    children: [
                      const Icon(Icons.location_on,
                          color: AppColors.textSecondary, size: 16),
                      const SizedBox(width: 4),
                      Expanded(
                          child: Text(t.alamat!,
                              style: const TextStyle(
                                  color: AppColors.textSecondary))),
                    ],
                  ),
                const SizedBox(height: 24),

                // Profil Sentimen
                const Text('Profil Sentimen',
                    style: TextStyle(
                        fontSize: 16, fontWeight: FontWeight.bold)),
                const SizedBox(height: 4),
                Text(
                  'Berdasarkan analisis ${t.totalUlasan} ulasan menggunakan IndoBERT ABSA.',
                  style: const TextStyle(
                      color: AppColors.textSecondary, fontSize: 12),
                ),
                const SizedBox(height: 16),

                // Radar Chart sederhana (bar chart per aspek)
                if (s != null) _buildSentimenBars(s),
                const SizedBox(height: 24),

                // Tombol Google Maps
                ElevatedButton.icon(
                  onPressed: () {},
                  icon: const Icon(Icons.directions),
                  label: const Text('Arahkan dengan Google Maps'),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildSentimenBars(SentimenAspek s) {
    final aspek = [
      {'label': 'Suasana',   'pos': s.suasanaPos,   'neg': s.suasanaNeg},
      {'label': 'Harga',     'pos': s.hargaPos,     'neg': s.hargaNeg},
      {'label': 'Lokasi',    'pos': s.lokasiPos,    'neg': s.lokasiNeg},
      {'label': 'Pelayanan', 'pos': s.pelayananPos, 'neg': s.pelayananNeg},
      {'label': 'Fasilitas', 'pos': s.fasilitasPos, 'neg': s.fasilitasNeg},
    ];

    return Column(
      children: aspek.map((a) {
        final pos = (a['pos'] as double) * 100;
        final label = a['label'] as String;
        return Padding(
          padding: const EdgeInsets.only(bottom: 12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(label,
                      style: const TextStyle(fontWeight: FontWeight.w500)),
                  Text('${pos.toStringAsFixed(0)}% positif',
                      style: const TextStyle(
                          color: AppColors.positif, fontSize: 12)),
                ],
              ),
              const SizedBox(height: 4),
              ClipRRect(
                borderRadius: BorderRadius.circular(4),
                child: LinearProgressIndicator(
                  value: pos / 100,
                  minHeight: 8,
                  backgroundColor: Colors.grey[200],
                  valueColor: const AlwaysStoppedAnimation(AppColors.positif),
                ),
              ),
            ],
          ),
        );
      }).toList(),
    );
  }
}