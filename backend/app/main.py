from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import auth, tempat, rekomendasi, profil, admin
from app.db.database import Base, engine, SessionLocal
from app.models import models
from app.models.models import User
from app.core.security import hash_password
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup Tasks ---
    print("[SYSTEM] Starting up...")
    
    # 1. Migrasi manual
    print("[DB] Menjalankan migrasi manual untuk 'jenis_kelamin'...")
    from sqlalchemy import text
    try:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS jenis_kelamin VARCHAR(20)"))
            conn.commit()
            print("[DB] Migrasi 'jenis_kelamin' OK.")
    except Exception as e:
        print(f"[DB] Gagal migrasi: {e}")

    # 2. Inisialisasi admin
    print("[AUTH] Mengecek ketersediaan akun admin...")
    db = SessionLocal()
    try:
        email = "mahardhikayoanda07@gmail.com"
        user = db.query(User).filter(User.email == email).first()
        hashed_pw = hash_password("admin123")
        
        if not user:
            print(f">>> [ADMIN SETUP] Membuat admin baru: {email}")
            user = User(
                nama="Mahardhika Yoanda",
                email=email,
                password=hashed_pw,
                role="admin"
            )
            db.add(user)
            db.commit()
            print(f">>> [ADMIN SETUP] Sukses membuat admin.")
        else:
            print(f">>> [ADMIN SETUP] Resetting password admin untuk: {email}")
            user.role = "admin"
            user.password = hashed_pw
            db.commit()
            print(f">>> [ADMIN SETUP] Password admin berhasil di-reset ke 'admin123'.")
            
        print("[AUTH] Akun admin siap: mahardhikayoanda07@gmail.com / admin123")
    except Exception as e:
        print(f"[AUTH] ERROR saat inisialisasi admin: {e}")
    finally:
        db.close()
    
    yield
    
    # --- Shutdown Tasks ---
    print("[SYSTEM] Shutting down...")

# Inisialisasi app dengan lifespan dan settings
app = FastAPI(
    title=settings.app_name,
    description="API untuk sistem rekomendasi tempat nongkrong Kota Padang",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Buat semua tabel (jika belum ada)
Base.metadata.create_all(bind=engine)

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
app.include_router(profil.router,       prefix="/api/v1")
app.include_router(admin.router,        prefix="/api/v1")

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