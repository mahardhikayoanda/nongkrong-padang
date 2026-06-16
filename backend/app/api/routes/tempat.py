from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.db.database import get_db
from app.models.models import Tempat, ProfilTempat, AspekSentimen, Ulasan
from app.schemas.schemas import TempatDetailResponse, SentimenAspek
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/tempat", tags=["Tempat"])

@router.get("/", response_model=List[dict])
def list_tempat(
    skip: int = 0,
    limit: int = 20,
    kategori: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Tempat)
    if kategori:
        query = query.filter(Tempat.kategori == kategori)
    
    tempat_list = query.offset(skip).limit(limit).all()
    
    return [
        {
            "id_tempat": str(t.id_tempat),
            "nama_tempat": t.nama_tempat,
            "alamat": t.alamat,
            "rating_google": t.rating_google,
            "kategori": t.kategori,
            "foto_url": t.foto_url,
        }
        for t in tempat_list
    ]

@router.get("/{id_tempat}/detail")
def detail_tempat(id_tempat: UUID, db: Session = Depends(get_db)):
    tempat = db.query(Tempat).filter(Tempat.id_tempat == id_tempat).first()
    if not tempat:
        raise HTTPException(status_code=404, detail="Tempat tidak ditemukan")
    
    profil = db.query(ProfilTempat).filter(
        ProfilTempat.id_tempat == id_tempat
    ).first()
    
    # Ambil cuplikan ulasan per aspek
    cuplikan = {}
    for aspek in ["suasana", "harga", "lokasi", "pelayanan", "fasilitas"]:
        sample = db.query(AspekSentimen).join(Ulasan).filter(
            Ulasan.id_tempat == id_tempat,
            AspekSentimen.kategori_aspek == aspek,
            AspekSentimen.polaritas == "positif"
        ).limit(2).all()
        
        cuplikan[aspek] = [
            {"teks": a.ulasan.teks_ulasan[:150], "polaritas": a.polaritas}
            for a in sample
        ]
    
    vektor = profil.vektor_sentimen if profil else [0]*10
    
    return {
        "id_tempat": str(tempat.id_tempat),
        "nama_tempat": tempat.nama_tempat,
        "alamat": tempat.alamat,
        "latitude": tempat.latitude,
        "longitude": tempat.longitude,
        "rating_google": tempat.rating_google,
        "foto_url": tempat.foto_url,
        "total_ulasan": profil.total_ulasan if profil else 0,
        "profil_sentimen": {
            "suasana_pos": vektor[0], "suasana_neg": vektor[1],
            "harga_pos": vektor[2],   "harga_neg": vektor[3],
            "lokasi_pos": vektor[4],  "lokasi_neg": vektor[5],
            "pelayanan_pos": vektor[6],"pelayanan_neg": vektor[7],
            "fasilitas_pos": vektor[8],"fasilitas_neg": vektor[9],
        },
        "cuplikan_ulasan": cuplikan
    }