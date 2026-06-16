from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import sys
import os

# Path ke folder pipeline
PIPELINE_DIR = "/opt/airflow/dags/../"
sys.path.insert(0, PIPELINE_DIR)

# Default args untuk semua task dalam DAG
default_args = {
    "owner": "mahardhika",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

def task_scraping_google(**context):
    """Task 1: Ambil data dari Google Places API → Kafka."""
    from producers.google_places_producer import jalankan_scraping
    hasil = jalankan_scraping()
    
    # Push hasil ke XCom agar bisa diakses task berikutnya
    context["ti"].xcom_push(key="hasil_scraping", value=hasil)
    print(f"[DAG] Scraping selesai: {hasil}")
    return hasil

def task_consume_kafka(**context):
    """Task 2: Consume Kafka → simpan ke PostgreSQL."""
    from consumers.review_consumer import jalankan_consumer
    hasil = jalankan_consumer()
    
    context["ti"].xcom_push(key="hasil_consume", value=hasil)
    print(f"[DAG] Consumer selesai: {hasil}")
    return hasil

def task_update_profil_tempat(**context):
    """
    Task 3: Hitung ulang vektor aspek-sentimen semua tempat.
    Dijalankan SETELAH ulasan baru tersimpan.
    (Fase ini akan diisi setelah model ABSA selesai di Fase 4)
    """
    import psycopg2
    import os
    
    conn = psycopg2.connect(os.getenv(
        "AIRFLOW__DATABASE__SQL_ALCHEMY_CONN",
        "postgresql://nongkrong_user:nongkrong_pass@postgres/nongkrong_db"
    ).replace("postgresql+psycopg2", "postgresql"))
    
    cur = conn.cursor()
    
    # Untuk sekarang: update timestamp profil agar tahu kapan terakhir diperbarui
    cur.execute("""
        INSERT INTO profil_tempat (id_tempat, vektor_sentimen, total_ulasan)
        SELECT 
            t.id_tempat,
            ARRAY[0,0,0,0,0,0,0,0,0,0]::float[],
            COUNT(u.id_ulasan)
        FROM tempat t
        LEFT JOIN ulasan u ON t.id_tempat = u.id_tempat
        GROUP BY t.id_tempat
        ON CONFLICT (id_tempat) DO UPDATE SET
            total_ulasan = EXCLUDED.total_ulasan,
            updated_at = NOW()
    """)
    
    conn.commit()
    cur.close()
    conn.close()
    
    print("[DAG] Profil tempat diperbarui (vektor akan diisi setelah ABSA)")

# ─── DEFINISI DAG ────────────────────────────────────────────────────────────
with DAG(
    dag_id="scraping_harian_google_places",
    description="Scraping ulasan harian dari Google Maps via Google Places API",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule_interval="0 2 * * *",   # Setiap hari pukul 02:00 WIB
    catchup=False,
    tags=["scraping", "pipeline", "production"],
) as dag:

    # TASK 1 — Scraping Google Places API
    t1_scraping = PythonOperator(
        task_id="scraping_google_places",
        python_callable=task_scraping_google,
        provide_context=True,
    )

    # TASK 2 — Consume Kafka dan simpan ke DB
    t2_consume = PythonOperator(
        task_id="consume_kafka_simpan_db",
        python_callable=task_consume_kafka,
        provide_context=True,
    )

    # TASK 3 — Update profil tempat
    t3_update_profil = PythonOperator(
        task_id="update_profil_tempat",
        python_callable=task_update_profil_tempat,
        provide_context=True,
    )

    # Urutan eksekusi: t1 → t2 → t3
    t1_scraping >> t2_consume >> t3_update_profil