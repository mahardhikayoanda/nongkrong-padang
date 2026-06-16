from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.schemas import KonteksRequest, RekomendasiResponse
from app.services.rekomendasi_service import RekomendasiService
from app.services.cache_service import CacheService
from app.core.dependencies import get_current_user
from app.models.models import User, Interaksi
import json

router = APIRouter(prefix="/rekomendasi", tags=["Rekomendasi"])

@router.post("/", response_model=RekomendasiResponse)
def get_rekomendasi(
    konteks: KonteksRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cache = CacheService()
    
    # Generate cache key dari parameter konteks
    cache_key = f"rek:{konteks.waktu}:{konteks.tujuan}:{konteks.rombongan}:k{konteks.top_k}"
    
    # Cek Redis cache dulu
    cached = cache.get(cache_key)
    if cached:
        return RekomendasiResponse(**json.loads(cached))
    
    # Hitung rekomendasi
    service = RekomendasiService(db)
    hasil = service.hitung_rekomendasi(konteks)
    
    # Simpan ke cache (TTL 1 jam)
    cache.set(cache_key, json.dumps(hasil.dict(), default=str), ttl=3600)
    
    # Log interaksi user
    log = Interaksi(
        id_user=current_user.id_user,
        id_tempat=None,  # interaksi pencarian, bukan klik tempat
        tipe_aksi="klik",
        konteks_sesi={
            "waktu": konteks.waktu,
            "tujuan": konteks.tujuan,
            "rombongan": konteks.rombongan
        }
    )
    
    return hasil