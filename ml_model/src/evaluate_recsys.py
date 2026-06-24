import numpy as np
import math

def hitung_precision_at_k(recommended_items, relevant_items, k):
    """
    Menghitung Precision@K
    Berapa banyak dari Top-K rekomendasi yang relevan?
    """
    rek_k = recommended_items[:k]
    relevant_and_recommended = set(rek_k).intersection(set(relevant_items))
    return len(relevant_and_recommended) / k

def hitung_recall_at_k(recommended_items, relevant_items, k):
    """
    Menghitung Recall@K
    Berapa banyak dari total item relevan yang berhasil direkomendasikan di Top-K?
    """
    rek_k = recommended_items[:k]
    relevant_and_recommended = set(rek_k).intersection(set(relevant_items))
    if len(relevant_items) == 0:
        return 0.0
    return len(relevant_and_recommended) / len(relevant_items)

def hitung_ndcg_at_k(recommended_items, relevant_items, k):
    """
    Menghitung NDCG@K (Normalized Discounted Cumulative Gain)
    Seberapa baik urutan/ranking dari item relevan di Top-K?
    """
    rek_k = recommended_items[:k]
    dcg = 0.0
    for i, item in enumerate(rek_k):
        if item in relevant_items:
            # Relevansi biner (1 jika relevan, 0 jika tidak)
            dcg += 1.0 / math.log2(i + 2) # i+2 karena index mulai dari 0 dan log2(1) = 0
            
    # Hitung IDCG (Ideal DCG) jika semua item relevan ada di urutan teratas
    idcg = 0.0
    for i in range(min(len(relevant_items), k)):
        idcg += 1.0 / math.log2(i + 2)
        
    if idcg == 0.0:
        return 0.0
    return dcg / idcg

def evaluasi_leave_one_out(user_ground_truth, user_recommendations, k_list=[5, 10]):
    """
    Fungsi utama untuk menjalankan evaluasi Leave-One-Out
    user_ground_truth: dict {user_id: [item_id_yang_disembunyikan]}
    user_recommendations: dict {user_id: [list_top_n_rekomendasi_dari_sistem]}
    """
    hasil_evaluasi = {}
    
    for k in k_list:
        precisions, recalls, ndcgs = [], [], []
        
        for user_id, relevant_items in user_ground_truth.items():
            rekomendasi = user_recommendations.get(user_id, [])
            
            if not rekomendasi:
                continue
                
            precisions.append(hitung_precision_at_k(rekomendasi, relevant_items, k))
            recalls.append(hitung_recall_at_k(rekomendasi, relevant_items, k))
            ndcgs.append(hitung_ndcg_at_k(rekomendasi, relevant_items, k))
            
        hasil_evaluasi[f'K={k}'] = {
            'Precision': np.mean(precisions) if precisions else 0.0,
            'Recall': np.mean(recalls) if recalls else 0.0,
            'NDCG': np.mean(ndcgs) if ndcgs else 0.0
        }
        
    return hasil_evaluasi

# --- BLOK PENGUJIAN DUMMY (Bisa dihapus nanti saat integrasi dengan DB) ---
if __name__ == "__main__":
    print("Menjalankan simulasi evaluasi sistem rekomendasi...")
    
    # Simulasi: Item target (ground truth) hasil leave-one-out untuk 3 user
    dummy_ground_truth = {
        'user_1': ['place_101'],
        'user_2': ['place_205'],
        'user_3': ['place_303']
    }
    
    # Simulasi: Hasil prediksi dari model Cosine Similarity Anda
    dummy_recommendations = {
        'user_1': ['place_001', 'place_101', 'place_003', 'place_004', 'place_005'], # Hits di rank 2
        'user_2': ['place_201', 'place_202', 'place_203', 'place_204', 'place_205'], # Hits di rank 5
        'user_3': ['place_301', 'place_302', 'place_305', 'place_306', 'place_307']  # Miss
    }
    
    metrik = evaluasi_leave_one_out(dummy_ground_truth, dummy_recommendations, k_list=[3, 5])
    
    import json
    print(json.dumps(metrik, indent=4))