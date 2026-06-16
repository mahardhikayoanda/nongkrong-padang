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
    # WAKTU × TUJUAN × ROMBONGAN
    ("pagi", "kerja", "sendiri"):   [0.3, 0.1, 0.2, 0.2, 0.1, 0.1, 0.2, 0.1, 0.5, 0.2],
    ("pagi", "kerja", "berdua"):    [0.3, 0.1, 0.2, 0.2, 0.1, 0.1, 0.2, 0.1, 0.4, 0.2],
    ("siang", "kerja", "sendiri"):  [0.3, 0.1, 0.3, 0.2, 0.2, 0.1, 0.2, 0.1, 0.5, 0.1],
    ("malam", "kencan", "berdua"):  [0.6, 0.2, 0.2, 0.1, 0.2, 0.1, 0.5, 0.2, 0.1, 0.1],
    ("malam", "hangout", "kecil"):  [0.5, 0.1, 0.3, 0.2, 0.3, 0.1, 0.3, 0.1, 0.2, 0.1],
    ("sore", "hangout", "besar"):   [0.4, 0.1, 0.3, 0.2, 0.4, 0.1, 0.3, 0.1, 0.2, 0.1],
    ("siang", "meeting", "kecil"):  [0.3, 0.1, 0.2, 0.1, 0.2, 0.1, 0.4, 0.2, 0.4, 0.1],
}

BOBOT_DEFAULT = [0.4, 0.1, 0.3, 0.1, 0.3, 0.1, 0.3, 0.1, 0.3, 0.1]

def get_bobot_konteks(waktu: str, tujuan: str, rombongan: str) -> List[float]:
    """Ambil vektor bobot berdasarkan kombinasi konteks."""
    key = (waktu, tujuan, rombongan)
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
        # 1. Ambil bobot konteks
        bobot = get_bobot_konteks(konteks.waktu, konteks.tujuan, konteks.rombongan)
        
        # 2. Ambil semua profil tempat dari database
        profil_list = self.db.query(ProfilTempat).join(Tempat).all()
        
        if not profil_list:
            return RekomendasiResponse(
                konteks=konteks.dict(),
                total=0,
                rekomendasi=[]
            )
        
        # 3. Hitung skor untuk setiap tempat
        scored = []
        for profil in profil_list:
            if profil.vektor_sentimen is None:
                continue
            
            skor = weighted_cosine_similarity(profil.vektor_sentimen, bobot)
            scored.append((skor, profil))
        
        # 4. Urutkan descending dan ambil Top-K
        scored.sort(key=lambda x: x[0], reverse=True)
        top_k = scored[:konteks.top_k]
        
        # 5. Format response
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