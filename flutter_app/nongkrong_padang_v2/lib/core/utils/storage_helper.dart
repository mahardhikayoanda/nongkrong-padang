import 'package:shared_preferences/shared_preferences.dart';

class StorageHelper {
  static const _keyToken    = 'access_token';
  static const _keyUserId   = 'user_id';
  static const _keyUserName = 'user_name';
  static const _keyUserRole = 'user_role';

  static Future<void> saveToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_keyToken, token);
  }

  static Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_keyToken);
  }

  static Future<void> saveUserInfo({
    required String id,
    required String nama,
    required String role,
  }) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_keyUserId,   id);
    await prefs.setString(_keyUserName, nama);
    await prefs.setString(_keyUserRole, role);
  }

  static Future<Map<String, String?>> getUserInfo() async {
    final prefs = await SharedPreferences.getInstance();
    return {
      'id':   prefs.getString(_keyUserId),
      'nama': prefs.getString(_keyUserName),
      'role': prefs.getString(_keyUserRole),
    };
  }

  static Future<bool> isLoggedIn() async {
    final token = await getToken();
    return token != null;
  }

  static Future<void> clearAll() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();
  }
}