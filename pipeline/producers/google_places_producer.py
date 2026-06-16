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
    "kafe di Padang Sumatera Barat",
    "kedai kopi di Padang",
    "tempat nongkrong Padang",
    "coworking space Padang",
    "restoran casual Padang",
]

def init_producer():
    """Inisialisasi Kafka producer dengan serialisasi JSON."""
    return KafkaProducer(
        bootstrap_servers=KAFKA_SERVERS,
        value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode("utf-8"),
        key_serializer=lambda k: k.encode("utf-8") if k else None,
        retries=3
    )

def cari_tempat_google(query: str) -> list:
    """
    Cari tempat menggunakan Google Places Text Search API.
    Dokumentasi: https://developers.google.com/maps/documentation/places/web-service/text-search
    """
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": query,
        "key": GOOGLE_API_KEY,
        "language": "id",
        "region": "id"
    }
    
    response = requests.get(url, params=params, timeout=10)
    data = response.json()
    
    if data.get("status") != "OK":
        print(f"[GOOGLE API] Status: {data.get('status')} untuk query: {query}")
        return []
    
    hasil = []
    for place in data.get("results", []):
        # Ambil foto pertama jika ada
        foto_url = None
        if place.get("photos"):
            foto_ref = place["photos"][0]["photo_reference"]
            foto_url = (
                f"https://maps.googleapis.com/maps/api/place/photo"
                f"?maxwidth=800&photo_reference={foto_ref}&key={GOOGLE_API_KEY}"
            )
        
        hasil.append({
            "place_id_google": place.get("place_id"),
            "nama_tempat": place.get("name"),
            "alamat": place.get("formatted_address"),
            "latitude": place["geometry"]["location"]["lat"],
            "longitude": place["geometry"]["location"]["lng"],
            "rating_google": place.get("rating"),
            "kategori": "kafe",
            "foto_url": foto_url,
        })
    
    return hasil

def ambil_ulasan_tempat(place_id: str, id_tempat: str) -> list:
    """
    Ambil detail dan ulasan tempat menggunakan Google Places Details API.
    Mengembalikan list pesan untuk dikirim ke Kafka.
    """
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "name,reviews,rating",
        "key": GOOGLE_API_KEY,
        "language": "id",
        "reviews_sort": "newest"
    }
    
    response = requests.get(url, params=params, timeout=10)
    data = response.json()
    
    if data.get("status") != "OK":
        print(f"[GOOGLE API] Detail gagal untuk {place_id}: {data.get('status')}")
        return []
    
    pesan_list = []
    reviews = data.get("result", {}).get("reviews", [])
    
    for review in reviews:
        # Buat unique ID untuk hindari duplikasi
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
    Fungsi utama yang dipanggil oleh Airflow DAG.
    Alur: Search tempat → Simpan ke DB → Ambil ulasan → Kirim ke Kafka
    """
    print("[PIPELINE] Memulai scraping Google Places...")
    producer = init_producer()
    
    total_tempat = 0
    total_ulasan = 0
    
    # STEP 1: Cari dan simpan tempat baru
    for query in SEARCH_QUERIES:
        print(f"[SEARCH] Query: {query}")
        tempat_list = cari_tempat_google(query)
        
        for tempat_data in tempat_list:
            id_tempat = simpan_tempat_baru(tempat_data)
            if id_tempat:
                total_tempat += 1
        
        time.sleep(1)  # hindari rate limit
    
    print(f"[PIPELINE] Total tempat diproses: {total_tempat}")
    
    # STEP 2: Ambil ulasan untuk setiap tempat yang sudah ada di DB
    semua_tempat = get_semua_tempat()
    
    for tempat in semua_tempat:
        print(f"[SCRAPE] Ambil ulasan: {tempat['nama_tempat']}")
        
        ulasan_list = ambil_ulasan_tempat(
            tempat["place_id_google"],
            tempat["id_tempat"]
        )
        
        # STEP 3: Kirim setiap ulasan ke Kafka topic
        for ulasan in ulasan_list:
            producer.send(
                KAFKA_TOPIC,
                key=tempat["id_tempat"],
                value=ulasan
            )
            total_ulasan += 1
        
        time.sleep(0.5)  # jeda antar request
    
    producer.flush()
    producer.close()
    
    print(f"[PIPELINE] Selesai. Total ulasan dikirim ke Kafka: {total_ulasan}")
    return {"total_tempat": total_tempat, "total_ulasan": total_ulasan}

if __name__ == "__main__":
    jalankan_scraping()