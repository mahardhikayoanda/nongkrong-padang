from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import auth, tempat, rekomendasi, profil, admin
from app.db.database import Base, engine
from app.models import models  # pastikan models ter-import

# Buat semua tabel (jika belum ada)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    description="API untuk sistem rekomendasi tempat nongkrong Kota Padang",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS untuk Flutter app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ganti dengan domain spesifik di production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register semua routes
app.include_router(auth.router,         prefix="/api/v1")
app.include_router(tempat.router,       prefix="/api/v1")
app.include_router(rekomendasi.router,  prefix="/api/v1")

@app.get("/")
def root():
    return {
        "app": settings.app_name,
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}