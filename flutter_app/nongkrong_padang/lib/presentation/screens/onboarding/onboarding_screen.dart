import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/app_theme.dart';

class OnboardingScreen extends StatefulWidget {
  const OnboardingScreen({super.key});

  @override
  State<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends State<OnboardingScreen> {
  String _waktu      = 'siang';
  String _tujuan     = 'hangout';
  String _rombongan  = 'berdua';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              const SizedBox(height: 32),

              // Logo
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: AppColors.primary,
                  borderRadius: BorderRadius.circular(20),
                ),
                child: const Icon(Icons.coffee, color: Colors.white, size: 40),
              ),
              const SizedBox(height: 24),

              const Text(
                'Nongkrong Padang',
                style: TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                  color: AppColors.primary,
                ),
              ),
              const SizedBox(height: 8),
              const Text(
                'Cari Tempat Nongkrong Terbaik di Padang',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                  color: AppColors.textPrimary,
                ),
              ),
              const SizedBox(height: 8),
              const Text(
                'Rekomendasi cerdas berbasis analisis sentimen ulasan Google Maps.',
                textAlign: TextAlign.center,
                style: TextStyle(color: AppColors.textSecondary),
              ),
              const SizedBox(height: 40),

              // ── Waktu Kunjungan ──────────────────────
              _buildSectionTitle(Icons.access_time, 'Waktu Kunjungan'),
              const SizedBox(height: 12),
              _buildChipGroup(
                options: ['pagi', 'siang', 'sore', 'malam'],
                selected: _waktu,
                onSelect: (v) => setState(() => _waktu = v),
              ),
              const SizedBox(height: 24),

              // ── Tujuan Kunjungan ─────────────────────
              _buildSectionTitle(Icons.place, 'Tujuan Kunjungan'),
              const SizedBox(height: 12),
              _buildChipGroup(
                options: ['kerja', 'hangout', 'kencan', 'meeting'],
                labels:  ['Nugas / Kerja', 'Nongkrong Santai', 'Kencan', 'Meeting'],
                selected: _tujuan,
                onSelect: (v) => setState(() => _tujuan = v),
              ),
              const SizedBox(height: 24),

              // ── Ukuran Rombongan ─────────────────────
              _buildSectionTitle(Icons.group, 'Ukuran Rombongan'),
              const SizedBox(height: 12),
              _buildChipGroup(
                options: ['sendiri', 'berdua', 'kecil', 'besar'],
                labels:  ['Sendiri', 'Berdua', '3 - 4 Orang', '> 4 Orang'],
                selected: _rombongan,
                onSelect: (v) => setState(() => _rombongan = v),
              ),
              const SizedBox(height: 40),

              // ── Tombol CTA ───────────────────────────
              ElevatedButton.icon(
                onPressed: () {
                  // Simpan konteks default lalu ke home
                  context.go('/home', extra: {
                    'waktu':     _waktu,
                    'tujuan':    _tujuan,
                    'rombongan': _rombongan,
                  });
                },
                icon: const Icon(Icons.arrow_forward),
                label: const Text(
                  'Mulai Cari Rekomendasi',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
              ),
              const SizedBox(height: 16),

              // Link ke Login
              TextButton(
                onPressed: () => context.go('/login'),
                child: const Text(
                  'Sudah punya akun? Masuk di sini',
                  style: TextStyle(color: AppColors.primary),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSectionTitle(IconData icon, String title) => Row(
    children: [
      Icon(icon, color: AppColors.primary, size: 20),
      const SizedBox(width: 8),
      Text(
        title,
        style: const TextStyle(
          fontWeight: FontWeight.w600,
          fontSize: 15,
          color: AppColors.textPrimary,
        ),
      ),
    ],
  );

  Widget _buildChipGroup({
    required List<String> options,
    List<String>? labels,
    required String selected,
    required Function(String) onSelect,
  }) => Wrap(
    spacing: 8,
    runSpacing: 8,
    children: List.generate(options.length, (i) {
      final val   = options[i];
      final label = labels?[i] ?? val[0].toUpperCase() + val.substring(1);
      final isSelected = selected == val;

      return GestureDetector(
        onTap: () => onSelect(val),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          decoration: BoxDecoration(
            color: isSelected ? AppColors.primary : Colors.transparent,
            border: Border.all(
              color: isSelected ? AppColors.primary : Colors.grey[300]!,
            ),
            borderRadius: BorderRadius.circular(20),
          ),
          child: Text(
            label,
            style: TextStyle(
              color: isSelected ? Colors.white : AppColors.textSecondary,
              fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
              fontSize: 13,
            ),
          ),
        ),
      );
    }),
  );
}