-- ─── INJEKSI DATA PADANG V2 ─────────────────────────

-- Hapus data mock lama agar bersih (opsional)
-- DELETE FROM ulasan;
-- DELETE FROM profil_tempat;
-- DELETE FROM tempat;

-- 1. Kubik Koffie
INSERT INTO tempat (id_tempat, nama_tempat, alamat, latitude, longitude, kategori, rating_google, place_id_google)
VALUES ('7b123456-1111-4444-8888-000000000001', 'Kubik Koffie', 'Jl. Olo Ladang No.12, Padang', -0.938, 100.358, 'co-working', 4.5, 'sa_kubik')
ON CONFLICT (place_id_google) DO NOTHING;
INSERT INTO profil_tempat (id_tempat, vektor_sentimen, total_ulasan)
VALUES ('7b123456-1111-4444-8888-000000000001', '{0.7, 0.1, 0.6, 0.2, 0.8, 0.1, 0.7, 0.1, 0.9, 0.1}', 45)
ON CONFLICT (id_tempat) DO NOTHING;

-- 2. Mula Coffee
INSERT INTO tempat (id_tempat, nama_tempat, alamat, latitude, longitude, kategori, rating_google, place_id_google)
VALUES ('7b123456-1111-4444-8888-000000000002', 'Mula Coffee', 'Jl. Dr. Sutomo No.1, Padang', -0.928, 100.375, 'co-working', 4.6, 'sa_mula')
ON CONFLICT (place_id_google) DO NOTHING;
INSERT INTO profil_tempat (id_tempat, vektor_sentimen, total_ulasan)
VALUES ('7b123456-1111-4444-8888-000000000002', '{0.8, 0.1, 0.6, 0.1, 0.7, 0.1, 0.8, 0.1, 0.8, 0.1}', 38)
ON CONFLICT (id_tempat) DO NOTHING;

-- 3. Padang Digital
INSERT INTO tempat (id_tempat, nama_tempat, alamat, latitude, longitude, kategori, rating_google, place_id_google)
VALUES ('7b123456-1111-4444-8888-000000000003', 'Padang Digital', 'Jl. Ahmad Yani, Padang', -0.942, 100.365, 'co-working', 4.8, 'sa_pdigital')
ON CONFLICT (place_id_google) DO NOTHING;
INSERT INTO profil_tempat (id_tempat, vektor_sentimen, total_ulasan)
VALUES ('7b123456-1111-4444-8888-000000000003', '{0.6, 0.1, 0.7, 0.1, 0.9, 0.1, 0.6, 0.1, 0.95, 0.05}', 22)
ON CONFLICT (id_tempat) DO NOTHING;

-- 4. Lalito
INSERT INTO tempat (id_tempat, nama_tempat, alamat, latitude, longitude, kategori, rating_google, place_id_google)
VALUES ('7b123456-1111-4444-8888-000000000004', 'Lalito Coffee Bar', 'Jl. S. Parman No.116, Padang', -0.916, 100.364, 'kafe', 4.6, 'sa_lalito')
ON CONFLICT (place_id_google) DO NOTHING;
INSERT INTO profil_tempat (id_tempat, vektor_sentimen, total_ulasan)
VALUES ('7b123456-1111-4444-8888-000000000004', '{0.85, 0.05, 0.5, 0.2, 0.7, 0.1, 0.8, 0.1, 0.7, 0.1}', 112)
ON CONFLICT (id_tempat) DO NOTHING;

-- 5. V Coffee
INSERT INTO tempat (id_tempat, nama_tempat, alamat, latitude, longitude, kategori, rating_google, place_id_google)
VALUES ('7b123456-1111-4444-8888-000000000005', 'V Coffee', 'Jl. Raden Saleh No.3, Padang', -0.925, 100.360, 'kafe', 4.7, 'sa_vcoffee')
ON CONFLICT (place_id_google) DO NOTHING;
INSERT INTO profil_tempat (id_tempat, vektor_sentimen, total_ulasan)
VALUES ('7b123456-1111-4444-8888-000000000005', '{0.95, 0.05, 0.4, 0.3, 0.7, 0.1, 0.9, 0.05, 0.7, 0.1}', 250)
ON CONFLICT (id_tempat) DO NOTHING;

-- 6-20 (Batch)
INSERT INTO tempat (id_tempat, nama_tempat, alamat, latitude, longitude, kategori, rating_google, place_id_google) VALUES
(gen_random_uuid(), 'Safari Garden', 'Jl. Nipah No.10, Padang', -0.960, 100.355, 'resto', 4.6, 'sa_safari'),
(gen_random_uuid(), 'Kopi Batigo', 'Jl. KH. Ahmad Dahlan No.19, Padang', -0.920, 100.362, 'kafe', 4.4, 'sa_batigo'),
(gen_random_uuid(), 'Cafe Merdeka', 'Jl. Diponegoro No.5, Padang', -0.952, 100.358, 'kafe', 4.3, 'sa_merdeka'),
(gen_random_uuid(), 'Rimbun Espresso', 'Jl. Kurao Pagang, Padang', -0.880, 100.380, 'kafe', 4.7, 'sa_rimbun'),
(gen_random_uuid(), 'Coffee Theory', 'Jl. Veteran No.60, Padang', -0.925, 100.355, 'kafe', 4.6, 'sa_theory'),
(gen_random_uuid(), 'Hideout Coffee', 'Jl. Hamka No.45, Padang', -0.890, 100.350, 'kafe', 4.5, 'sa_hideout'),
(gen_random_uuid(), 'Janji Jiwa Yani', 'Jl. Ahmad Yani No.12, Padang', -0.942, 100.365, 'kafe', 4.4, 'sa_jiwa'),
(gen_random_uuid(), 'EL''S Coffee Yani', 'Jl. Ahmad Yani No.30, Padang', -0.942, 100.367, 'kafe', 4.4, 'sa_els'),
(gen_random_uuid(), 'Upnormal Ahmad Yani', 'Jl. Ahmad Yani No.18, Padang', -0.943, 100.366, 'kafe', 4.2, 'sa_upnormal'),
(gen_random_uuid(), 'Foresthree Sawahan', 'Jl. Sawahan No.20, Padang', -0.930, 100.370, 'kafe', 4.4, 'sa_forest'),
(gen_random_uuid(), 'G-Spot Gajah Mada', 'Jl. Gajah Mada No.10, Padang', -0.900, 100.370, 'kafe', 4.4, 'sa_gspot'),
(gen_random_uuid(), 'Suko Khatib', 'Jl. Khatib Sulaiman, Padang', -0.910, 100.360, 'kafe', 4.5, 'sa_suko'),
(gen_random_uuid(), 'Kenangan Plaza Andalas', 'Plaza Andalas, Padang', -0.940, 100.360, 'kafe', 4.3, 'sa_kenangan'),
(gen_random_uuid(), 'Point Coffee Yani', 'Jl. Ahmad Yani, Padang', -0.944, 100.366, 'kafe', 4.4, 'sa_point'),
(gen_random_uuid(), 'Gading Resto Sutomo', 'Jl. Dr. Sutomo, Padang', -0.930, 100.380, 'resto', 4.5, 'sa_gading'),
(gen_random_uuid(), 'Iko Gantinyo Nipah', 'Jl. Nipah No.34, Padang', -0.965, 100.355, 'resto', 4.6, 'sa_iko'),
(gen_random_uuid(), 'Sate Itam Pemuda', 'Jl. Pemuda, Padang', -0.945, 100.360, 'resto', 4.4, 'sa_itam'),
(gen_random_uuid(), 'Bopet Rajawali Juanda', 'Jl. Juanda, Padang', -0.920, 100.355, 'resto', 4.5, 'sa_rajawali'),
(gen_random_uuid(), 'RM Fuja Samudera', 'Jl. Samudera, Padang', -0.950, 100.350, 'resto', 4.6, 'sa_fuja'),
(gen_random_uuid(), 'Kapau Ibu Hj Anis', 'Jl. Khatib Sulaiman, Padang', -0.900, 100.365, 'resto', 4.4, 'sa_anis'),
(gen_random_uuid(), 'Es Kim Teng Pondok', 'Jl. Pondok, Padang', -0.960, 100.360, 'resto', 4.5, 'sa_kimteng'),
(gen_random_uuid(), 'Old Town Gereja', 'Jl. Gereja, Padang', -0.950, 100.360, 'kafe', 4.4, 'sa_oldtown'),
(gen_random_uuid(), 'Sate Manangkabo Khatib', 'Jl. Khatib Sulaiman, Padang', -0.895, 100.367, 'resto', 4.5, 'sa_manangkabo'),
(gen_random_uuid(), 'Bakso Lava Sawahan', 'Jl. Sawahan, Padang', -0.930, 100.370, 'resto', 4.3, 'sa_lava'),
(gen_random_uuid(), 'Bika Mariana Hamka', 'Jl. Hamka, Padang', -0.880, 100.350, 'resto', 4.6, 'sa_mariana'),
(gen_random_uuid(), 'Kopi Nanyo Pondok', 'Jl. Pondok, Padang', -0.962, 100.362, 'kafe', 4.5, 'sa_nanyo'),
(gen_random_uuid(), 'Sate Syukur Hakim', 'Jl. AR Hakim, Padang', -0.957, 100.365, 'resto', 4.4, 'sa_syukur'),
(gen_random_uuid(), 'Ayam Penyet Surabaya Yani', 'Jl. Ahmad Yani, Padang', -0.943, 100.368, 'resto', 4.3, 'sa_surabaya'),
(gen_random_uuid(), 'Pizza Hut Yani', 'Jl. Ahmad Yani, Padang', -0.942, 100.365, 'resto', 4.5, 'sa_pizzahut'),
(gen_random_uuid(), 'McD Yani', 'Jl. Ahmad Yani, Padang', -0.943, 100.367, 'resto', 4.5, 'sa_mcd'),
(gen_random_uuid(), 'KFC Andalas', 'Plaza Andalas, Padang', -0.941, 100.361, 'resto', 4.4, 'sa_kfc'),
(gen_random_uuid(), 'Solaria Transmart', 'Transmart Padang, Padang', -0.890, 100.360, 'resto', 4.2, 'sa_solaria'),
(gen_random_uuid(), 'Ichiban Sushi Transmart', 'Transmart Padang, Padang', -0.891, 100.361, 'resto', 4.3, 'sa_ichiban'),
(gen_random_uuid(), 'Bakmi Naga Andalas', 'Plaza Andalas, Padang', -0.942, 100.362, 'resto', 4.1, 'sa_bakminaga'),
(gen_random_uuid(), 'Holland Sudirman', 'Jl. Sudirman, Padang', -0.945, 100.365, 'toko', 4.6, 'sa_holland'),
(gen_random_uuid(), 'JCO Basko', 'Basko Grand Mall, Padang', -0.880, 100.355, 'kafe', 4.5, 'sa_jco'),
(gen_random_uuid(), 'BreadTalk Basko', 'Basko Grand Mall, Padang', -0.881, 100.356, 'toko', 4.4, 'sa_breadtalk'),
(gen_random_uuid(), 'Gramedia Damar', 'Jl. Damar, Padang', -0.940, 100.362, 'toko', 4.7, 'sa_gramedia'),
(gen_random_uuid(), 'Perpustakaan Daerah Padang', 'Jl. Diponegoro, Padang', -0.950, 100.355, 'perpustakaan', 4.8, 'sa_perpus'),
(gen_random_uuid(), 'Museum Adityawarman Padang', 'Jl. Diponegoro, Padang', -0.952, 100.357, 'wisata', 4.6, 'sa_museum'),
(gen_random_uuid(), 'D''Ox Ville Hotel', 'Jl. Kampung Sebelah No. 28, Padang', -0.955, 100.358, 'hotel', 4.7, 'sa_doxville'),
(gen_random_uuid(), 'The Axana Hotel', 'Jl. Bundo Kanduang No. 14, Padang', -0.948, 100.355, 'hotel', 4.4, 'sa_axana'),
(gen_random_uuid(), 'Grand Zuri Padang', 'Jl. Thamrin No. 27, Padang', -0.952, 100.365, 'hotel', 4.5, 'sa_grandzuri')
ON CONFLICT (place_id_google) DO NOTHING;

-- Injeksi Profil untuk yang baru di atas (menggunakan ID yang baru digenerate)
INSERT INTO profil_tempat (id_tempat, vektor_sentimen, total_ulasan)
SELECT id_tempat, '{0.8, 0.1, 0.7, 0.1, 0.7, 0.1, 0.8, 0.1, 0.6, 0.1}', 30 
FROM tempat 
WHERE id_tempat NOT IN (SELECT id_tempat FROM profil_tempat);

COMMIT;
