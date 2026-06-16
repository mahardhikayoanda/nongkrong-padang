import json
import torch
from torch.utils.data import Dataset
from transformers import AutoTokenizer
from typing import List, Dict, Tuple

# Label mapping untuk ASC
POLARITAS_MAP = {"positif": 0, "negatif": 1, "netral": 2}
ID_TO_POLARITAS = {v: k for k, v in POLARITAS_MAP.items()}

# Label mapping untuk ATE (BIO tagging)
BIO_MAP = {"O": 0, "B-ASP": 1, "I-ASP": 2}
ID_TO_BIO = {v: k for k, v in BIO_MAP.items()}

# Kategori aspek dan kata kunci terkait
ASPEK_KEYWORDS = {
    "suasana":   ["suasana", "tempat", "nyaman", "tenang", "ramai", "bising",
                  "lighting", "dekorasi", "ambiance", "interior", "outdoor", "indoor"],
    "harga":     ["harga", "mahal", "murah", "terjangkau", "worth", "reasonable",
                  "hemat", "ekonomis", "kantong", "biaya"],
    "lokasi":    ["lokasi", "parkir", "akses", "strategis", "jauh", "dekat",
                  "jalan", "transportasi", "tersembunyi"],
    "pelayanan": ["pelayanan", "staff", "karyawan", "ramah", "lambat", "cepat",
                  "profesional", "melayani", "antri"],
    "fasilitas": ["wifi", "colokan", "toilet", "ac", "listrik", "fasilitas",
                  "kebersihan", "bersih", "kotor", "kopi", "makanan"],
}

def term_ke_kategori(term: str) -> str:
    """Petakan term aspek ke salah satu dari 5 kategori."""
    term_lower = term.lower()
    for kategori, keywords in ASPEK_KEYWORDS.items():
        if any(kw in term_lower for kw in keywords):
            return kategori
    return "suasana"  # default fallback

class DatasetASC(Dataset):
    """
    Dataset untuk Aspect Sentiment Classification.
    Input: [CLS] teks_ulasan [SEP] Bagaimana {kategori_aspek} di tempat ini? [SEP]
    Label: 0=positif, 1=negatif, 2=netral
    """
    
    def __init__(self, data_path: str, tokenizer_name: str, max_length: int = 256):
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
        self.max_length = max_length
        self.samples = []
        self._load_data(data_path)
    
    def _load_data(self, path: str):
        with open(path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
        
        for item in raw_data:
            teks = item["teks"]
            for aspek_item in item["aspek_sentimen"]:
                kategori = aspek_item["aspek"]
                polaritas = aspek_item["polaritas"]
                
                # Auxiliary sentence (sesuai metode Hoang et al. 2022)
                aux_sentence = f"Bagaimana {kategori} di tempat ini?"
                
                self.samples.append({
                    "teks": teks,
                    "aux_sentence": aux_sentence,
                    "kategori": kategori,
                    "label": POLARITAS_MAP[polaritas]
                })
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        sample = self.samples[idx]
        
        # Tokenisasi: [CLS] teks [SEP] aux_sentence [SEP]
        encoding = self.tokenizer(
            sample["teks"],
            sample["aux_sentence"],
            max_length=self.max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        
        return {
            "input_ids":      encoding["input_ids"].squeeze(),
            "attention_mask": encoding["attention_mask"].squeeze(),
            "token_type_ids": encoding.get("token_type_ids", 
                              torch.zeros_like(encoding["input_ids"])).squeeze(),
            "labels":         torch.tensor(sample["label"], dtype=torch.long)
        }


class DatasetATE(Dataset):
    """
    Dataset untuk Aspect Term Extraction menggunakan BIO tagging.
    Setiap token diberi label: O, B-ASP (awal aspek), I-ASP (lanjutan aspek)
    """
    
    def __init__(self, data_path: str, tokenizer_name: str, max_length: int = 128):
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
        self.max_length = max_length
        self.samples = []
        self._load_data(data_path)
    
    def _load_data(self, path: str):
        with open(path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
        
        for item in raw_data:
            teks = item["teks"]
            kata_list = teks.split()
            
            # Inisialisasi semua token sebagai "O"
            bio_labels = ["O"] * len(kata_list)
            
            # Tandai token yang merupakan term aspek
            for aspek_item in item["aspek_sentimen"]:
                term_kata = aspek_item["term"].lower().split()
                
                for i in range(len(kata_list)):
                    if kata_list[i].lower() == term_kata[0]:
                        # Cek apakah urutan kata cocok
                        match = all(
                            i + j < len(kata_list) and
                            kata_list[i + j].lower() == term_kata[j]
                            for j in range(len(term_kata))
                        )
                        if match:
                            bio_labels[i] = "B-ASP"
                            for j in range(1, len(term_kata)):
                                bio_labels[i + j] = "I-ASP"
            
            self.samples.append({
                "kata_list": kata_list,
                "bio_labels": [BIO_MAP[l] for l in bio_labels]
            })
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        sample = self.samples[idx]
        
        encoding = self.tokenizer(
            sample["kata_list"],
            is_split_into_words=True,
            max_length=self.max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        
        # Align label ke subword tokens
        word_ids = encoding.word_ids()
        labels_aligned = []
        prev_word_id = None
        
        for word_id in word_ids:
            if word_id is None:
                labels_aligned.append(-100)  # token spesial → ignore
            elif word_id != prev_word_id:
                labels_aligned.append(sample["bio_labels"][word_id])
            else:
                # Subword lanjutan: pakai I-ASP jika B-ASP sebelumnya
                prev_label = sample["bio_labels"][word_id]
                labels_aligned.append(
                    BIO_MAP["I-ASP"] if prev_label == BIO_MAP["B-ASP"] else prev_label
                )
            prev_word_id = word_id
        
        return {
            "input_ids":      encoding["input_ids"].squeeze(),
            "attention_mask": encoding["attention_mask"].squeeze(),
            "labels":         torch.tensor(labels_aligned, dtype=torch.long)
        }