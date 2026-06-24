import sys
import os
from sqlalchemy.orm import Session

# Tambahkan project root ke sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.models import User
from app.db.database import SessionLocal
from app.core.security import hash_password

def setup_admin(email: str, nama: str, password: str):
    log_file = "admin_setup.log"
    db = SessionLocal()
    try:
        with open(log_file, "w") as f:
            f.write(f"Memulai setup admin untuk {email}...\n")
            user = db.query(User).filter(User.email == email).first()
            if user:
                f.write(f"User '{email}' ditemukan. Memperbarui menjadi admin...\n")
                user.role = "admin"
                user.nama = nama
            else:
                f.write(f"User '{email}' tidak ditemukan. Membuat user baru...\n")
                user = User(
                    nama=nama,
                    email=email,
                    password=hash_password(password),
                    role="admin"
                )
                db.add(user)
            
            db.commit()
            f.write(f"SUKSES: '{nama}' ({email}) sekarang adalah Admin.\n")
            f.write(f"Password: {password}\n")
            print("Done.")
    except Exception as e:
        with open(log_file, "a") as f:
            f.write(f"ERROR: {e}\n")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    email = "mahardhikayoanda07@gmail.com"
    nama = "Mahardhika Yoanda"
    password = "admin123"
    
    setup_admin(email, nama, password)
