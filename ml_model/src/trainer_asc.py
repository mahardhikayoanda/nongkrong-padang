import os
import torch
import json
from torch.utils.data import DataLoader, random_split
from transformers import (AutoModelForSequenceClassification, 
                           AutoTokenizer, get_linear_schedule_with_warmup)
from torch.optim import AdamW
from sklearn.metrics import f1_score, classification_report
from src.dataset import DatasetASC, POLARITAS_MAP, ID_TO_POLARITAS
from dotenv import load_dotenv

load_dotenv()

INDOBERT_BASE  = os.getenv("INDOBERT_BASE", "indobenchmark/indobert-base-p1")
MODEL_ASC_PATH = os.getenv("MODEL_ASC_PATH", "./models/asc")
DATA_PATH      = "./data/annotated/dataset_asc.json"

# Hyperparameter (sesuai proposal Section 3.5.3)
LEARNING_RATE = 2e-5
BATCH_SIZE    = 8    # kecilkan jika RAM terbatas
MAX_EPOCHS    = 5
MAX_LENGTH    = 256
NUM_LABELS    = 3    # positif, negatif, netral

def evaluate(model, dataloader, device):
    """Evaluasi model pada validation set, return F1 macro."""
    model.eval()
    all_preds, all_labels = [], []
    
    with torch.no_grad():
        for batch in dataloader:
            input_ids      = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels         = batch["labels"].to(device)
            
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            preds   = torch.argmax(outputs.logits, dim=1)
            
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
    
    f1 = f1_score(all_labels, all_preds, average="macro", zero_division=0)
    return f1, all_preds, all_labels

def train_asc():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[ASC TRAINER] Device: {device}")
    print(f"[ASC TRAINER] Loading IndoBERT dari: {INDOBERT_BASE}")
    
    # Load dataset
    dataset_full = DatasetASC(DATA_PATH, INDOBERT_BASE, MAX_LENGTH)
    print(f"[ASC TRAINER] Total samples: {len(dataset_full)}")
    
    # Split 85% train, 15% val
    n_val   = max(1, int(len(dataset_full) * 0.15))
    n_train = len(dataset_full) - n_val
    train_ds, val_ds = random_split(dataset_full, [n_train, n_val])
    
    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
    val_loader   = DataLoader(val_ds,   batch_size=BATCH_SIZE, shuffle=False)
    
    # Load model
    model = AutoModelForSequenceClassification.from_pretrained(
        INDOBERT_BASE,
        num_labels=NUM_LABELS,
        ignore_mismatched_sizes=True
    ).to(device)
    
    # Optimizer & scheduler
    optimizer = AdamW(model.parameters(), lr=LEARNING_RATE, weight_decay=0.01)
    total_steps = len(train_loader) * MAX_EPOCHS
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=total_steps // 10,
        num_training_steps=total_steps
    )
    
    best_f1 = 0.0
    history = []
    
    print(f"[ASC TRAINER] Mulai training {MAX_EPOCHS} epoch...")
    
    for epoch in range(MAX_EPOCHS):
        model.train()
        total_loss = 0
        
        for step, batch in enumerate(train_loader):
            input_ids      = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels         = batch["labels"].to(device)
            
            optimizer.zero_grad()
            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels
            )
            
            loss = outputs.loss
            loss.backward()
            
            # Gradient clipping
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            
            optimizer.step()
            scheduler.step()
            total_loss += loss.item()
        
        avg_loss = total_loss / len(train_loader)
        val_f1, preds, labels_true = evaluate(model, val_loader, device)
        
        history.append({"epoch": epoch+1, "loss": avg_loss, "val_f1": val_f1})
        print(f"  Epoch {epoch+1}/{MAX_EPOCHS} | Loss: {avg_loss:.4f} | Val F1: {val_f1:.4f}")
        
        # Simpan model terbaik (early stopping logic)
        if val_f1 > best_f1:
            best_f1 = val_f1
            os.makedirs(MODEL_ASC_PATH, exist_ok=True)
            model.save_pretrained(MODEL_ASC_PATH)
            dataset_full.tokenizer.save_pretrained(MODEL_ASC_PATH)
            print(f"  ✅ Model terbaik disimpan (F1={best_f1:.4f})")
    
    # Laporan akhir
    print(f"\n[ASC TRAINER] Training selesai. Best Val F1: {best_f1:.4f}")
    print(f"[ASC TRAINER] Target proposal: F1 ≥ 0.80")
    
    if best_f1 >= 0.80:
        print("✅ TARGET TERCAPAI!")
    else:
        print("⚠️ Butuh lebih banyak data anotasi untuk mencapai target F1 ≥ 0.80")
    
    # Simpan history
    with open(f"{MODEL_ASC_PATH}/training_history.json", "w") as f:
        json.dump(history, f, indent=2)
    
    return best_f1

if __name__ == "__main__":
    train_asc()