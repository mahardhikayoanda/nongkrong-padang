import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "nongkrong_db"),
        user=os.getenv("DB_USER", "nongkrong_user"),
        password=os.getenv("DB_PASS", "nongkrong_pass")
    )

def get_ulasan_belum_dianalisis():
    """Mengambil ulasan yang belum masuk ke tabel aspek_sentimen."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    # Sesuaikan query dengan nama kolom di tabel Anda
    query = """
        SELECT u.id_ulasan, u.teks_ulasan 
        FROM ulasan u
        LEFT JOIN aspek_sentimen a ON u.id_ulasan = a.id_ulasan
        WHERE a.id_ulasan IS NULL;
    """
    cur.execute(query)
    hasil = cur.fetchall()
    cur.close()
    conn.close()
    return hasil

def simpan_hasil_sentimen(id_ulasan, data):
    """Menyimpan hasil analisis ABSA ke tabel aspek_sentimen."""
    conn = get_db_connection()
    cur = conn.cursor()
    # Pastikan urutan dan nama kolom sesuai dengan skema
    query = """
        INSERT INTO aspek_sentimen (id_ulasan, term_aspek, kategori_aspek, polaritas, skor_confidence)
        VALUES (%s, %s, %s, %s, %s)
    """
    # Sesuaikan dictionary key dengan output dari ABSAPipeline Anda
    cur.execute(query, (
        id_ulasan, 
        data['term'], 
        data['kategori'], 
        data['polaritas'], 
        data['confidence']
    ))
    conn.commit()
    cur.close()
    conn.close()