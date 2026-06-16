class SentimenAspek {
  final double suasanaPos, suasanaNeg;
  final double hargaPos,   hargaNeg;
  final double lokasiPos,  lokasiNeg;
  final double pelayananPos, pelayananNeg;
  final double fasilitasPos, fasilitasNeg;

  const SentimenAspek({
    this.suasanaPos = 0, this.suasanaNeg = 0,
    this.hargaPos = 0,   this.hargaNeg = 0,
    this.lokasiPos = 0,  this.lokasiNeg = 0,
    this.pelayananPos = 0, this.pelayananNeg = 0,
    this.fasilitasPos = 0, this.fasilitasNeg = 0,
  });

  factory SentimenAspek.fromJson(Map<String, dynamic> json) => SentimenAspek(
    suasanaPos:   (json['suasana_pos']   ?? 0).toDouble(),
    suasanaNeg:   (json['suasana_neg']   ?? 0).toDouble(),
    hargaPos:     (json['harga_pos']     ?? 0).toDouble(),
    hargaNeg:     (json['harga_neg']     ?? 0).toDouble(),
    lokasiPos:    (json['lokasi_pos']    ?? 0).toDouble(),
    lokasiNeg:    (json['lokasi_neg']    ?? 0).toDouble(),
    pelayananPos: (json['pelayanan_pos'] ?? 0).toDouble(),
    pelayananNeg: (json['pelayanan_neg'] ?? 0).toDouble(),
    fasilitasPos: (json['fasilitas_pos'] ?? 0).toDouble(),
    fasilitasNeg: (json['fasilitas_neg'] ?? 0).toDouble(),
  );
}

class TempatModel {
  final String  idTempat;
  final String  namaTempat;
  final String? alamat;
  final double? latitude;
  final double? longitude;
  final double? ratingGoogle;
  final String? fotoUrl;
  final int     totalUlasan;
  final SentimenAspek? profilSentimen;

  const TempatModel({
    required this.idTempat,
    required this.namaTempat,
    this.alamat,
    this.latitude,
    this.longitude,
    this.ratingGoogle,
    this.fotoUrl,
    this.totalUlasan = 0,
    this.profilSentimen,
  });

  factory TempatModel.fromJson(Map<String, dynamic> json) => TempatModel(
    idTempat:    json['id_tempat'],
    namaTempat:  json['nama_tempat'],
    alamat:      json['alamat'],
    latitude:    json['latitude']?.toDouble(),
    longitude:   json['longitude']?.toDouble(),
    ratingGoogle: json['rating_google']?.toDouble(),
    fotoUrl:     json['foto_url'],
    totalUlasan: json['total_ulasan'] ?? 0,
    profilSentimen: json['profil_sentimen'] != null
        ? SentimenAspek.fromJson(json['profil_sentimen'])
        : null,
  );
}