from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.models.models import Interaksi, Tempat
from app.schemas.schemas import TempatResponse

router = APIRouter(prefix="/profil", tags=["Profil"])

@router.get("/riwayat", response_model=List[TempatResponse])
def get_riwayat_kunjungan(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Mengambil daftar tempat yang pernah diinteraksi (diklik/diulas) oleh pengguna login.
    """
    # Mengambil riwayat dari tabel interaksi, diurutkan dari yang terbaru
    riwayat = db.query(Interaksi).filter(
        Interaksi.id_user == current_user.id_user
    ).order_by(Interaksi.timestamp.desc()).all()

    if not riwayat:
        return []

    # Mengambil detail tempat berdasarkan id_tempat dari interaksi
    tempat_dikunjungi = []
    seen_places = set() # Untuk menghindari duplikasi tempat
    
    for interaksi in riwayat:
        if interaksi.id_tempat not in seen_places:
            tempat = db.query(Tempat).filter(Tempat.id_tempat == interaksi.id_tempat).first()
            if tempat:
                tempat_dikunjungi.append(tempat)
                seen_places.add(interaksi.id_tempat)

    return tempat_dikunjungi