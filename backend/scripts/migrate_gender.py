import sys
import os
from sqlalchemy import text
from app.db.database import SessionLocal

def migrate():
    db = SessionLocal()
    try:
        print("Mengecek kolom 'jenis_kelamin' di tabel 'users'...")
        db.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS jenis_kelamin VARCHAR(20)"))
        db.commit()
        print("Migrasi berhasil: Kolom 'jenis_kelamin' sudah ada.")
    except Exception as e:
        print(f"Error saat migrasi: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
