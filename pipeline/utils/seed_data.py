"""
Seed data dummy untuk testing pipeline tanpa Google API key.
Jalankan sekali: python utils/seed_data.py
"""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db_helper import get_connection
import uuid

TEMPAT_DUMMY = [
    {
        "nama_tempat": "V Kopi Padang",
        "alamat": "Jl. Raden Saleh No.12, Padang Barat",
        "latitude": -0.9471,
        "longitude": 100.3541,
        "kategori": "kafe",
        "rating_google": 4.8,
        "place_id_google": "dummy_v_kopi_001",
        "foto_url": None,
    },
    {
        "nama_tempat": "Kopigo",
        "alamat": "Jl. Pulau Karam, Padang Selatan",
        "latitude": -0.9612,
        "longitude": 100.3589,
        "kategori": "kafe",
        "rating_google": 4.6,
        "place_id_google": "dummy_kopigo_002",
        "foto_url": None,
    },
    {
        "nama_tempat": "Kopmil Om Ping",
        "alamat": "Jl. Pondok No.5, Padang Selatan",
        "latitude": -0.9534,
        "longitude": 100.3512,
        "kategori": "kafe",
        "rating_google": 4.8,
        "place_id_google": "dummy_kopmil_003",
        "foto_url": None,
    },
    {
        "nama_tempat": "Kiosk 19",
        "alamat": "Jl. Sudirman, Padang",
        "latitude": -0.9398,
        "longitude": 100.3623,
        "kategori": "kafe",
        "rating_google": 4.5,
        "place_id_google": "dummy_kiosk19_004",
        "foto_url": None,
    },
]

ULASAN_DUMMY = [
    # V Kopi — bagus di suasana & fasilitas, harga agak mahal
    ("dummy_v_kopi_001", "Tempatnya nyaman banget buat nugas, wifi kencang, colokan banyak. Tapi harganya lumayan mahal untuk mahasiswa.", 4, "Andi S."),
    ("dummy_v_kopi_001", "Suasananya enak, lighting bagus cocok buat foto. Pelayanan ramah dan cepat.", 5, "Rina M."),
    ("dummy_v_kopi_001", "WiFi-nya kencang banget, tapi parkir susah kalau akhir pekan.", 4, "Budi K."),
    ("dummy_v_kopi_001", "Kopinya mantap, harga wajar untuk kualitasnya. Lokasi strategis di tengah kota.", 5, "Sari P."),
    ("dummy_v_kopi_001", "Pelayanannya lambat kalau lagi ramai, tapi tempatnya nyaman.", 3, "Doni A."),
    # Kopigo — bagus di suasana & harga
    ("dummy_kopigo_002", "Harganya murah meriah, cocok banget buat kantong mahasiswa. Suasananya juga cozy.", 5, "Maya L."),
    ("dummy_kopigo_002", "Tempatnya sedang populer, selalu ramai. Tapi pelayanan tetap oke dan cepat.", 4, "Reza F."),
    ("dummy_kopigo_002", "Kopi lamaknya (enak) dan harganya terjangkau. Recommended buat nongkrong santai.", 5, "Nita R."),
    ("dummy_kopigo_002", "Fasilitas biasa aja, wifi kadang lemot. Tapi suasana outdoor-nya bagus.", 3, "Hendra B."),
    # Kopmil Om Ping — excellent overall
    ("dummy_kopmil_003", "Tempatnya rancak (bagus) banget! Suasana nyaman, pelayanan ramah, harga reasonable.", 5, "Putri W."),
    ("dummy_kopmil_003", "Sangat bagus untuk rombongan besar. Tersedia area outdoor dan indoor.", 5, "Fajar M."),
    ("dummy_kopmil_003", "Kopinya enak, tempatnya instagramable. WiFi kencang, colokan tersedia.", 5, "Laila K."),
    ("dummy_kopmil_003", "Pelayanannya agak lambat kalau lagi jam makan siang, tapi kualitas makanannya mantap.", 4, "Rio S."),
    # Kiosk 19 — bagus di fasilitas, lokasi kurang strategis
    ("dummy_kiosk19_004", "WiFi super kencang, cocok banget buat kerja remote. Tapi lokasinya agak tersembunyi.", 4, "Irma D."),
    ("dummy_kiosk19_004", "Harga standard, pelayanan oke. Tempatnya nyaman meskipun agak kecil.", 4, "Wahyu P."),
    ("dummy_kiosk19_004", "Akses parkir mudah, dekat jalan utama. Suasana tenang cocok buat meeting.", 5, "Desi A."),
]

def seed():
    conn = get_connection()
    cur = conn.cursor()
    
    print("[SEED] Memasukkan data tempat dummy...")
    tempat_ids = {}
    
    for t in TEMPAT_DUMMY:
        cur.execute("""
            INSERT INTO tempat 
                (nama_tempat, alamat, latitude, longitude, 
                 kategori, rating_google, place_id_google)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (place_id_google) DO UPDATE SET
                rating_google = EXCLUDED.rating_google
            RETURNING id_tempat, place_id_google
        """, (
            t["nama_tempat"], t["alamat"], t["latitude"], t["longitude"],
            t["kategori"], t["rating_google"], t["place_id_google"]
        ))
        row = cur.fetchone()
        tempat_ids[t["place_id_google"]] = str(row[0])
        print(f"  ✓ {t['nama_tempat']} → {str(row[0])[:8]}...")
    
    print("\n[SEED] Memasukkan ulasan dummy...")
    for place_id, teks, rating, author in ULASAN_DUMMY:
        id_tempat = tempat_ids.get(place_id)
        if not id_tempat:
            continue
        
        review_id = f"{place_id}_{author.replace(' ','_').lower()}"
        cur.execute("""
            INSERT INTO ulasan (id_tempat, teks_ulasan, rating, author_name, review_id_google)
            VALUES (%s,%s,%s,%s,%s)
            ON CONFLICT (review_id_google) DO NOTHING
        """, (id_tempat, teks, rating, author, review_id))
        print(f"  ✓ Ulasan: '{teks[:40]}...'")
    
    # Buat profil tempat awal (vektor kosong, diisi ABSA nanti)
    print("\n[SEED] Membuat profil tempat awal...")
    for place_id, id_tempat in tempat_ids.items():
        cur.execute("""
            INSERT INTO profil_tempat (id_tempat, vektor_sentimen, total_ulasan)
            VALUES (%s, ARRAY[0,0,0,0,0,0,0,0,0,0]::float[], 
                    (SELECT COUNT(*) FROM ulasan WHERE id_tempat = %s::uuid))
            ON CONFLICT (id_tempat) DO UPDATE SET
                total_ulasan = EXCLUDED.total_ulasan
        """, (id_tempat, id_tempat))
        print(f"  ✓ Profil dibuat untuk tempat {id_tempat[:8]}...")
    
    conn.commit()
    cur.close()
    conn.close()
    print("\n[SEED] ✅ Selesai! Data siap digunakan.")

if __name__ == "__main__":
    seed()