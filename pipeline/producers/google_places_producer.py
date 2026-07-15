import os
import sys

# --- TAMBAHKAN BLOK INI ---
# Mengarahkan Python agar mengenali folder 'pipeline' sebagai root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
import time
from kafka import KafkaProducer
from dotenv import load_dotenv
from apify_client import ApifyClient
from utils.db_helper import simpan_tempat_baru, get_semua_tempat

load_dotenv()

APIFY_TOKEN = os.getenv("APIFY_API_TOKEN")
KAFKA_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC_REVIEWS", "reviews")

# Inisialisasi Apify Client
apify_client = ApifyClient(APIFY_TOKEN)

# Kata kunci pencarian (bisa disesuaikan)
SEARCH_QUERIES = [
    "kafe di Padang",
    "tempat nongkrong di Padang",
    "coffee shop Padang"
]

def init_producer():
    """Inisialisasi Kafka producer dengan serialisasi JSON."""
    return KafkaProducer(
        bootstrap_servers=KAFKA_SERVERS,
        value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode("utf-8"),
        key_serializer=lambda k: k.encode("utf-8") if k else None,
        retries=3
    )

def map_kategori(kategori_apify: str) -> str:
    """Menerjemahkan kategori dari Apify ke format internal kita."""
    if not kategori_apify:
        return "kafe"
    
    kategori_apify = kategori_apify.lower()
    if "bakery" in kategori_apify: return "bakery"
    if "restaurant" in kategori_apify or "restoran" in kategori_apify: return "restoran"
    if "bar" in kategori_apify or "bistro" in kategori_apify: return "bistro"
    
    return "kafe"

def jalankan_scraping_apify():
    """
    Menjalankan scraper menggunakan Apify Actor Google Maps Scraper,
    Menyimpan tempat ke DB, dan mengirim ulasan ke Kafka.
    """
    print("[PIPELINE] Memulai scraping menggunakan Apify...")
    producer = init_producer()
    
    total_tempat_baru = 0
    total_ulasan = 0

    # Konfigurasi parameter untuk Actor Apify (compass/google-maps-scraper)
    # Anda bisa menaikkan limit maxCrawledPlaces dan maxReviews nanti
    run_input = {
        "searchStringsArray": SEARCH_QUERIES,
        "locationQuery": "Padang, West Sumatra",
        "language": "id",
        "maxCrawledPlacesPerSearch": 10, # Batasi 10 tempat per query agar proses cepat saat testing
        "maxReviews": 15,               # Ambil 15 review terbaru per tempat
        "maxImages": 1,
    }

    print(f"[APIFY] Memanggil Actor di cloud (Ini mungkin memakan waktu beberapa menit)...")
    
    # Jalankan Actor di server Apify
    run = apify_client.actor("compass/crawler-google-places").call(run_input=run_input)
    
    # Ambil hasil scraping dari Apify Dataset
    # Ambil hasil scraping dari Apify Dataset (Kompatibel dengan library versi terbaru)
    try:
        dataset_id = run["defaultDatasetId"]
    except TypeError:
        # Jika formatnya adalah Object
        dataset_id = getattr(run, "defaultDatasetId", getattr(run, "default_dataset_id", None))
        
    dataset_items = apify_client.dataset(dataset_id).list_items().items
    print(f"[APIFY] Selesai! Mendapatkan {len(dataset_items)} tempat.")

    for item in dataset_items:
        # 1. Petakan (Mapping) data tempat sesuai format db_helper.py
        tempat_data = {
            "place_id_google": item.get("placeId"),
            "nama_tempat": item.get("title"),
            "alamat": item.get("address", "Padang"),
            "latitude": item.get("location", {}).get("lat"),
            "longitude": item.get("location", {}).get("lng"),
            "rating_google": item.get("totalScore"),
            "kategori": map_kategori(item.get("categoryName")),
            "foto_url": item.get("imageUrl")
        }

        # Simpan ke PostgreSQL
        id_tempat_internal = simpan_tempat_baru(tempat_data)
        if id_tempat_internal:
            total_tempat_baru += 1

        # 2. Iterasi array reviews dari Apify dan kirim ke Kafka
        reviews = item.get("reviews", [])
        for rev in reviews:
            # PENTING: ABSA Pipeline Anda butuh teks untuk dianalisis
            if not rev.get("text"):
                continue # Abaikan ulasan yang cuma ngasih bintang tanpa teks
                
            review_id = rev.get("reviewId") or f"{item.get('placeId')}_{rev.get('name')}"
            
            ulasan_data = {
                "id_tempat": str(id_tempat_internal),
                "place_id_google": item.get("placeId"),
                "teks_ulasan": rev.get("text", ""),
                "rating": rev.get("stars"),
                "author_name": rev.get("name"),
                "review_id_google": review_id,
                "timestamp": rev.get("publishedAtDate")
            }

            # Kirim ke Kafka
            producer.send(
                KAFKA_TOPIC,
                key=str(id_tempat_internal),
                value=ulasan_data
            )
            total_ulasan += 1
            
    producer.flush()
    producer.close()
    
    print(f"\n[SUMMARY] Selesai.")
    print(f" - Tempat baru/diperbarui di DB: {total_tempat_baru}")
    print(f" - Ulasan dikirim ke Kafka: {total_ulasan}")

if __name__ == "__main__":
    jalankan_scraping_apify()