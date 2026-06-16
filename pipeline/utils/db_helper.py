import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    """Buat koneksi langsung ke PostgreSQL."""
    return psycopg2.connect(os.getenv("DATABASE_URL"))

def get_semua_tempat():
    """
    Ambil semua place_id_google dari tabel tempat.
    Digunakan oleh scraper untuk tahu tempat mana yang harus diambil ulasannya.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id_tempat, place_id_google, nama_tempat 
        FROM tempat 
        WHERE place_id_google IS NOT NULL
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {"id_tempat": str(r[0]), "place_id_google": r[1], "nama_tempat": r[2]}
        for r in rows
    ]

def simpan_tempat_baru(data: dict):
    """
    Insert tempat baru dari Google Places ke database.
    Gunakan ON CONFLICT untuk hindari duplikasi.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO tempat 
            (nama_tempat, alamat, latitude, longitude, 
             kategori, rating_google, place_id_google, foto_url)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (place_id_google) DO UPDATE SET
            rating_google = EXCLUDED.rating_google,
            updated_at = NOW()
        RETURNING id_tempat
    """, (
        data.get("nama_tempat"),
        data.get("alamat"),
        data.get("latitude"),
        data.get("longitude"),
        data.get("kategori", "kafe"),
        data.get("rating_google"),
        data.get("place_id_google"),
        data.get("foto_url")
    ))
    id_tempat = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return str(id_tempat)

def simpan_ulasan(data: dict):
    """
    Insert ulasan dari Kafka consumer ke database.
    Skip jika review_id_google sudah ada (duplikasi).
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO ulasan 
                (id_tempat, teks_ulasan, rating, author_name, review_id_google)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (review_id_google) DO NOTHING
            RETURNING id_ulasan
        """, (
            data["id_tempat"],
            data["teks_ulasan"],
            data.get("rating"),
            data.get("author_name"),
            data.get("review_id_google")
        ))
        result = cur.fetchone()
        conn.commit()
        return str(result[0]) if result else None
    except Exception as e:
        conn.rollback()
        print(f"[DB ERROR] Gagal simpan ulasan: {e}")
        return None
    finally:
        cur.close()
        conn.close()