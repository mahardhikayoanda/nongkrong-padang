import os
import json
import sys
from kafka import KafkaConsumer
from dotenv import load_dotenv

# Tambahkan parent folder ke path agar bisa import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db_helper import simpan_ulasan
from utils.text_cleaner import bersihkan_teks, is_teks_valid

load_dotenv()

KAFKA_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC   = os.getenv("KAFKA_TOPIC_REVIEWS", "reviews")
KAFKA_GROUP   = "absa-consumer-group"

def proses_pesan(pesan: dict) -> dict | None:
    """
    Preprocessing pesan ulasan sebelum disimpan ke DB.
    Return None jika teks tidak valid.
    """
    teks_asli   = pesan.get("teks_ulasan", "")
    teks_bersih = bersihkan_teks(teks_asli)
    
    if not is_teks_valid(teks_bersih):
        print(f"[SKIP] Teks terlalu pendek atau kosong: '{teks_asli[:50]}'")
        return None
    
    pesan["teks_ulasan"] = teks_bersih
    return pesan

def jalankan_consumer():
    """
    Consumer utama: baca dari Kafka → preprocessing → simpan ke PostgreSQL.
    Akan terus berjalan sampai di-stop manual.
    """
    print(f"[CONSUMER] Mendengarkan topic '{KAFKA_TOPIC}'...")
    
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_SERVERS,
        group_id=KAFKA_GROUP,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        consumer_timeout_ms=30000  # stop otomatis jika 30 detik tidak ada pesan
    )
    
    total_diproses = 0
    total_disimpan = 0
    total_skip     = 0
    
    for msg in consumer:
        pesan = msg.value
        print(f"[CONSUME] Ulasan dari tempat: {pesan.get('id_tempat', '?')[:8]}...")
        
        # Preprocessing
        pesan_bersih = proses_pesan(pesan)
        
        if pesan_bersih is None:
            total_skip += 1
            total_diproses += 1
            continue
        
        # Simpan ke PostgreSQL
        id_ulasan = simpan_ulasan(pesan_bersih)
        
        if id_ulasan:
            print(f"[SAVED] Ulasan tersimpan: {id_ulasan[:8]}...")
            total_disimpan += 1
        else:
            print(f"[SKIP] Duplikasi atau error, ulasan tidak disimpan")
        
        total_diproses += 1
    
    consumer.close()
    
    print(f"""
[CONSUMER] Selesai.
  - Total diproses : {total_diproses}
  - Tersimpan      : {total_disimpan}
  - Diskip         : {total_skip}
    """)
    
    return {
        "diproses": total_diproses,
        "disimpan": total_disimpan,
        "skip": total_skip
    }

if __name__ == "__main__":
    jalankan_consumer()