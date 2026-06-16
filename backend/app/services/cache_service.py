import redis
from app.core.config import settings

class CacheService:
    def __init__(self):
        try:
            self.client = redis.from_url(settings.redis_url, decode_responses=True)
        except Exception:
            self.client = None

    def get(self, key: str):
        if not self.client:
            return None
        try:
            return self.client.get(key)
        except Exception:
            return None

    def set(self, key: str, value: str, ttl: int = 3600):
        if not self.client:
            return
        try:
            self.client.setex(key, ttl, value)
        except Exception:
            pass

    def delete(self, key: str):
        if not self.client:
            return
        try:
            self.client.delete(key)
        except Exception:
            pass