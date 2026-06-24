import psycopg2
try:
    print("Connecting to DB...")
    conn = psycopg2.connect(
        database="nongkrong_db",
        user="nongkrong_user",
        password="nongkrong_pass",
        host="127.0.0.1",
        port=5432
    )
    conn.autocommit = True
    cur = conn.cursor()
    print("Running ALTER TABLE...")
    cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS jenis_kelamin VARCHAR(20);")
    print("SUCCESS: Kolom 'jenis_kelamin' berhasil ditambahkan (atau sudah ada).")
    cur.close()
    conn.close()
except Exception as e:
    print(f"FAILED: {e}")
