"""
Script untuk menjalankan inferensi ABSA pada semua ulasan
dan memperbarui vektor profil_tempat di PostgreSQL.

Dipanggil oleh Airflow DAG setelah scraping selesai.
"""

import os
import sys
import psycopg2
import numpy as np
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from inference.absa_pipeline import ABSAPipeline

load_dotenv()

def get_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

def ambil_ulasan_belum_dianalisis(conn) -> list:
    """Ambil ulasan yang belum ada di tabel aspek_sentimen."""
    cur = conn.cursor()
    cur.execute("""
        SELECT u.id_ulasan, u.id_tempat, u.teks_ulasan
        FROM ulasan u
        LEFT JOIN aspek_sentimen a ON u.id_ulasan = a.id_ulasan
        WHERE a.id_ulasan IS NULL
        LIMIT 100
    """)
    rows = cur.fetchall()
    cur.close()
    return [
        {"id_ulasan": str(r[0]), "id_tempat": str(r[1]), "teks": r[2]}
        for r in rows
    ]

def simpan_hasil_absa(conn, id_ulasan: str, hasil: list):
    """Simpan triplet ABSA ke tabel aspek_sentimen."""
    cur = conn.cursor()
    for item in hasil:
        cur.execute("""
            INSERT INTO aspek_sentimen 
                (id_ulasan, kategori_aspek, polaritas, skor_confidence, term_aspek)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            id_ulasan,
            item["kategori"],
            item["polaritas"],
            item["confidence"],
            item["term"]
        ))
    conn.commit()
    cur.close()

def hitung_vektor_tempat(conn, id_tempat: str) -> list:
    """
    Hitung vektor sentimen 10-dimensi dari seluruh aspek_sentimen tempat.
    Formula: skor_aspek = (Σ positif - Σ negatif) / total_ulasan_aspek
    Range: [-1.0, +1.0] per dimensi
    """
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            a.kategori_aspek,
            a.polaritas,
            COUNT(*) as jumlah
        FROM aspek_sentimen a
        JOIN ulasan u ON a.id_ulasan = u.id_ulasan
        WHERE u.id_tempat = %s::uuid
        GROUP BY a.kategori_aspek, a.polaritas
    """, (id_tempat,))
    
    rows = cur.fetchall()
    cur.close()
    
    # Struktur: {kategori: {positif: N, negatif: N, netral: N}}
    aspek_count = {
        k: {"positif": 0, "negatif": 0, "netral": 0}
        for k in ["suasana", "harga", "lokasi", "pelayanan", "fasilitas"]
    }
    
    for kategori, polaritas, jumlah in rows:
        if kategori in aspek_count:
            aspek_count[kategori][polaritas] = jumlah
    
    # Bangun vektor 10 dimensi
    # [suasana+, suasana-, harga+, harga-, lokasi+, lokasi-,
    #  pelayanan+, pelayanan-, fasilitas+, fasilitas-]
    vektor = []
    for aspek in ["suasana", "harga", "lokasi", "pelayanan", "fasilitas"]:
        pos = aspek_count[aspek]["positif"]
        neg = aspek_count[aspek]["negatif"]
        total = pos + neg + aspek_count[aspek]["netral"]
        
        if total == 0:
            vektor.extend([0.0, 0.0])
        else:
            vektor.append(round(pos / total, 4))
            vektor.append(round(neg / total, 4))
    
    return vektor

def update_profil_tempat(conn, id_tempat: str, vektor: list):
    """Update vektor sentimen di tabel profil_tempat."""
    cur = conn.cursor()
    cur.execute("""
        UPDATE profil_tempat
        SET vektor_sentimen = %s::float[],
            updated_at = NOW()
        WHERE id_tempat = %s::uuid
    """, (vektor, id_tempat))
    conn.commit()
    cur.close()

def jalankan_absa_update():
    """Fungsi utama — dipanggil oleh Airflow DAG task_absa."""
    print("[ABSA UPDATE] Memuat model...")
    pipeline = ABSAPipeline()
    
    conn = get_connection()
    
    # Step 1: Ambil ulasan yang belum dianalisis
    ulasan_list = ambil_ulasan_belum_dianalisis(conn)
    print(f"[ABSA UPDATE] {len(ulasan_list)} ulasan akan dianalisis")
    
    if not ulasan_list:
        print("[ABSA UPDATE] Tidak ada ulasan baru. Skip.")
        conn.close()
        return
    
    # Step 2: Jalankan ABSA per ulasan
    tempat_perlu_update = set()
    
    for i, ulasan in enumerate(ulasan_list):
        print(f"  [{i+1}/{len(ulasan_list)}] Analisis: '{ulasan['teks'][:50]}...'")
        
        hasil = pipeline.analisis(ulasan["teks"])
        
        if hasil:
            simpan_hasil_absa(conn, ulasan["id_ulasan"], hasil)
            tempat_perlu_update.add(ulasan["id_tempat"])
            print(f"    → {len(hasil)} aspek terdeteksi")
        else:
            print(f"    → Tidak ada aspek terdeteksi")
    
    # Step 3: Hitung ulang vektor untuk tempat yang ulasannya berubah
    print(f"\n[ABSA UPDATE] Update vektor untuk {len(tempat_perlu_update)} tempat...")
    
    for id_tempat in tempat_perlu_update:
        vektor = hitung_vektor_tempat(conn, id_tempat)
        update_profil_tempat(conn, id_tempat, vektor)
        print(f"  ✅ Tempat {id_tempat[:8]}... → vektor: {[round(v,2) for v in vektor]}")
    
    conn.close()
    print("\n[ABSA UPDATE] ✅ Selesai!")

if __name__ == "__main__":
    jalankan_absa_update()