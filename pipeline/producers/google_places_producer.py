import os
import json
import time
import requests
from kafka import KafkaProducer
from dotenv import load_dotenv
from utils.db_helper import get_semua_tempat, simpan_tempat_baru

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
KAFKA_SERVERS  = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC    = os.getenv("KAFKA_TOPIC_REVIEWS", "reviews")

# Daftar query pencarian untuk tempat nongkrong di Padang
SEARCH_QUERIES = [
    "kafe",
    "kedai kopi",
    "tempat nongkrong",
    "coworking space",
    "restoran casual",
    "bakery",
    "bistro",
    "gelato",
    "warung kopi modern"
]

# Titik pusat wilayah di Padang untuk pencarian berbasis lokasi
PADANG_CENTERS = [
    {"nama": "Pusat Kota", "loc": "-0.947,100.373"},
    {"nama": "Padang Utara", "loc": "-0.916,100.364"},
    {"nama": "Padang Selatan", "loc": "-0.963,100.362"},
    {"nama": "Tabing / Air Tawar", "loc": "-0.887,100.354"},
    {"nama": "Bypass / Pauh", "loc": "-0.925,100.410"},
]

def init_producer():
    """Inisialisasi Kafka producer dengan serialisasi JSON."""
    return KafkaProducer(
        bootstrap_servers=KAFKA_SERVERS,
        value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode("utf-8"),
        key_serializer=lambda k: k.encode("utf-8") if k else None,
        retries=3
    )

def map_kategori(types: list) -> str:
    """Mapping tipe dari Google Places ke kategori internal."""
    if not types:
        return "kafe"
    
    mapping = {
        "bakery": "bakery",
        "cafe": "kafe",
        "coffee_shop": "kafe",
        "restaurant": "restoran",
        "bar": "bistro",
        "meal_takeaway": "restoran",
    }
    
    for t in types:
        if t in mapping:
            return mapping[t]
    return "kafe"

def cari_tempat_google(query: str, location: str = None, radius: int = 5000) -> list:
    """
    Cari tempat menggunakan Google Places Text Search API dengan dukungan paginasi.
    """
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    hasil_total = []
    next_page_token = None
    
    while True:
        params = {
            "query": query,
            "key": GOOGLE_API_KEY,
            "language": "id",
            "region": "id"
        }
        
        if location:
            params["location"] = location
            params["radius"] = radius
        
        if next_page_token:
            params["pagetoken"] = next_page_token
            # Google butuh jeda singkat sebelum pagetoken menjadi valid
            time.sleep(2)
        
        response = requests.get(url, params=params, timeout=15)
        data = response.json()
        
        if data.get("status") not in ["OK", "ZERO_RESULTS"]:
            print(f"[GOOGLE API] Error: {data.get('status')} untuk query: {query}")
            break
            
        results = data.get("results", [])
        for place in results:
            foto_url = None
            if place.get("photos"):
                foto_ref = place["photos"][0]["photo_reference"]
                foto_url = (
                    f"https://maps.googleapis.com/maps/api/place/photo"
                    f"?maxwidth=800&photo_reference={foto_ref}&key={GOOGLE_API_KEY}"
                )
            
            hasil_total.append({
                "place_id_google": place.get("place_id"),
                "nama_tempat": place.get("name"),
                "alamat": place.get("formatted_address"),
                "latitude": place["geometry"]["location"]["lat"],
                "longitude": place["geometry"]["location"]["lng"],
                "rating_google": place.get("rating"),
                "kategori": map_kategori(place.get("types", [])),
                "foto_url": foto_url,
            })
        
        next_page_token = data.get("next_page_token")
        if not next_page_token:
            break
            
        print(f"[PAGINATION] Mengambil halaman berikutnya untuk: {query}...")
        
    return hasil_total

def ambil_ulasan_tempat(place_id: str, id_tempat: str) -> list:
    """
    Ambil detail dan ulasan tempat menggunakan Google Places Details API.
    """
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "name,reviews,rating",
        "key": GOOGLE_API_KEY,
        "language": "id",
        "reviews_sort": "newest"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
    except Exception as e:
        print(f"[ERROR] Request failed for {place_id}: {e}")
        return []
    
    if data.get("status") != "OK":
        print(f"[GOOGLE API] Detail gagal untuk {place_id}: {data.get('status')}")
        return []
    
    pesan_list = []
    reviews = data.get("result", {}).get("reviews", [])
    
    for review in reviews:
        review_id = f"{place_id}_{review.get('time', '')}_{review.get('author_name','')[:10]}"
        pesan_list.append({
            "id_tempat": id_tempat,
            "place_id_google": place_id,
            "teks_ulasan": review.get("text", ""),
            "rating": review.get("rating"),
            "author_name": review.get("author_name"),
            "review_id_google": review_id,
            "timestamp": review.get("time")
        })
    
    return pesan_list

def jalankan_scraping():
    """
    Fungsi utama: Iterasi wilayah → Search places → Simpan → Ambil ulasan → Kafka.
    """
    print("[PIPELINE] Memulai scraping Google Places dengan cakupan diperluas...")
    producer = init_producer()
    
    total_tempat_baru = 0
    total_ulasan = 0
    diproses_place_ids = set() # Hindari proses ulang dalam satu running
    
    # STEP 1: Crawl berdasarkan wilayah dan query
    for center in PADANG_CENTERS:
        print(f"\n[AREA] Memulai pencarian di wilayah: {center['nama']}")
        
        for q in SEARCH_QUERIES:
            print(f"[SEARCH] Query: '{q}'")
            tempat_list = cari_tempat_google(q, location=center['loc'], radius=3000)
            
            for tempat_data in tempat_list:
                pid = tempat_data["place_id_google"]
                if pid in diproses_place_ids:
                    continue
                
                id_tempat = simpan_tempat_baru(tempat_data)
                if id_tempat:
                    total_tempat_baru += 1
                    diproses_place_ids.add(pid)
            
            time.sleep(1) # Jeda antar query
            
    print(f"\n[PIPELINE] Scraping selesai. Total tempat unik diproses: {len(diproses_place_ids)}")
    
    # STEP 2: Ambil ulasan terbaru untuk tempat-tempat di DB
    semua_tempat = get_semua_tempat()
    
    for tempat in semua_tempat:
        print(f"[SCRAPE] Update ulasan: {tempat['nama_tempat']}")
        ulasan_list = ambil_ulasan_tempat(tempat["place_id_google"], tempat["id_tempat"])
        
        for ulasan in ulasan_list:
            producer.send(
                KAFKA_TOPIC,
                key=tempat["id_tempat"],
                value=ulasan
            )
            total_ulasan += 1
        
        time.sleep(0.5)
    
    producer.flush()
    producer.close()
    
    print(f"\n[SUMMARY] Selesai.")
    print(f" - Tempat baru/diperbarui: {total_tempat_baru}")
    print(f" - Ulasan dikirim ke Kafka: {total_ulasan}")
    
    return {"total_tempat": total_tempat_baru, "total_ulasan": total_ulasan}

if __name__ == "__main__":
    jalankan_scraping()
