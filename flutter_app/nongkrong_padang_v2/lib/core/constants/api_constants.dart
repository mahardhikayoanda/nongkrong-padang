class ApiConstants {
  // Ganti dengan IP komputer kamu jika test di HP fisik
  // Untuk emulator Android: 10.0.2.2
  // Untuk HP fisik: IP WiFi komputer kamu (cek dengan ipconfig)
  static const baseUrl = 'http://10.0.2.2:8000/api/v1';

  // Auth
  static const register = '/auth/register';
  static const login = '/auth/login';

  // Tempat
  static const tempat = '/tempat/';
  static const tempatDetail = '/tempat/{id}/detail';

  // Rekomendasi
  static const rekomendasi = '/rekomendasi/';

  // Profil
  static const profil = '/profil/me';
  static const updateProfil = '/profil/update';
}
