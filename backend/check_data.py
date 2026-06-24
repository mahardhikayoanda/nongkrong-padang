import os
from sqlalchemy import create_url
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/nongkrong_padang")

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    # Check tempat
    res_tempat = conn.execute(text("SELECT count(*) FROM tempat")).scalar()
    print(f"Total Tempat: {res_tempat}")
    
    # Check profil
    res_profil = conn.execute(text("SELECT count(*) FROM profil_tempat")).scalar()
    print(f"Total Profil Tempat: {res_profil}")
    
    # Samples
    print("\nSample Tempat:")
    samples = conn.execute(text("SELECT nama_tempat, kategori FROM tempat LIMIT 10")).fetchall()
    for s in samples:
        print(f"- {s[0]} ({s[1]})")
        
    # Check categories
    print("\nKategori yang ada:")
    cats = conn.execute(text("SELECT kategori, count(*) FROM tempat GROUP BY kategori")).fetchall()
    for c in cats:
        print(f"- {c[0]}: {c[1]}")
