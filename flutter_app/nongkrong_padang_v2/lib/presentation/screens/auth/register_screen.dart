import 'package:flutter/material.dart';
import 'package:dio/dio.dart';
import 'package:go_router/go_router.dart';
import '../../../core/network/dio_client.dart';
import '../../../core/theme/app_theme.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _namaCtrl = TextEditingController();
  final _emailCtrl = TextEditingController();
  final _passwordCtrl = TextEditingController();
  bool _isLoading = false;
  bool _obscurePass = true;

  String? _jenisKelamin;

  Future<void> _register() async {
    debugPrint('Mencoba registrasi dengan data:');
    debugPrint('Nama: ${_namaCtrl.text}');
    debugPrint('Email: ${_emailCtrl.text}');
    debugPrint('JK: $_jenisKelamin');

    if (_namaCtrl.text.isEmpty ||
        _emailCtrl.text.isEmpty ||
        _passwordCtrl.text.isEmpty ||
        _jenisKelamin == null) {
      debugPrint('Validasi gagal: Ada kolom kosong.');
      _showSnack('Semua kolom harus diisi');
      return;
    }

    setState(() => _isLoading = true);
    debugPrint('Status Loading: true');

    try {
      debugPrint('Mengirim request ke /auth/register...');
      final response = await DioClient.instance.post(
        '/auth/register',
        data: {
          'nama': _namaCtrl.text.trim(),
          'email': _emailCtrl.text.trim(),
          'password': _passwordCtrl.text,
          'jenis_kelamin': _jenisKelamin,
        },
      );

      debugPrint('Response terima: ${response.statusCode}');
      debugPrint('Data: ${response.data}');

      if (mounted) {
        _showSnack('Registrasi berhasil! Silakan login.');
        context.go('/login');
      }
    } on DioException catch (e) {
      debugPrint('Dio Error: ${e.type}');
      debugPrint('Dio Message: ${e.message}');

      final data = e.response?.data;
      String? detail;
      if (data is Map) {
        detail = data['detail'];
      } else if (data is String) {
        detail = data;
      }

      final status = e.response?.statusCode;
      final msg = "Registrasi Gagal ($status): ${detail ?? e.message}";
      _showSnack(msg);
    } catch (e) {
      debugPrint('General Error: $e');
      _showSnack('Terjadi kesalahan sistem: $e');
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
        debugPrint('Status Loading: false');
      }
    }
  }

  void _showSnack(String msg) {
    debugPrint('Menampilkan SnackBar: $msg');
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(msg)));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Card(
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(24),
            ),
            elevation: 4,
            child: Padding(
              padding: const EdgeInsets.all(28),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Text(
                    'Daftar Akun',
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: AppColors.primary,
                    ),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'Buat akun untuk mendapatkan rekomendasi personal.',
                    textAlign: TextAlign.center,
                    style: TextStyle(color: AppColors.textSecondary),
                  ),
                  const SizedBox(height: 28),
                  TextField(
                    controller: _namaCtrl,
                    decoration: const InputDecoration(
                      labelText: 'Nama Lengkap',
                      prefixIcon: Icon(Icons.person_outline),
                    ),
                  ),
                  const SizedBox(height: 16),
                  DropdownButtonFormField<String>(
                    value: _jenisKelamin,
                    decoration: const InputDecoration(
                      labelText: 'Jenis Kelamin',
                      prefixIcon: Icon(Icons.wc),
                    ),
                    items: const [
                      DropdownMenuItem(
                          value: 'Laki-laki', child: Text('Laki-laki')),
                      DropdownMenuItem(
                          value: 'Perempuan', child: Text('Perempuan')),
                    ],
                    onChanged: (v) => setState(() => _jenisKelamin = v),
                  ),
                  const SizedBox(height: 16),
                  TextField(
                    controller: _emailCtrl,
                    keyboardType: TextInputType.emailAddress,
                    decoration: const InputDecoration(
                      labelText: 'Email',
                      prefixIcon: Icon(Icons.email_outlined),
                    ),
                  ),
                  const SizedBox(height: 16),
                  TextField(
                    controller: _passwordCtrl,
                    obscureText: _obscurePass,
                    decoration: InputDecoration(
                      labelText: 'Password',
                      prefixIcon: const Icon(Icons.lock_outline),
                      suffixIcon: IconButton(
                        icon: Icon(_obscurePass
                            ? Icons.visibility_off
                            : Icons.visibility),
                        onPressed: () =>
                            setState(() => _obscurePass = !_obscurePass),
                      ),
                    ),
                  ),
                  const SizedBox(height: 28),
                  _isLoading
                      ? const CircularProgressIndicator()
                      : ElevatedButton(
                          onPressed: _register,
                          child: const Text('Daftar Sekarang'),
                        ),
                  const SizedBox(height: 16),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Text('Sudah punya akun? '),
                      TextButton(
                        onPressed: () => context.go('/login'),
                        child: const Text(
                          'Masuk',
                          style: TextStyle(
                            color: AppColors.primary,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
