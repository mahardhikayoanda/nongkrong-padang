import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://nongkrong_user:nongkrong_pass@localhost:5432/nongkrong_db")

def fix():
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            print("Connected to DB. Adding column...")
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS jenis_kelamin VARCHAR(20)"))
            conn.commit()
            print("Column 'jenis_kelamin' added successfully (or already exists).")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix()
