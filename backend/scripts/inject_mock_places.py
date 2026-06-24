import uuid
from app.db.database import SessionLocal
from app.models.models import Tempat, ProfilTempat

DATA_TEMPAT = [
    {"nama": "Lalito Coffee Bar", "addr": "Jl. S. Parman No.116, Padang", "lat": -0.916, "lng": 100.364, "rat": 4.6},
    {"nama": "Pavilon Coffee", "addr": "Jl. Hayam Wuruk No.30, Padang", "lat": -0.947, "lng": 100.362, "rat": 4.5},
    {"nama": "V Coffee", "addr": "Jl. Raden Saleh No.3, Padang", "lat": -0.925, "lng": 100.360, "rat": 4.7},
    {"nama": "Kopi Janji Jiwa - Ahmad Yani", "addr": "Jl. Ahmad Yani No.12, Padang", "lat": -0.942, "lng": 100.365, "rat": 4.4},
    {"nama": "Weekend Café", "addr": "Jl. Kelenteng No.1, Padang", "lat": -0.963, "lng": 100.368, "rat": 4.5},
    {"nama": "Safari Garden", "addr": "Jl. Nipah No.10, Padang", "lat": -0.960, "lng": 100.355, "rat": 4.6},
    {"nama": "Kubik Koffie", "addr": "Jl. Olo Ladang No.12, Padang", "lat": -0.938, "lng": 100.358, "rat": 4.5},
    {"nama": "Kopi Batigo", "addr": "Jl. KH. Ahmad Dahlan No.19, Padang", "lat": -0.920, "lng": 100.362, "rat": 4.4},
    {"nama": "Mula Coffee", "addr": "Jl. Dr. Sutomo No.1, Padang", "lat": -0.928, "lng": 100.375, "rat": 4.6},
    {"nama": "Cafe Merdeka", "addr": "Jl. Diponegoro No.5, Padang", "lat": -0.952, "lng": 100.358, "rat": 4.3},
    {"nama": "Hau's Tea", "addr": "Jl. Hos Cokroaminoto No.45, Padang", "lat": -0.955, "lng": 100.365, "rat": 4.5},
    {"nama": "EL'S Coffee", "addr": "Jl. Ahmad Yani No.30, Padang", "lat": -0.942, "lng": 100.367, "rat": 4.4},
    {"nama": "Kyoto Coffee", "addr": "Jl. Belakang Olo, Padang", "lat": -0.935, "lng": 100.362, "rat": 4.5},
    {"nama": "Warunk Upnormal Padang", "addr": "Jl. Ahmad Yani No.18, Padang", "lat": -0.943, "lng": 100.366, "rat": 4.2},
    {"nama": "Foresthree Coffee", "addr": "Jl. Sawahan No.20, Padang", "lat": -0.930, "lng": 100.370, "rat": 4.4},
    {"nama": "Rimbun Espresso & Brew Bar", "addr": "Jl. Kurao Pagang, Padang", "lat": -0.880, "lng": 100.380, "rat": 4.7},
    {"nama": "Coffee Theory", "addr": "Jl. Veteran No.60, Padang", "lat": -0.925, "lng": 100.355, "rat": 4.6},
    {"nama": "Hideout Coffee", "addr": "Jl. Hamka No.45, Padang", "lat": -0.890, "lng": 100.350, "rat": 4.5},
    {"nama": "G-Spot Coffee", "addr": "Jl. Gajah Mada No.10, Padang", "lat": -0.900, "lng": 100.370, "rat": 4.4},
    {"nama": "Suko Kopi", "addr": "Jl. Khatib Sulaiman, Padang", "lat": -0.910, "lng": 100.360, "rat": 4.5}
]

def inject_mock_data():
    db = SessionLocal()
    try:
        print(f"Injecting {len(DATA_TEMPAT)} places...")
        for d in DATA_TEMPAT:
            # Check if exists
            exists = db.query(Tempat).filter(Tempat.nama_tempat == d["nama"]).first()
            if exists:
                continue
            
            t = Tempat(
                id_tempat=uuid.uuid4(),
                nama_tempat=d["nama"],
                alamat=d["addr"],
                latitude=d["lat"],
                longitude=d["lng"],
                rating_google=d["rat"],
                kategori="kafe",
                place_id_google=f"mock_{uuid.uuid4().hex[:10]}"
            )
            db.add(t)
            db.flush() # Get ID
            
            # Add Profile with random/generic high quality vector
            p = ProfilTempat(
                id_tempat=t.id_tempat,
                vektor_sentimen=[0.8, 0.1, 0.7, 0.1, 0.6, 0.1, 0.8, 0.1, 0.7, 0.1],
                total_ulasan=10
            )
            db.add(p)
            
        db.commit()
        print("Success!")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    inject_mock_data()
