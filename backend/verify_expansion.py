import os
import redis
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/nongkrong_padang")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

def verify_and_clear():
    # 1. Check DB
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            cnt = conn.execute(text("SELECT count(*) FROM tempat")).scalar()
            print(f"VERIFICATION: Total places in DB = {cnt}")
    except Exception as e:
        print(f"DB Error: {e}")

    # 2. Clear Redis
    try:
        r = redis.from_url(REDIS_URL)
        r.flushall()
        print("VERIFICATION: Redis cache cleared successfully.")
    except Exception as e:
        print(f"Redis Error: {e}")

if __name__ == "__main__":
    verify_and_clear()
