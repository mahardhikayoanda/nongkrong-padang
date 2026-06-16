from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Nongkrong Padang API"
    debug: bool = True
    
    # Database
    database_url: str
    
    # JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Google API
    google_places_api_key: str = ""

    class Config:
        env_file = ".env"

settings = Settings()