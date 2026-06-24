import uuid
from app.db.database import SessionLocal
from app.models.models import Tempat, ProfilTempat

# Data 50+ Tempat di Padang (Mixed: Cafe, Co-working, Resto, Library)
# Profil Sentimen: [suasana+, suasana-, harga+, harga-, lokasi+, lokasi-, pelayanan+, pelayanan-, fasilitas+, fasilitas-]
DATA_PADANG = [
    # ─── CO-WORKING & WORK-FRIENDLY ──────────────────────
    {
        "nama": "Kubik Koffie",
        "addr": "Jl. Olo Ladang No.12, Padang",
        "lat": -0.938, "lng": 100.358, "rat": 4.5, "cat": "co-working",
        "vec": [0.7, 0.1, 0.6, 0.2, 0.8, 0.1, 0.7, 0.1, 0.9, 0.1] # High Fasilitas (WiFi, Plug)
    },
    {
        "nama": "Mula Coffee",
        "addr": "Jl. Dr. Sutomo No.1, Padang",
        "lat": -0.928, "lng": 100.375, "rat": 4.6, "cat": "co-working",
        "vec": [0.8, 0.1, 0.6, 0.1, 0.7, 0.1, 0.8, 0.1, 0.8, 0.1]
    },
    {
        "nama": "Padang Digital Co-working",
        "addr": "Jl. Ahmad Yani, Padang",
        "lat": -0.942, "lng": 100.365, "rat": 4.8, "cat": "co-working",
        "vec": [0.6, 0.1, 0.7, 0.1, 0.9, 0.1, 0.6, 0.1, 0.95, 0.05]
    },
    {
        "nama": "Lalito Coffee Bar",
        "addr": "Jl. S. Parman No.116, Padang",
        "lat": -0.916, "lng": 100.364, "rat": 4.6, "cat": "kafe",
        "vec": [0.85, 0.05, 0.5, 0.2, 0.7, 0.1, 0.8, 0.1, 0.7, 0.1]
    },
    {
        "nama": "Kyoto Coffee",
        "addr": "Jl. Belakang Olo, Padang",
        "lat": -0.935, "lng": 100.362, "rat": 4.5, "cat": "kafe",
        "vec": [0.8, 0.1, 0.6, 0.1, 0.7, 0.1, 0.8, 0.1, 0.7, 0.1]
    },
    # ─── HANGOUT & DISKUSI ─────────────────────────────
    {
        "nama": "Pavilon Coffee",
        "addr": "Jl. Hayam Wuruk No.30, Padang",
        "lat": -0.947, "lng": 100.362, "rat": 4.5, "cat": "kafe",
        "vec": [0.9, 0.05, 0.6, 0.1, 0.8, 0.1, 0.8, 0.1, 0.6, 0.1]
    },
    {
        "nama": "V Coffee",
        "addr": "Jl. Raden Saleh No.3, Padang",
        "lat": -0.925, "lng": 100.360, "rat": 4.7, "cat": "kafe",
        "vec": [0.95, 0.05, 0.4, 0.3, 0.7, 0.1, 0.9, 0.05, 0.7, 0.1]
    },
    {
        "nama": "Weekend Café",
        "addr": "Jl. Kelenteng No.1, Padang",
        "lat": -0.963, "lng": 100.368, "rat": 4.5, "cat": "resto",
        "vec": [0.9, 0.05, 0.4, 0.2, 0.6, 0.1, 0.8, 0.1, 0.5, 0.1]
    },
    {
        "nama": "Safari Garden",
        "addr": "Jl. Nipah No.10, Padang",
        "lat": -0.960, "lng": 100.355, "rat": 4.6, "cat": "resto",
        "vec": [0.9, 0.05, 0.5, 0.1, 0.8, 0.1, 0.7, 0.1, 0.6, 0.1]
    },
    {
        "nama": "Kopi Batigo",
        "addr": "Jl. KH. Ahmad Dahlan No.19, Padang",
        "lat": -0.920, "lng": 100.362, "rat": 4.4, "cat": "kafe",
        "vec": [0.7, 0.1, 0.8, 0.1, 0.7, 0.1, 0.7, 0.1, 0.6, 0.1]
    },
    {
        "nama": "Cafe Merdeka",
        "addr": "Jl. Diponegoro No.5, Padang",
        "lat": -0.952, "lng": 100.358, "rat": 4.3, "cat": "kafe",
        "vec": [0.7, 0.1, 0.8, 0.1, 0.8, 0.1, 0.6, 0.1, 0.5, 0.1]
    },
    {
        "nama": "Hau's Tea",
        "addr": "Jl. Hos Cokroaminoto No.45, Padang",
        "lat": -0.955, "lng": 100.365, "rat": 4.5, "cat": "kafe",
        "vec": [0.8, 0.1, 0.7, 0.1, 0.7, 0.1, 0.7, 0.1, 0.6, 0.1]
    },
    {
        "nama": "Rimbun Espresso",
        "addr": "Jl. Kurao Pagang, Padang",
        "lat": -0.880, "lng": 100.380, "rat": 4.7, "cat": "kafe",
        "vec": [0.9, 0.05, 0.6, 0.1, 0.5, 0.2, 0.9, 0.05, 0.7, 0.1]
    },
    {
        "nama": "Coffee Theory",
        "addr": "Jl. Veteran No.60, Padang",
        "lat": -0.925, "lng": 100.355, "rat": 4.6, "cat": "kafe",
        "vec": [0.8, 0.1, 0.6, 0.1, 0.7, 0.1, 0.8, 0.1, 0.7, 0.1]
    },
    {
        "nama": "Hideout Coffee",
        "addr": "Jl. Hamka No.45, Padang",
        "lat": -0.890, "lng": 100.350, "rat": 4.5, "cat": "kafe",
        "vec": [0.8, 0.1, 0.7, 0.1, 0.6, 0.1, 0.7, 0.1, 0.6, 0.1]
    },
    # ─── TEMPAT POPULER LAINNYA ─────────────────────────
    { "nama": "Kopi Janji Jiwa - Ahmad Yani", "addr": "Jl. Ahmad Yani No.12, Padang", "lat": -0.942, "lng": 100.365, "rat": 4.4, "cat": "kafe", "vec": [0.6, 0.1, 0.8, 0.1, 0.8, 0.1, 0.7, 0.1, 0.4, 0.2] },
    { "nama": "EL'S Coffee", "addr": "Jl. Ahmad Yani No.30, Padang", "lat": -0.942, "lng": 100.367, "rat": 4.4, "cat": "kafe", "vec": [0.7, 0.1, 0.6, 0.1, 0.8, 0.1, 0.7, 0.1, 0.7, 0.1] },
    { "nama": "Warunk Upnormal", "addr": "Jl. Ahmad Yani No.18, Padang", "lat": -0.943, "lng": 100.366, "rat": 4.2, "cat": "kafe", "vec": [0.7, 0.1, 0.7, 0.1, 0.8, 0.1, 0.6, 0.1, 0.6, 0.1] },
    { "nama": "Foresthree Coffee", "addr": "Jl. Sawahan No.20, Padang", "lat": -0.930, "lng": 100.370, "rat": 4.4, "cat": "kafe", "vec": [0.7, 0.1, 0.7, 0.1, 0.7, 0.1, 0.7, 0.1, 0.6, 0.1] },
    { "nama": "G-Spot Coffee", "addr": "Jl. Gajah Mada No.10, Padang", "lat": -0.900, "lng": 100.370, "rat": 4.4, "cat": "kafe", "vec": [0.7, 0.1, 0.8, 0.1, 0.7, 0.1, 0.6, 0.1, 0.5, 0.1] },
    { "nama": "Suko Kopi", "addr": "Jl. Khatib Sulaiman, Padang", "lat": -0.910, "lng": 100.360, "rat": 4.5, "cat": "kafe", "vec": [0.7, 0.1, 0.7, 0.1, 0.8, 0.1, 0.7, 0.1, 0.6, 0.1] },
    { "nama": "Kopi Kenangan - Plaza Andalas", "addr": "Plaza Andalas, Padang", "lat": -0.940, "lng": 100.360, "rat": 4.3, "cat": "kafe", "vec": [0.6, 0.1, 0.8, 0.1, 0.9, 0.1, 0.6, 0.1, 0.4, 0.1] },
    { "nama": "Point Coffee - Ahmad Yani", "addr": "Jl. Ahmad Yani, Padang", "lat": -0.944, "lng": 100.366, "rat": 4.4, "cat": "kafe", "vec": [0.5, 0.1, 0.9, 0.1, 0.8, 0.1, 0.6, 0.1, 0.3, 0.2] },
    { "nama": "Gading Resto", "addr": "Jl. Dr. Sutomo, Padang", "lat": -0.930, "lng": 100.380, "rat": 4.5, "cat": "resto", "vec": [0.8, 0.1, 0.6, 0.1, 0.7, 0.1, 0.8, 0.1, 0.4, 0.2] },
    { "nama": "Iko Gantinyo", "addr": "Jl. Nipah No.34, Padang", "lat": -0.965, "lng": 100.355, "rat": 4.6, "cat": "resto", "vec": [0.8, 0.1, 0.7, 0.1, 0.9, 0.1, 0.8, 0.1, 0.4, 0.2] },
    { "nama": "Sate Itam", "addr": "Jl. Pemuda, Padang", "lat": -0.945, "lng": 100.360, "rat": 4.4, "cat": "resto", "vec": [0.6, 0.1, 0.9, 0.1, 0.8, 0.1, 0.7, 0.1, 0.2, 0.2] },
    { "nama": "Bopet Rajawali", "addr": "Jl. Juanda, Padang", "lat": -0.920, "lng": 100.355, "rat": 4.5, "cat": "resto", "vec": [0.7, 0.1, 0.8, 0.1, 0.8, 0.1, 0.7, 0.1, 0.3, 0.2] },
    { "nama": "Rumah Makan Fuja", "addr": "Jl. Samudera, Padang", "lat": -0.950, "lng": 100.350, "rat": 4.6, "cat": "resto", "vec": [0.8, 0.1, 0.5, 0.1, 0.9, 0.1, 0.7, 0.1, 0.3, 0.2] },
    { "nama": "Nasi Kapau Ibu Hj. Anis", "addr": "Jl. Khatib Sulaiman, Padang", "lat": -0.900, "lng": 100.365, "rat": 4.4, "cat": "resto", "vec": [0.6, 0.1, 0.7, 0.1, 0.8, 0.1, 0.7, 0.1, 0.2, 0.2] },
    { "nama": "Es Kim Teng", "addr": "Jl. Pondok, Padang", "lat": -0.960, "lng": 100.360, "rat": 4.5, "cat": "resto", "vec": [0.8, 0.1, 0.7, 0.1, 0.7, 0.1, 0.7, 0.1, 0.4, 0.2] },
    { "nama": "Old Town Coffee", "addr": "Jl. Gereja, Padang", "lat": -0.950, "lng": 100.360, "rat": 4.4, "cat": "kafe", "vec": [0.8, 0.1, 0.6, 0.1, 0.8, 0.1, 0.7, 0.1, 0.6, 0.1] },
    { "nama": "Kopi Teori - Veteran", "addr": "Jl. Veteran, Padang", "lat": -0.925, "lng": 100.355, "rat": 4.5, "cat": "kafe", "vec": [0.8, 0.1, 0.7, 0.1, 0.7, 0.1, 0.8, 0.1, 0.7, 0.1] },
    { "nama": "Sate Manangkabo", "addr": "Jl. Khatib Sulaiman, Padang", "lat": -0.895, "lng": 100.367, "rat": 4.5, "cat": "resto", "vec": [0.7, 0.1, 0.8, 0.1, 0.8, 0.1, 0.7, 0.1, 0.3, 0.2] },
    { "nama": "Bakso Lava", "addr": "Jl. Sawahan, Padang", "lat": -0.930, "lng": 100.370, "rat": 4.3, "cat": "resto", "vec": [0.6, 0.1, 0.9, 0.1, 0.7, 0.1, 0.6, 0.1, 0.2, 0.2] },
    { "nama": "Bika Si Mariana", "addr": "Jl. Hamka, Padang", "lat": -0.880, "lng": 100.350, "rat": 4.6, "cat": "resto", "vec": [0.7, 0.1, 0.9, 0.1, 0.8, 0.1, 0.7, 0.1, 0.2, 0.2] },
    { "nama": "Warung Kopi Nanyo", "addr": "Jl. Pondok, Padang", "lat": -0.962, "lng": 100.362, "rat": 4.5, "cat": "kafe", "vec": [0.8, 0.1, 0.9, 0.1, 0.8, 0.1, 0.7, 0.1, 0.3, 0.2] },
    { "nama": "Sate Syukur Padang", "addr": "Jl. AR Hakim, Padang", "lat": -0.957, "lng": 100.365, "rat": 4.4, "cat": "resto", "vec": [0.7, 0.1, 0.8, 0.1, 0.7, 0.1, 0.7, 0.1, 0.2, 0.2] },
    { "nama": "Ayam Penyet Surabaya", "addr": "Jl. Ahmad Yani, Padang", "lat": -0.943, "lng": 100.368, "rat": 4.3, "cat": "resto", "vec": [0.6, 0.1, 0.9, 0.1, 0.8, 0.1, 0.6, 0.1, 0.2, 0.2] },
    { "nama": "Pizza Hut - Ahmad Yani", "addr": "Jl. Ahmad Yani, Padang", "lat": -0.942, "lng": 100.365, "rat": 4.5, "cat": "resto", "vec": [0.9, 0.1, 0.5, 0.1, 0.8, 0.1, 0.9, 0.1, 0.6, 0.1] },
    { "nama": "McDonald's Padang", "addr": "Jl. Ahmad Yani, Padang", "lat": -0.943, "lng": 100.367, "rat": 4.5, "cat": "resto", "vec": [0.8, 0.1, 0.7, 0.1, 0.8, 0.1, 0.8, 0.1, 0.7, 0.1] },
    { "nama": "KFC Plaza Andalas", "addr": "Plaza Andalas, Padang", "lat": -0.941, "lng": 100.361, "rat": 4.4, "cat": "resto", "vec": [0.7, 0.1, 0.7, 0.1, 0.9, 0.1, 0.7, 0.1, 0.6, 0.1] },
    { "nama": "Solaria Transmart", "addr": "Transmart Padang, Padang", "lat": -0.890, "lng": 100.360, "rat": 4.2, "cat": "resto", "vec": [0.8, 0.1, 0.6, 0.1, 0.8, 0.1, 0.7, 0.1, 0.5, 0.1] },
    { "nama": "Ichiban Sushi", "addr": "Transmart Padang, Padang", "lat": -0.891, "lng": 100.361, "rat": 4.3, "cat": "resto", "vec": [0.8, 0.1, 0.5, 0.1, 0.8, 0.1, 0.8, 0.1, 0.4, 0.2] },
    { "nama": "Bakmi Naga", "addr": "Plaza Andalas, Padang", "lat": -0.942, "lng": 100.362, "rat": 4.1, "cat": "resto", "vec": [0.6, 0.1, 0.8, 0.1, 0.8, 0.1, 0.6, 0.1, 0.3, 0.2] },
    { "nama": "Holland Bakery - Sudirman", "addr": "Jl. Sudirman, Padang", "lat": -0.945, "lng": 100.365, "rat": 4.6, "cat": "toko", "vec": [0.7, 0.1, 0.5, 0.1, 0.8, 0.1, 0.8, 0.1, 0.3, 0.2] },
    { "nama": "J.CO Donuts - Basko", "addr": "Basko Grand Mall, Padang", "lat": -0.880, "lng": 100.355, "rat": 4.5, "cat": "kafe", "vec": [0.8, 0.1, 0.6, 0.1, 0.7, 0.1, 0.8, 0.1, 0.6, 0.1] },
    { "nama": "BreadTalk - Basko", "addr": "Basko Grand Mall, Padang", "lat": -0.881, "lng": 100.356, "rat": 4.4, "cat": "toko", "vec": [0.7, 0.1, 0.6, 0.1, 0.7, 0.1, 0.7, 0.1, 0.3, 0.2] },
    { "nama": "Gramedia Padang", "addr": "Jl. Damar, Padang", "lat": -0.940, "lng": 100.362, "rat": 4.7, "cat": "toko", "vec": [0.8, 0.1, 0.7, 0.1, 0.7, 0.1, 0.9, 0.1, 0.8, 0.1] },
    { "nama": "Minangkabau Library", "addr": "Jl. Diponegoro, Padang", "lat": -0.950, "lng": 100.355, "rat": 4.8, "cat": "perpustakaan", "vec": [0.6, 0.05, 0.95, 0.05, 0.8, 0.1, 0.9, 0.05, 0.95, 0.05] },
    { "nama": "Museum Adityawarman", "addr": "Jl. Diponegoro, Padang", "lat": -0.952, "lng": 100.357, "rat": 4.6, "cat": "wisata", "vec": [0.8, 0.1, 0.9, 0.05, 0.9, 0.1, 0.8, 0.1, 0.5, 0.1] },
]

def inject_v2():
    db = SessionLocal()
    try:
        print(f"Injecting {len(DATA_PADANG)} places...")
        count_added = 0
        for d in DATA_PADANG:
            # Check if exists by name (to avoid duplicates)
            exists = db.query(Tempat).filter(Tempat.nama_tempat == d["nama"]).first()
            if exists:
                # Update existing if needed or skip
                continue
            
            t = Tempat(
                id_tempat=uuid.uuid4(),
                nama_tempat=d["nama"],
                alamat=d["addr"],
                latitude=d["lat"],
                longitude=d["lng"],
                rating_google=d["rat"],
                kategori=d["cat"],
                place_id_google=f"v2_{uuid.uuid4().hex[:10]}"
            )
            db.add(t)
            db.flush() # Sync ID
            
            p = ProfilTempat(
                id_tempat=t.id_tempat,
                vektor_sentimen=d["vec"],
                total_ulasan=20 + (int(d["rat"] * 10) % 50) # Mock ulasan count
            )
            db.add(p)
            count_added += 1
            
        db.commit()
        print(f"Success! Added {count_added} brand new places.")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    inject_v2()
