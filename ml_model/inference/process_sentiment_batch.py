import sys
import os

# --- PERBAIKAN PATH AGAR BISA AKSES 'utils' DAN 'ml_model' ---
# Mendapatkan path absolut ke folder D:\nongkrong-padang
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if root_dir not in sys.path:
    sys.path.append(root_dir)
# ------------------------------------------------------------

from ml_model.inference.absa_pipeline import ABSAPipeline
print(sys.path)
# Jika utils ada di dalam pipeline, gunakan path ini:
from pipeline.utils.db_helper import get_ulasan_belum_dianalisis, simpan_hasil_sentimen

def jalankan_batch_analysis():
    print("[BATCH] Memulai proses analisis sentimen...")
    pipeline = ABSAPipeline()
    
    # Ambil ulasan yang belum diproses
    ulasan_list = get_ulasan_belum_dianalisis()
    
    if not ulasan_list:
        print("[BATCH] Tidak ada ulasan baru untuk diproses.")
        return

    print(f"[BATCH] Ditemukan {len(ulasan_list)} ulasan untuk dianalisis.")
    
    for ulasan in ulasan_list:
        print(f"---")
        print(f"[PROCESS] Ulasan ID {ulasan['id_ulasan']}: {ulasan['teks_ulasan'][:50]}...")
        
        # Jalankan pipeline ABSA
        hasil = pipeline.analisis(ulasan['teks_ulasan'])
        
        if not hasil:
            print("[SKIP] Tidak ada aspek ditemukan.")
            continue
            
        for item in hasil:
            simpan_hasil_sentimen(ulasan['id_ulasan'], item)
            print(f"[SAVED] Aspek: {item['term']} | Sentimen: {item['polaritas']}")

    print("[BATCH] Proses selesai.")

if __name__ == "__main__":
    jalankan_batch_analysis()