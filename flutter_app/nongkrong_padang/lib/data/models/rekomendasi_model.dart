import 'tempat_model.dart';

class RekomendasiItem {
  final String  idTempat;
  final String  namaTempat;
  final String? alamat;
  final double? ratingGoogle;
  final String? fotoUrl;
  final double  skorRelevansi;
  final SentimenAspek profilSentimen;
  final List<String>  tagKonteks;

  const RekomendasiItem({
    required this.idTempat,
    required this.namaTempat,
    this.alamat,
    this.ratingGoogle,
    this.fotoUrl,
    required this.skorRelevansi,
    required this.profilSentimen,
    this.tagKonteks = const [],
  });

  factory RekomendasiItem.fromJson(Map<String, dynamic> json) => RekomendasiItem(
    idTempat:      json['id_tempat'],
    namaTempat:    json['nama_tempat'],
    alamat:        json['alamat'],
    ratingGoogle:  json['rating_google']?.toDouble(),
    fotoUrl:       json['foto_url'],
    skorRelevansi: (json['skor_relevansi'] ?? 0).toDouble(),
    profilSentimen: SentimenAspek.fromJson(json['profil_sentimen'] ?? {}),
    tagKonteks:    List<String>.from(json['tag_konteks'] ?? []),
  );
}

class RekomendasiResponse {
  final int   total;
  final List<RekomendasiItem> rekomendasi;

  const RekomendasiResponse({
    required this.total,
    required this.rekomendasi,
  });

  factory RekomendasiResponse.fromJson(Map<String, dynamic> json) =>
    RekomendasiResponse(
      total: json['total'] ?? 0,
      rekomendasi: (json['rekomendasi'] as List? ?? [])
          .map((e) => RekomendasiItem.fromJson(e))
          .toList(),
    );
}