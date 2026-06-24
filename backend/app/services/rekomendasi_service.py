import numpy as np
from sqlalchemy.orm import Session
from typing import List
from app.models.models import Tempat, ProfilTempat
from app.schemas.schemas import KonteksRequest, RekomendasiResponse, RekomendasiItem, SentimenAspek

# ─── LOOKUP TABLE KONTEKS ─────────────────────────────────────────────────────
# Bobot per dimensi: [suasana+, suasana-, harga+, harga-, lokasi+, lokasi-,
#                     pelayanan+, pelayanan-, fasilitas+, fasilitas-]
# Sesuai Gambar 3.3 pada proposal (contextual weight vector)

KONTEKS_BOBOT = {
    # (WAKTU, TUJUAN, ROMBONGAN, HARI)
    ("pagi", "kerja", "sendiri", "kerja"):   [0.3, 0.1, 0.2, 0.2, 0.1, 0.1, 0.2, 0.1, 0.6, 0.1], # Fokus fasilitas (WiFi)
    ("pagi", "kerja", "sendiri", "akhir_pekan"): [0.4, 0.1, 0.2, 0.1, 0.2, 0.1, 0.2, 0.1, 0.5, 0.1], # Lebih rileks
    ("siang", "kerja", "sendiri", "kerja"):  [0.3, 0.1, 0.3, 0.2, 0.2, 0.1, 0.2, 0.1, 0.5, 0.1],
    ("malam", "kencan", "berdua", "akhir_pekan"): [0.8, 0.1, 0.2, 0.1, 0.2, 0.1, 0.6, 0.1, 0.1, 0.1], # Fokus suasana & pelayanan
    ("malam", "hangout", "kecil", "kerja"):  [0.6, 0.1, 0.4, 0.2, 0.3, 0.1, 0.4, 0.1, 0.2, 0.1],
    ("malam", "hangout", "kecil", "akhir_pekan"): [0.7, 0.1, 0.3, 0.1, 0.4, 0.1, 0.4, 0.1, 0.2, 0.1],
    ("sore", "hangout", "besar", "akhir_pekan"): [0.6, 0.1, 0.3, 0.2, 0.4, 0.1, 0.3, 0.1, 0.3, 0.1], # Fokus lokasi/kapasitas
}

BOBOT_DEFAULT = [0.4, 0.1, 0.3, 0.1, 0.3, 0.1, 0.3, 0.1, 0.3, 0.1]

def get_bobot_konteks(waktu: str, tujuan: str, rombongan: str, hari: str) -> List[float]:
    """Ambil vektor bobot berdasarkan kombinasi konteks (4 dimensi)."""
    key = (waktu, tujuan, rombongan, hari)
    return KONTEKS_BOBOT.get(key, BOBOT_DEFAULT)

def weighted_cosine_similarity(v_tempat: List[float], w_konteks: List[float]) -> float:
    """
    Hitung weighted cosine similarity.
    score(i) = sim(v_tempat_i, v_konteks) dengan bobot w_konteks
    """
    v = np.array(v_tempat, dtype=float)
    w = np.array(w_konteks, dtype=float)
    
    # Weighted dot product
    weighted_v = v * w
    weighted_w = w * w
    
    norm_v = np.linalg.norm(weighted_v)
    norm_w = np.linalg.norm(weighted_w)
    
    if norm_v == 0 or norm_w == 0:
        return 0.0
    
    return float(np.dot(weighted_v, weighted_w) / (norm_v * norm_w))

def generate_tag_konteks(vektor: List[float], konteks: KonteksRequest) -> List[str]:
    """Generate tag deskriptif berdasarkan profil sentimen dan konteks."""
    tags = []
    
    if vektor[8] > 0.6:  # fasilitas_pos tinggi
        tags.append("WiFi Cepat")
    if vektor[0] > 0.6:  # suasana_pos tinggi
        tags.append("Suasana Nyaman")
    if vektor[2] > 0.6:  # harga_pos tinggi
        tags.append("Harga Terjangkau")
    if vektor[6] > 0.6:  # pelayanan_pos tinggi
        tags.append("Pelayanan Ramah")
    if konteks.tujuan == "kerja":
        tags.append("Cocok untuk Nugas")
    if konteks.rombongan in ["kecil", "besar"]:
        tags.append("Cocok untuk Rombongan")
    
    return tags[:3]  # max 3 tag

class RekomendasiService:
    def __init__(self, db: Session):
        self.db = db

    def hitung_rekomendasi(self, konteks: KonteksRequest) -> RekomendasiResponse:
        """
        Fungsi utama untuk menghitung rekomendasi berbasis konteks.
        Dilengkapi dengan fallback ke tempat terpopuler jika data profil belum siap.
        """
        # 1. Ambil bobot konteks (sekarang 4 dimensi: waktu, tujuan, rombongan, hari)
        bobot = get_bobot_konteks(konteks.waktu, konteks.tujuan, konteks.rombongan, konteks.hari)
        
        # 2. Ambil semua profil tempat dari database (opsional filter kategori)
        query = self.db.query(ProfilTempat).join(Tempat)
        if konteks.kategori:
            query = query.filter(Tempat.kategori == konteks.kategori)
        
        profil_list = query.all()
        
        # Check jika database benar-benar kosong (bahkan tabel tempat kosong)
        if not profil_list:
            # Coba cek apakah ada data di tabel tempat walaupun belum ada profilnya
            status_tempat = self.db.query(Tempat).count()
            if status_tempat == 0:
                print("[REKOMENDASI] Database tempat kosong.")
                return RekomendasiResponse(konteks=konteks.dict(), total=0, rekomendasi=[])
            
            print("[REKOMENDASI] Profil kosong, fallback ke tempat terpopuler.")
            return self._get_fallback_populer(konteks)
        
        # 3. Hitung skor untuk setiap tempat
        scored = []
        for profil in profil_list:
            if profil.vektor_sentimen is None:
                continue
            
            skor = weighted_cosine_similarity(profil.vektor_sentimen, bobot)
            scored.append((skor, profil))
        
        # 4. Cek hasil scoring. Jika semua 0 (Cold Start), gunakan fallback.
        max_skor = max([s[0] for s in scored]) if scored else 0
        if max_skor == 0:
            print("[REKOMENDASI] Skor semua nol (Cold Start), fallback ke tempat terpopuler.")
            return self._get_fallback_populer(konteks)
            
        # 5. Urutkan descending dan ambil Top-K
        scored.sort(key=lambda x: x[0], reverse=True)
        top_k = scored[:konteks.top_k]
        
        # 6. Format response
        hasil = []
        for skor, profil in top_k:
            v = profil.vektor_sentimen
            sentimen = SentimenAspek(
                suasana_pos=v[0], suasana_neg=v[1],
                harga_pos=v[2],   harga_neg=v[3],
                lokasi_pos=v[4],  lokasi_neg=v[5],
                pelayanan_pos=v[6],pelayanan_neg=v[7],
                fasilitas_pos=v[8],fasilitas_neg=v[9]
            )
            
            tags = generate_tag_konteks(v, konteks)
            
            hasil.append(RekomendasiItem(
                id_tempat=profil.tempat.id_tempat,
                nama_tempat=profil.tempat.nama_tempat,
                alamat=profil.tempat.alamat,
                rating_google=profil.tempat.rating_google,
                foto_url=profil.tempat.foto_url,
                skor_relevansi=round(skor, 4),
                profil_sentimen=sentimen,
                tag_konteks=tags
            ))
        
        return RekomendasiResponse(
            konteks=konteks.dict(),
            total=len(hasil),
            rekomendasi=hasil
        )

    def _get_fallback_populer(self, konteks: KonteksRequest) -> RekomendasiResponse:
        """Helper untuk mengambil tempat dengan rating tertinggi sebagai fallback."""
        query = self.db.query(Tempat)
        if konteks.kategori:
            query = query.filter(Tempat.kategori == konteks.kategori)
            
        top_rated = query.order_by(Tempat.rating_google.desc()).limit(konteks.top_k).all()
        
        hasil = []
        for t in top_rated:
            # Karena profil belum ada atau nol, gunakan dummy profil sentimen netral
            sentimen = SentimenAspek()
            
            hasil.append(RekomendasiItem(
                id_tempat=t.id_tempat,
                nama_tempat=t.nama_tempat,
                alamat=t.alamat,
                rating_google=t.rating_google,
                foto_url=t.foto_url,
                skor_relevansi=0.0,
                profil_sentimen=sentimen,
                tag_konteks=["Terpopuler"]
            ))
            
        return RekomendasiResponse(
            konteks=konteks.dict(),
            total=len(hasil),
            rekomendasi=hasil
        )
