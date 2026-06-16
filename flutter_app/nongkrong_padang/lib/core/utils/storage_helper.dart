import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class StorageHelper {
  static const _storage = FlutterSecureStorage();
  
  static const _keyToken    = 'access_token';
  static const _keyUserId   = 'user_id';
  static const _keyUserName = 'user_name';
  static const _keyUserRole = 'user_role';

  // Token
  static Future<void> saveToken(String token) =>
      _storage.write(key: _keyToken, value: token);

  static Future<String?> getToken() =>
      _storage.read(key: _keyToken);

  static Future<void> deleteToken() =>
      _storage.delete(key: _keyToken);

  // User info
  static Future<void> saveUserInfo({
    required String id,
    required String nama,
    required String role,
  }) async {
    await _storage.write(key: _keyUserId,   value: id);
    await _storage.write(key: _keyUserName, value: nama);
    await _storage.write(key: _keyUserRole, value: role);
  }

  static Future<Map<String, String?>> getUserInfo() async => {
    'id':   await _storage.read(key: _keyUserId),
    'nama': await _storage.read(key: _keyUserName),
    'role': await _storage.read(key: _keyUserRole),
  };

  static Future<bool> isLoggedIn() async =>
      (await getToken()) != null;

  static Future<void> clearAll() => _storage.deleteAll();
}