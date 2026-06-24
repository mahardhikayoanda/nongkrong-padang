import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Tambahkan project root ke sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.models import User
from app.db.database import SessionLocal, engine
from app.core.security import verify_password

def check_user(email: str):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            print(f"USER FOUND: {user.email}")
            print(f"Name: {user.nama}")
            print(f"Role: {user.role}")
            print(f"Password Match 'admin123': {verify_password('admin123', user.password)}")
        else:
            print(f"USER NOT FOUND: {email}")
    except Exception as e:
        print(f"DATABASE ERROR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_user("mahardhikayoanda07@gmail.com")
