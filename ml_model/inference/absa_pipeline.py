import os
import sys

# Perbaikan path agar folder 'ml_model' dikenali sebagai paket
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(parent_dir)
sys.path.append(root_dir)

import torch
from transformers import (AutoModelForSequenceClassification,
                          AutoModelForTokenClassification,
                          AutoTokenizer)
# Sekarang impor dari src akan berhasil karena root_dir sudah di-append
from src.dataset import (POLARITAS_MAP, ID_TO_POLARITAS,
                         BIO_MAP, ID_TO_BIO, term_ke_kategori)
from dotenv import load_dotenv

load_dotenv()

# Gunakan jalur absolut agar lebih aman
BASE_DIR = root_dir
MODEL_ATE_PATH = os.getenv("MODEL_ATE_PATH", os.path.join(BASE_DIR, "models", "ate"))
MODEL_ASC_PATH = os.getenv("MODEL_ASC_PATH", os.path.join(BASE_DIR, "models", "asc"))
INDOBERT_BASE  = "indobenchmark/indobert-base-p1"

class ABSAPipeline:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"[ABSA] Menggunakan device: {self.device}")
        self._load_models()
    
    def _load_models(self):
        # ── ATE Model ──────────────────────────────────────
        ate_path = MODEL_ATE_PATH if os.path.exists(MODEL_ATE_PATH) else INDOBERT_BASE
        print(f"[ABSA] Loading ATE dari: {ate_path}")
        self.ate_tokenizer = AutoTokenizer.from_pretrained(ate_path)
        self.ate_model = AutoModelForTokenClassification.from_pretrained(
            ate_path, num_labels=3, ignore_mismatched_sizes=True
        ).to(self.device)
        self.ate_model.eval()
        
        # ── ASC Model ──────────────────────────────────────
        asc_path = MODEL_ASC_PATH if os.path.exists(MODEL_ASC_PATH) else INDOBERT_BASE
        print(f"[ABSA] Loading ASC dari: {asc_path}")
        self.asc_tokenizer = AutoTokenizer.from_pretrained(asc_path)
        self.asc_model = AutoModelForSequenceClassification.from_pretrained(
            asc_path, num_labels=3, ignore_mismatched_sizes=True
        ).to(self.device)
        self.asc_model.eval()
        
        print("[ABSA] ✅ Model siap digunakan")
    
    # ... (tambahkan method lainnya: ekstrak_term_aspek, klasifikasi_sentimen, analisis, _keyword_fallback seperti kode Anda sebelumnya)
    
    def ekstrak_term_aspek(self, teks: str) -> list[str]:
        """
        Stage 1 — ATE: Identifikasi term aspek menggunakan BIO tagging.
        Return: list of term strings
        """
        kata_list = teks.split()
        
        encoding = self.ate_tokenizer(
            kata_list,
            is_split_into_words=True,
            return_tensors="pt",
            max_length=128,
            padding=True,
            truncation=True
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.ate_model(**encoding)
        
        pred_ids = torch.argmax(outputs.logits, dim=2).squeeze().cpu().numpy()
        word_ids = encoding.word_ids()
        
        # Decode BIO → term strings
        term_spans = {}
        prev_word_id = None
        
        for token_idx, word_id in enumerate(word_ids):
            if word_id is None or word_id == prev_word_id:
                prev_word_id = word_id
                continue
            
            label = ID_TO_BIO.get(pred_ids[token_idx], "O")
            
            if label == "B-ASP":
                term_spans[word_id] = [word_id]
            elif label == "I-ASP" and term_spans:
                last_key = max(term_spans.keys())
                term_spans[last_key].append(word_id)
            
            prev_word_id = word_id
        
        terms = []
        for word_indices in term_spans.values():
            term = " ".join(kata_list[i] for i in word_indices if i < len(kata_list))
            if term:
                terms.append(term)
        
        return terms
    
    def klasifikasi_sentimen(self, teks: str, kategori: str) -> tuple[str, float]:
        """
        Stage 2 — ASC: Klasifikasi polaritas untuk satu aspek.
        Return: (polaritas_string, confidence_score)
        """
        aux_sentence = f"Bagaimana {kategori} di tempat ini?"
        
        encoding = self.asc_tokenizer(
            teks,
            aux_sentence,
            max_length=256,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.asc_model(**encoding)
        
        probs      = torch.softmax(outputs.logits, dim=1).squeeze()
        pred_id    = torch.argmax(probs).item()
        confidence = probs[pred_id].item()
        
        return ID_TO_POLARITAS[pred_id], confidence
    
    def analisis(self, teks: str) -> list[dict]:
        """
        Pipeline lengkap ABSA untuk satu ulasan.
        Return: list of {term, kategori, polaritas, confidence}
        """
        if not teks or len(teks.split()) < 3:
            return []
        
        # Stage 1: Ekstrak term aspek
        terms = self.ekstrak_term_aspek(teks)
        
        if not terms:
            # Fallback: gunakan keyword matching
            terms = self._keyword_fallback(teks)
        
        # Stage 2: Klasifikasi sentimen per term
        hasil = []
        for term in terms:
            kategori            = term_ke_kategori(term)
            polaritas, conf     = self.klasifikasi_sentimen(teks, kategori)
            
            hasil.append({
                "term":       term,
                "kategori":   kategori,
                "polaritas":  polaritas,
                "confidence": round(conf, 4)
            })
        
        return hasil
    
    def _keyword_fallback(self, teks: str) -> list[str]:
        """
        Fallback jika ATE tidak mendeteksi term: gunakan keyword matching.
        """
        from src.dataset import ASPEK_KEYWORDS
        teks_lower = teks.lower()
        found = []
        
        for kategori, keywords in ASPEK_KEYWORDS.items():
            for kw in keywords:
                if kw in teks_lower:
                    found.append(kw)
                    break
        
        return found[:5]  # max 5 aspek per ulasan

if __name__ == "__main__":
    # Inisialisasi pipeline
    pipeline = ABSAPipeline()
    
    # Uji coba analisis
    teks = "Tempatnya nyaman, tapi kopinya mahal sekali."
    hasil = pipeline.analisis(teks)
    
    # Cetak hasil
    print(f"[HASIL ANALISIS]: {hasil}")