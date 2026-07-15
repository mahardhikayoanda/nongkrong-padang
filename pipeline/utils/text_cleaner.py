import re

# Mapping singkatan/slang umum Bahasa Indonesia & Minang
SLANG_MAP = {
    "gak": "tidak", "ga": "tidak", "nggak": "tidak", "ndak": "tidak",
    "udah": "sudah", "udh": "sudah", "sdh": "sudah",
    "utk": "untuk", "tuk": "untuk", "buat": "untuk",
    "dgn": "dengan", "sm": "sama",
    "yg": "yang", "krn": "karena", "karna": "karena",
    "bgt": "banget", "bngt": "banget",
    "tmpt": "tempat", "tmpat": "tempat",
    "pelayanan": "pelayanan", "playananya": "pelayanannya",
    "wfii": "wifi", "wi-fi": "wifi",
    "harganya": "harga", "hrg": "harga",
    "mantap": "bagus", "mantul": "bagus",
    "kece": "bagus", "keren": "bagus",
    "jelek": "buruk", "parah": "buruk",
    # Bahasa Minang umum
    "lamak": "enak", "rancak": "bagus", "elok": "bagus",
    "indak": "tidak", "ndak": "tidak",
    "beko": "nanti", "bisuak": "besok",
}

def bersihkan_teks(teks: str) -> str:
    """
    Bersihkan dan normalisasi teks ulasan.
    Pipeline: lowercase → hapus noise → normalisasi slang → strip whitespace
    """
    if not teks:
        return ""
    
    # 1. Lowercase
    teks = teks.lower()
    
    # 2. Hapus URL
    teks = re.sub(r'http\S+|www\S+', '', teks)
    
    # 3. Hapus mention & hashtag
    teks = re.sub(r'@\w+|#\w+', '', teks)
    
    # 4. Hapus emoji dan karakter non-ASCII (simpan alfanumerik + tanda baca dasar)
    teks = re.sub(r'[^\w\s.,!?]', ' ', teks)
    
    # 5. Hapus karakter berulang (contoh: "bagussss" → "bagus")
    teks = re.sub(r'(.)\1{2,}', r'\1', teks)
    
    # 6. Normalisasi angka rating bintang
    teks = re.sub(r'\d+\s*bintang', '', teks)
    
    # 7. Ganti slang dengan kata baku
    kata_kata = teks.split()
    kata_bersih = [SLANG_MAP.get(kata, kata) for kata in kata_kata]
    teks = " ".join(kata_bersih)
    
    # 8. Hapus spasi berlebih
    teks = re.sub(r'\s+', ' ', teks).strip()
    
    return teks

def is_teks_valid(teks: str, min_kata: int = 3) -> bool: # Turunkan dari 5 ke 3
    """
    Validasi diperlonggar agar ulasan singkat tetap bisa dianalisis.
    """
    if not teks:
        return False
    # Hapus tanda baca untuk menghitung jumlah kata yang sebenarnya
    kata = teks.split()
    return len(kata) >= min_kata