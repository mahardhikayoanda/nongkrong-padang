-- ================================================
-- SKEMA DATABASE: Nongkrong Padang
-- Sesuai ERD pada proposal (Gambar 3.24)
-- ================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ─── TABEL USERS ────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id_user        UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nama           VARCHAR(100) NOT NULL,
    email          VARCHAR(150) UNIQUE NOT NULL,
    password       VARCHAR(255) NOT NULL,  -- bcrypt hash
    role           VARCHAR(20) DEFAULT 'user' CHECK (role IN ('user', 'admin')),
    jenis_kelamin  VARCHAR(20),
    preferensi_konteks JSONB DEFAULT '{}',
    created_at     TIMESTAMP DEFAULT NOW()
);

-- ─── TABEL TEMPAT ───────────────────────────────
CREATE TABLE IF NOT EXISTS tempat (
    id_tempat      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nama_tempat    VARCHAR(200) NOT NULL,
    alamat         TEXT,
    latitude       FLOAT,
    longitude      FLOAT,
    kategori       VARCHAR(50),
    rating_google  FLOAT,
    place_id_google VARCHAR(200) UNIQUE,  -- ID dari Google Places API
    foto_url       TEXT,
    jam_buka       JSONB DEFAULT '{}',
    created_at     TIMESTAMP DEFAULT NOW(),
    updated_at     TIMESTAMP DEFAULT NOW()
);

-- ─── TABEL ULASAN ───────────────────────────────
CREATE TABLE IF NOT EXISTS ulasan (
    id_ulasan      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    id_tempat      UUID NOT NULL REFERENCES tempat(id_tempat) ON DELETE CASCADE,
    teks_ulasan    TEXT NOT NULL,
    rating         INTEGER CHECK (rating BETWEEN 1 AND 5),
    author_name    VARCHAR(100),
    review_id_google VARCHAR(200) UNIQUE,  -- hindari duplikasi
    timestamp      TIMESTAMP DEFAULT NOW()
);

-- ─── TABEL ASPEK_SENTIMEN ───────────────────────
CREATE TABLE IF NOT EXISTS aspek_sentimen (
    id_aspek       UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    id_ulasan      UUID NOT NULL REFERENCES ulasan(id_ulasan) ON DELETE CASCADE,
    kategori_aspek VARCHAR(50) NOT NULL
                   CHECK (kategori_aspek IN
                   ('suasana','harga','lokasi','pelayanan','fasilitas')),
    polaritas      VARCHAR(10) NOT NULL
                   CHECK (polaritas IN ('positif','negatif','netral')),
    skor_confidence FLOAT DEFAULT 0.0,
    term_aspek     VARCHAR(200)  -- kata/frasa aspek yang diekstrak ATE
);

-- ─── TABEL PROFIL_TEMPAT ────────────────────────
-- Vektor 10 dimensi: [suasana+, suasana-, harga+, harga-,
--                     lokasi+, lokasi-, pelayanan+, pelayanan-,
--                     fasilitas+, fasilitas-]
CREATE TABLE IF NOT EXISTS profil_tempat (
    id_profil      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    id_tempat      UUID UNIQUE NOT NULL REFERENCES tempat(id_tempat),
    vektor_sentimen FLOAT[] DEFAULT ARRAY[0,0,0,0,0,0,0,0,0,0],
    total_ulasan   INTEGER DEFAULT 0,
    updated_at     TIMESTAMP DEFAULT NOW()
);

-- ─── TABEL INTERAKSI ────────────────────────────
CREATE TABLE IF NOT EXISTS interaksi (
    id_interaksi   UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    id_user        UUID NOT NULL REFERENCES users(id_user) ON DELETE CASCADE,
    id_tempat      UUID NOT NULL REFERENCES tempat(id_tempat) ON DELETE CASCADE,
    tipe_aksi      VARCHAR(30) NOT NULL
                   CHECK (tipe_aksi IN ('klik','bookmark','abaikan','kunjungi')),
    konteks_sesi   JSONB DEFAULT '{}',  -- waktu, tujuan, rombongan saat interaksi
    timestamp      TIMESTAMP DEFAULT NOW()
);

-- ─── INDEXES untuk performa query ───────────────
CREATE INDEX idx_ulasan_tempat ON ulasan(id_tempat);
CREATE INDEX idx_aspek_ulasan ON aspek_sentimen(id_ulasan);
CREATE INDEX idx_aspek_kategori ON aspek_sentimen(kategori_aspek);
CREATE INDEX idx_interaksi_user ON interaksi(id_user);
CREATE INDEX idx_interaksi_tempat ON interaksi(id_tempat);
CREATE INDEX idx_profil_tempat ON profil_tempat(id_tempat);

-- ─── DATA AWAL: Admin user ───────────────────────
-- Password: admin123 (ganti setelah deploy!)
INSERT INTO users (nama, email, password, role)
VALUES (
    'Administrator',
    'admin@nongkrong.com',
    '$2b$12$placeholder_hash_ganti_nanti',
    'admin'
) ON CONFLICT (email) DO NOTHING;