import uuid
import os
from sqlalchemy import create_engine, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.dialects.postgresql import JSONB

# Standalone script to avoid package errors
DATABASE_URL = "postgresql://nongkrong_user:nongkrong_pass@localhost:5432/nongkrong_db"

DATA_PADANG = [
    # ─── CO-WORKING & WORK-FRIENDLY ──────────────────────
    { "nama": "Kubik Koffie", "addr": "Jl. Olo Ladang No.12, Padang", "lat": -0.938, "lng": 100.358, "rat": 4.5, "cat": "co-working", "vec": [0.7, 0.1, 0.6, 0.2, 0.8, 0.1, 0.7, 0.1, 0.9, 0.1] },
    { "nama": "Mula Coffee", "addr": "Jl. Dr. Sutomo No.1, Padang", "lat": -0.928, "lng": 100.375, "rat": 4.6, "cat": "co-working", "vec": [0.8, 0.1, 0.6, 0.1, 0.7, 0.1, 0.8, 0.1, 0.8, 0.1] },
    { "nama": "Padang Digital Co-working", "addr": "Jl. Ahmad Yani, Padang", "lat": -0.942, "lng": 100.365, "rat": 4.8, "cat": "co-working", "vec": [0.6, 0.1, 0.7, 0.1, 0.9, 0.1, 0.6, 0.1, 0.95, 0.05] },
    { "nama": "Lalito Coffee Bar", "addr": "Jl. S. Parman No.116, Padang", "lat": -0.916, "lng": 100.364, "rat": 4.6, "cat": "kafe", "vec": [0.85, 0.05, 0.5, 0.2, 0.7, 0.1, 0.8, 0.1, 0.7, 0.1] },
    { "nama": "V Coffee", "addr": "Jl. Raden Saleh No.3, Padang", "lat": -0.925, "lng": 100.360, "rat": 4.7, "cat": "kafe", "vec": [0.95, 0.05, 0.4, 0.3, 0.7, 0.1, 0.9, 0.05, 0.7, 0.1] },
    { "nama": "Safari Garden", "addr": "Jl. Nipah No.10, Padang", "lat": -0.960, "lng": 100.355, "rat": 4.6, "cat": "resto", "vec": [0.9, 0.05, 0.5, 0.1, 0.8, 0.1, 0.7, 0.1, 0.6, 0.1] },
    { "nama": "Kopi Batigo", "addr": "Jl. KH. Ahmad Dahlan No.19, Padang", "lat": -0.920, "lng": 100.362, "rat": 4.4, "cat": "kafe", "vec": [0.7, 0.1, 0.8, 0.1, 0.7, 0.1, 0.7, 0.1, 0.6, 0.1] },
    { "nama": "Cafe Merdeka", "addr": "Jl. Diponegoro No.5, Padang", "lat": -0.952, "lng": 100.358, "rat": 4.3, "cat": "kafe", "vec": [0.7, 0.1, 0.8, 0.1, 0.8, 0.1, 0.6, 0.1, 0.5, 0.1] },
    { "nama": "Rimbun Espresso", "addr": "Jl. Kurao Pagang, Padang", "lat": -0.880, "lng": 100.380, "rat": 4.7, "cat": "kafe", "vec": [0.9, 0.05, 0.6, 0.1, 0.5, 0.2, 0.9, 0.05, 0.7, 0.1] },
    { "nama": "Coffee Theory", "addr": "Jl. Veteran No.60, Padang", "lat": -0.925, "lng": 100.355, "rat": 4.6, "cat": "kafe", "vec": [0.8, 0.1, 0.6, 0.1, 0.7, 0.1, 0.8, 0.1, 0.7, 0.1] },
    # Tambahkan lebih banyak untuk mencukupi 50+
    { "nama": "Kyoto Coffee Padang", "addr": "Jl. Belakang Olo, Padang", "lat": -0.935, "lng": 100.362, "rat": 4.5, "cat": "kafe", "vec": [0.8, 0.1, 0.6, 0.1, 0.7, 0.1, 0.8, 0.1, 0.7, 0.1] },
    { "nama": "Weekend Café", "addr": "Jl. Kelenteng No.1, Padang", "lat": -0.963, "lng": 100.368, "rat": 4.5, "cat": "resto", "vec": [0.9, 0.05, 0.4, 0.2, 0.6, 0.1, 0.8, 0.1, 0.5, 0.1] },
    { "nama": "Hau's Tea Padang", "addr": "Jl. Hos Cokroaminoto No.45, Padang", "lat": -0.955, "lng": 100.365, "rat": 4.5, "cat": "kafe", "vec": [0.8, 0.1, 0.7, 0.1, 0.7, 0.1, 0.7, 0.1, 0.6, 0.1] },
    { "nama": "Hideout Coffee Padang", "addr": "Jl. Hamka No.45, Padang", "lat": -0.890, "lng": 100.350, "rat": 4.5, "cat": "kafe", "vec": [0.8, 0.1, 0.7, 0.1, 0.6, 0.1, 0.7, 0.1, 0.6, 0.1] },
    { "nama": "Janji Jiwa Yani", "addr": "Jl. Ahmad Yani No.12, Padang", "lat": -0.942, "lng": 100.365, "rat": 4.4, "cat": "kafe", "vec": [0.6, 0.1, 0.8, 0.1, 0.8, 0.1, 0.7, 0.1, 0.4, 0.2] },
    { "nama": "EL'S Coffee Yani", "addr": "Jl. Ahmad Yani No.30, Padang", "lat": -0.942, "lng": 100.367, "rat": 4.4, "cat": "kafe", "vec": [0.7, 0.1, 0.6, 0.1, 0.8, 0.1, 0.7, 0.1, 0.7, 0.1] },
    { "nama": "Upnormal Ahmad Yani", "addr": "Jl. Ahmad Yani No.18, Padang", "lat": -0.943, "lng": 100.366, "rat": 4.2, "cat": "kafe", "vec": [0.7, 0.1, 0.7, 0.1, 0.8, 0.1, 0.6, 0.1, 0.6, 0.1] },
    { "nama": "Foresthree Sawahan", "addr": "Jl. Sawahan No.20, Padang", "lat": -0.930, "lng": 100.370, "rat": 4.4, "cat": "kafe", "vec": [0.7, 0.1, 0.7, 0.1, 0.7, 0.1, 0.7, 0.1, 0.6, 0.1] },
    { "nama": "G-Spot Gajah Mada", "addr": "Jl. Gajah Mada No.10, Padang", "lat": -0.900, "lng": 100.370, "rat": 4.4, "cat": "kafe", "vec": [0.7, 0.1, 0.8, 0.1, 0.7, 0.1, 0.6, 0.1, 0.5, 0.1] },
    { "nama": "Suko Khatib", "addr": "Jl. Khatib Sulaiman, Padang", "lat": -0.910, "lng": 100.360, "rat": 4.5, "cat": "kafe", "vec": [0.7, 0.1, 0.7, 0.1, 0.8, 0.1, 0.7, 0.1, 0.6, 0.1] },
    { "nama": "Kenangan Plaza Andalas", "addr": "Plaza Andalas, Padang", "lat": -0.940, "lng": 100.360, "rat": 4.3, "cat": "kafe", "vec": [0.6, 0.1, 0.8, 0.1, 0.9, 0.1, 0.6, 0.1, 0.4, 0.1] },
    { "nama": "Point Coffee Yani", "addr": "Jl. Ahmad Yani, Padang", "lat": -0.944, "lng": 100.366, "rat": 4.4, "cat": "kafe", "vec": [0.5, 0.1, 0.9, 0.1, 0.8, 0.1, 0.6, 0.1, 0.3, 0.2] },
    { "nama": "Gading Resto Sutomo", "addr": "Jl. Dr. Sutomo, Padang", "lat": -0.930, "lng": 100.380, "rat": 4.5, "cat": "resto", "vec": [0.8, 0.1, 0.6, 0.1, 0.7, 0.1, 0.8, 0.1, 0.4, 0.2] },
    { "nama": "Iko Gantinyo Nipah", "addr": "Jl. Nipah No.34, Padang", "lat": -0.965, "lng": 100.355, "rat": 4.6, "cat": "resto", "vec": [0.8, 0.1, 0.7, 0.1, 0.9, 0.1, 0.8, 0.1, 0.4, 0.2] },
    { "nama": "Sate Itam Pemuda", "addr": "Jl. Pemuda, Padang", "lat": -0.945, "lng": 100.360, "rat": 4.4, "cat": "resto", "vec": [0.6, 0.1, 0.9, 0.1, 0.8, 0.1, 0.7, 0.1, 0.2, 0.2] },
    { "nama": "Bopet Rajawali Juanda", "addr": "Jl. Juanda, Padang", "lat": -0.920, "lng": 100.355, "rat": 4.5, "cat": "resto", "vec": [0.7, 0.1, 0.8, 0.1, 0.8, 0.1, 0.7, 0.1, 0.3, 0.2] },
    { "nama": "RM Fuja Samudera", "addr": "Jl. Samudera, Padang", "lat": -0.950, "lng": 100.350, "rat": 4.6, "cat": "resto", "vec": [0.8, 0.1, 0.5, 0.1, 0.9, 0.1, 0.7, 0.1, 0.3, 0.2] },
    { "nama": "Kapau Ibu Hj Anis", "addr": "Jl. Khatib Sulaiman, Padang", "lat": -0.900, "lng": 100.365, "rat": 4.4, "cat": "resto", "vec": [0.6, 0.1, 0.7, 0.1, 0.8, 0.1, 0.7, 0.1, 0.2, 0.2] },
    { "nama": "Es Kim Teng Pondok", "addr": "Jl. Pondok, Padang", "lat": -0.960, "lng": 100.360, "rat": 4.5, "cat": "resto", "vec": [0.8, 0.1, 0.7, 0.1, 0.7, 0.1, 0.7, 0.1, 0.4, 0.2] },
    { "nama": "Old Town Gereja", "addr": "Jl. Gereja, Padang", "lat": -0.950, "lng": 100.360, "rat": 4.4, "cat": "kafe", "vec": [0.8, 0.1, 0.6, 0.1, 0.8, 0.1, 0.7, 0.1, 0.6, 0.1] },
    { "nama": "Sate Manangkabo Khatib", "addr": "Jl. Khatib Sulaiman, Padang", "lat": -0.895, "lng": 100.367, "rat": 4.5, "cat": "resto", "vec": [0.7, 0.1, 0.8, 0.1, 0.8, 0.1, 0.7, 0.1, 0.3, 0.2] },
    { "nama": "Bakso Lava Sawahan", "addr": "Jl. Sawahan, Padang", "lat": -0.930, "lng": 100.370, "rat": 4.3, "cat": "resto", "vec": [0.6, 0.1, 0.9, 0.1, 0.7, 0.1, 0.6, 0.1, 0.2, 0.2] },
    { "nama": "Bika Mariana Hamka", "addr": "Jl. Hamka, Padang", "lat": -0.880, "lng": 100.350, "rat": 4.6, "cat": "resto", "vec": [0.7, 0.1, 0.9, 0.1, 0.8, 0.1, 0.7, 0.1, 0.2, 0.2] },
    { "nama": "Kopi Nanyo Pondok", "addr": "Jl. Pondok, Padang", "lat": -0.962, "lng": 100.362, "rat": 4.5, "cat": "kafe", "vec": [0.8, 0.1, 0.9, 0.1, 0.8, 0.1, 0.7, 0.1, 0.3, 0.2] },
    { "nama": "Sate Syukur Hakim", "addr": "Jl. AR Hakim, Padang", "lat": -0.957, "lng": 100.365, "rat": 4.4, "cat": "resto", "vec": [0.7, 0.1, 0.8, 0.1, 0.7, 0.1, 0.7, 0.1, 0.2, 0.2] },
    { "nama": "Ayam Penyet Surabaya Yani", "addr": "Jl. Ahmad Yani, Padang", "lat": -0.943, "lng": 100.368, "rat": 4.3, "cat": "resto", "vec": [0.6, 0.1, 0.9, 0.1, 0.8, 0.1, 0.6, 0.1, 0.2, 0.2] },
    { "nama": "Pizza Hut Yani", "addr": "Jl. Ahmad Yani, Padang", "lat": -0.942, "lng": 100.365, "rat": 4.5, "cat": "resto", "vec": [0.9, 0.1, 0.5, 0.1, 0.8, 0.1, 0.9, 0.1, 0.6, 0.1] },
    { "nama": "McD Yani", "addr": "Jl. Ahmad Yani, Padang", "lat": -0.943, "lng": 100.367, "rat": 4.5, "cat": "resto", "vec": [0.8, 0.1, 0.7, 0.1, 0.8, 0.1, 0.8, 0.1, 0.7, 0.1] },
    { "nama": "KFC Andalas", "addr": "Plaza Andalas, Padang", "lat": -0.941, "lng": 100.361, "rat": 4.4, "cat": "resto", "vec": [0.7, 0.1, 0.7, 0.1, 0.9, 0.1, 0.7, 0.1, 0.6, 0.1] },
    { "nama": "Solaria Transmart", "addr": "Transmart Padang, Padang", "lat": -0.890, "lng": 100.360, "rat": 4.2, "cat": "resto", "vec": [0.8, 0.1, 0.6, 0.1, 0.8, 0.1, 0.7, 0.1, 0.5, 0.1] },
    { "nama": "Ichiban Sushi Transmart", "addr": "Transmart Padang, Padang", "lat": -0.891, "lng": 100.361, "rat": 4.3, "cat": "resto", "vec": [0.8, 0.1, 0.5, 0.1, 0.8, 0.1, 0.8, 0.1, 0.4, 0.2] },
    { "nama": "Bakmi Naga Andalas", "addr": "Plaza Andalas, Padang", "lat": -0.942, "lng": 100.362, "rat": 4.1, "cat": "resto", "vec": [0.6, 0.1, 0.8, 0.1, 0.8, 0.1, 0.6, 0.1, 0.3, 0.2] },
    { "nama": "Holland Sudirman", "addr": "Jl. Sudirman, Padang", "lat": -0.945, "lng": 100.365, "rat": 4.6, "cat": "toko", "vec": [0.7, 0.1, 0.5, 0.1, 0.8, 0.1, 0.8, 0.1, 0.3, 0.2] },
    { "nama": "JCO Basko", "addr": "Basko Grand Mall, Padang", "lat": -0.880, "lng": 100.355, "rat": 4.5, "cat": "kafe", "vec": [0.8, 0.1, 0.6, 0.1, 0.7, 0.1, 0.8, 0.1, 0.6, 0.1] },
    { "nama": "BreadTalk Basko", "addr": "Basko Grand Mall, Padang", "lat": -0.881, "lng": 100.356, "rat": 4.4, "cat": "toko", "vec": [0.7, 0.1, 0.6, 0.1, 0.7, 0.1, 0.7, 0.1, 0.3, 0.2] },
    { "nama": "Gramedia Damar", "addr": "Jl. Damar, Padang", "lat": -0.940, "lng": 100.362, "rat": 4.7, "cat": "toko", "vec": [0.8, 0.1, 0.7, 0.1, 0.7, 0.1, 0.9, 0.1, 0.8, 0.1] },
    { "nama": "Perpustakaan Daerah Padang", "addr": "Jl. Diponegoro, Padang", "lat": -0.950, "lng": 100.355, "rat": 4.8, "cat": "perpustakaan", "vec": [0.6, 0.05, 0.95, 0.05, 0.8, 0.1, 0.9, 0.05, 0.95, 0.05] },
    { "nama": "Museum Adityawarman Padang", "addr": "Jl. Diponegoro, Padang", "lat": -0.952, "lng": 100.357, "rat": 4.6, "cat": "wisata", "vec": [0.8, 0.1, 0.9, 0.05, 0.9, 0.1, 0.8, 0.1, 0.5, 0.1] },
    { "nama": "D'Ox Ville Hotel", "addr": "Jl. Kampung Sebelah No. 28, Padang", "lat": -0.955, "lng": 100.358, "rat": 4.7, "cat": "hotel", "vec": [0.9, 0.05, 0.4, 0.3, 0.6, 0.1, 0.9, 0.05, 0.8, 0.1] },
    { "nama": "The Axana Hotel", "addr": "Jl. Bundo Kanduang No. 14, Padang", "lat": -0.948, "lng": 100.355, "rat": 4.4, "cat": "hotel", "vec": [0.8, 0.1, 0.5, 0.2, 0.7, 0.1, 0.8, 0.1, 0.7, 0.1] },
    { "nama": "Grand Zuri Padang", "addr": "Jl. Thamrin No. 27, Padang", "lat": -0.952, "lng": 100.365, "rat": 4.5, "cat": "hotel", "vec": [0.8, 0.1, 0.6, 0.1, 0.8, 0.1, 0.8, 0.1, 0.7, 0.1] },
]

def standalone_inject():
    print(f"Connecting to {DATABASE_URL}")
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        print(f"Injecting {len(DATA_PADANG)} places...")
        added = 0
        for d in DATA_PADANG:
            # Check if exists
            res = conn.execute(text("SELECT id_tempat FROM tempat WHERE nama_tempat = :name"), {"name": d["nama"]}).fetchone()
            if res: continue
            
            tid = str(uuid.uuid4())
            conn.execute(text("""
                INSERT INTO tempat (id_tempat, nama_tempat, alamat, latitude, longitude, kategori, rating_google, place_id_google)
                VALUES (:id, :name, :addr, :lat, :lng, :cat, :rat, :pid)
            """), {
                "id": tid, "name": d["nama"], "addr": d["addr"],
                "lat": d["lat"], "lng": d["lng"], "cat": d["cat"],
                "rat": d["rat"], "pid": f"sa_{uuid.uuid4().hex[:10]}"
            })
            
            conn.execute(text("""
                INSERT INTO profil_tempat (id_tempat, vektor_sentimen, total_ulasan)
                VALUES (:id, :vec, :ulasan)
            """), {
                "id": tid, "vec": d["vec"], "ulasan": 25
            })
            added += 1
            
        conn.commit()
        print(f"DONE! Added {added} places.")

if __name__ == "__main__":
    standalone_inject()
