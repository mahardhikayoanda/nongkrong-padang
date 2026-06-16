from pydantic import BaseModel, EmailStr
from typing import Optional, List
from uuid import UUID
from datetime import datetime

# ─── AUTH ────────────────────────────────────────
class UserRegister(BaseModel):
    nama: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

# ─── TEMPAT ──────────────────────────────────────
class TempatBase(BaseModel):
    nama_tempat: str
    alamat: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    kategori: Optional[str] = None
    rating_google: Optional[float] = None
    foto_url: Optional[str] = None

class TempatResponse(TempatBase):
    id_tempat: UUID
    place_id_google: Optional[str] = None

    class Config:
        from_attributes = True

# ─── PROFIL SENTIMEN ─────────────────────────────
class SentimenAspek(BaseModel):
    suasana_pos: float = 0.0
    suasana_neg: float = 0.0
    harga_pos: float = 0.0
    harga_neg: float = 0.0
    lokasi_pos: float = 0.0
    lokasi_neg: float = 0.0
    pelayanan_pos: float = 0.0
    pelayanan_neg: float = 0.0
    fasilitas_pos: float = 0.0
    fasilitas_neg: float = 0.0

class TempatDetailResponse(TempatResponse):
    profil_sentimen: Optional[SentimenAspek] = None
    total_ulasan: int = 0

# ─── REKOMENDASI ─────────────────────────────────
class KonteksRequest(BaseModel):
    waktu: str          # pagi | siang | sore | malam
    tujuan: str         # kerja | hangout | kencan | meeting
    rombongan: str      # sendiri | berdua | kecil | besar
    top_k: int = 10

class RekomendasiItem(BaseModel):
    id_tempat: UUID
    nama_tempat: str
    alamat: Optional[str]
    rating_google: Optional[float]
    foto_url: Optional[str]
    skor_relevansi: float
    profil_sentimen: SentimenAspek
    tag_konteks: List[str] = []

class RekomendasiResponse(BaseModel):
    konteks: dict
    total: int
    rekomendasi: List[RekomendasiItem]

# ─── PROFIL USER ─────────────────────────────────
class UpdateProfil(BaseModel):
    nama: Optional[str] = None
    preferensi_konteks: Optional[dict] = None

class UserResponse(BaseModel):
    id_user: UUID
    nama: str
    email: str
    role: str
    preferensi_konteks: dict

    class Config:
        from_attributes = True