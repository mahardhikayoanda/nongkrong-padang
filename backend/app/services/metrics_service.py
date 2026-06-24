import math
import numpy as np
from sqlalchemy.orm import Session
from app.models.models import Interaksi, Tempat
from app.services.rekomendasi_service import RekomendasiService
from app.schemas.schemas import KonteksRequest

class MetricsService:
    def __init__(self, db: Session):
        self.db = db

    def calculate_metrics(self, user_id, k=10):
        """
        Menghitung Precision@K dan NDCG@K untuk user tertentu.
        Berdasarkan data interaksi (bookmark/klik) sebagai ground truth.
        """
        # 1. Ambil ground truth (tempat yang pernah diklik/bookmark oleh user)
        gt_interactions = self.db.query(Interaksi).filter(
            Interaksi.id_user == user_id,
            Interaksi.tipe_aksi.in_(["klik", "bookmark"])
        ).all()
        
        if not gt_interactions:
            return {"precision": 0.0, "ndcg": 0.0, "status": "no_data"}

        ground_truth_ids = set([str(i.id_tempat) for i in gt_interactions if i.id_tempat])
        
        # 2. Ambil konteks terakhir dari interaksi user untuk simulasi request
        last_interaksi = gt_interactions[-1]
        konteks_data = last_interaksi.konteks_sesi or {}
        
        konteks = KonteksRequest(
            waktu=konteks_data.get("waktu", "pagi"),
            tujuan=konteks_data.get("tujuan", "hangout"),
            rombongan=konteks_data.get("rombongan", "sendiri"),
            hari=konteks_data.get("hari", "kerja"),
            top_k=k
        )
        
        # 3. Dapatkan rekomendasi dari sistem
        service = RekomendasiService(self.db)
        rekomendasi_res = service.hitung_rekomendasi(konteks)
        rec_ids = [str(r.id_tempat) for r in rekomendasi_res.rekomendasi]

        # 4. Hitung Precision@K
        hits = [1 if rid in ground_truth_ids else 0 for rid in rec_ids]
        precision = sum(hits) / k if k > 0 else 0
        
        # 5. Hitung NDCG@K
        dcg = 0.0
        idcg = 0.0
        
        # DCG
        for i, hit in enumerate(hits):
            if hit:
                dcg += 1.0 / math.log2(i + 2)
        
        # IDCG (Ideal DCG - jika semua k teratas adalah relevan)
        for i in range(min(len(ground_truth_ids), k)):
            idcg += 1.0 / math.log2(i + 2)
            
        ndcg = dcg / idcg if idcg > 0 else 0.0
        
        return {
            "precision": round(precision, 4),
            "ndcg": round(ndcg, 4),
            "total_relevant": len(ground_truth_ids),
            "k": k
        }
