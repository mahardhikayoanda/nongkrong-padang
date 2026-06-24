import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Tambahkan project root ke sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal, engine

def dump_users():
    print("--- DUMPING USERS ---")
    db = SessionLocal()
    try:
        result = db.execute(text("SELECT id_user, nama, email, role FROM users")).fetchall()
        for row in result:
            print(f"ID: {row[0]} | Nama: {row[1]} | Email: {row[2]} | Role: {row[3]}")
    except Exception as e:
        print(f"DATABASE ERROR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    dump_users()
