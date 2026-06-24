import uuid
from sqlalchemy import (Column, String, Float, Integer, 
                         Text, TIMESTAMP, ARRAY, ForeignKey, CheckConstraint)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id_user = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nama    = Column(String(100), nullable=False)
    email   = Column(String(150), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role    = Column(String(20), default="user")
    jenis_kelamin = Column(String(20))
    preferensi_konteks = Column(JSONB, default={})
    created_at = Column(TIMESTAMP, server_default=func.now())

    interaksi = relationship("Interaksi", back_populates="user")


class Tempat(Base):
    __tablename__ = "tempat"

    id_tempat    = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nama_tempat  = Column(String(200), nullable=False)
    alamat       = Column(Text)
    latitude     = Column(Float)
    longitude    = Column(Float)
    kategori     = Column(String(50))
    rating_google = Column(Float)
    place_id_google = Column(String(200), unique=True)
    foto_url     = Column(Text)
    jam_buka     = Column(JSONB, default={})
    created_at   = Column(TIMESTAMP, server_default=func.now())
    updated_at   = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    ulasan       = relationship("Ulasan", back_populates="tempat")
    profil       = relationship("ProfilTempat", back_populates="tempat", uselist=False)
    interaksi    = relationship("Interaksi", back_populates="tempat")


class Ulasan(Base):
    __tablename__ = "ulasan"

    id_ulasan    = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_tempat    = Column(UUID(as_uuid=True), ForeignKey("tempat.id_tempat"), nullable=False)
    teks_ulasan  = Column(Text, nullable=False)
    rating       = Column(Integer)
    author_name  = Column(String(100))
    review_id_google = Column(String(200), unique=True)
    timestamp    = Column(TIMESTAMP, server_default=func.now())

    tempat       = relationship("Tempat", back_populates="ulasan")
    aspek_sentimen = relationship("AspekSentimen", back_populates="ulasan")


class AspekSentimen(Base):
    __tablename__ = "aspek_sentimen"

    id_aspek     = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_ulasan    = Column(UUID(as_uuid=True), ForeignKey("ulasan.id_ulasan"), nullable=False)
    kategori_aspek = Column(String(50), nullable=False)
    polaritas    = Column(String(10), nullable=False)
    skor_confidence = Column(Float, default=0.0)
    term_aspek   = Column(String(200))

    ulasan       = relationship("Ulasan", back_populates="aspek_sentimen")


class ProfilTempat(Base):
    __tablename__ = "profil_tempat"

    id_profil    = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_tempat    = Column(UUID(as_uuid=True), ForeignKey("tempat.id_tempat"), unique=True, nullable=False)
    # [suasana+, suasana-, harga+, harga-, lokasi+, lokasi-,
    #  pelayanan+, pelayanan-, fasilitas+, fasilitas-]
    vektor_sentimen = Column(ARRAY(Float), default=[0]*10)
    total_ulasan = Column(Integer, default=0)
    updated_at   = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    tempat       = relationship("Tempat", back_populates="profil")


class Interaksi(Base):
    __tablename__ = "interaksi"

    id_interaksi = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_user      = Column(UUID(as_uuid=True), ForeignKey("users.id_user"), nullable=False)
    id_tempat    = Column(UUID(as_uuid=True), ForeignKey("tempat.id_tempat"), nullable=False)
    tipe_aksi    = Column(String(30), nullable=False)
    konteks_sesi = Column(JSONB, default={})
    timestamp    = Column(TIMESTAMP, server_default=func.now())

    user         = relationship("User", back_populates="interaksi")
    tempat       = relationship("Tempat", back_populates="interaksi")