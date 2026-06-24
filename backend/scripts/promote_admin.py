import sys
import os
import argparse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Tambahkan project root ke sys.path agar bisa import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.models import User
from app.db.database import SessionLocal

def promote_user(email: str):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"Error: User dengan email '{email}' tidak ditemukan.")
            return
        
        user.role = "admin"
        db.commit()
        print(f"Sukses: User '{user.nama}' ({email}) sekarang memiliki role: {user.role}")
    except Exception as e:
        print(f"Error: Terjadi kesalahan saat update database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Promosikan user menjadi Admin.")
    parser.add_argument("--email", required=True, help="Email user yang akan dipromosikan.")
    args = parser.parse_args()
    
    promote_user(args.email)
