import os
import torch
from torch.utils.data import DataLoader, random_split
from transformers import AutoModelForTokenClassification, get_linear_schedule_with_warmup
from torch.optim import AdamW
from seqeval.metrics import f1_score as seq_f1
from src.dataset import DatasetATE, ID_TO_BIO
from dotenv import load_dotenv

load_dotenv()

INDOBERT_BASE  = os.getenv("INDOBERT_BASE", "indobenchmark/indobert-base-p1")
MODEL_ATE_PATH = os.getenv("MODEL_ATE_PATH", "./models/ate")
DATA_PATH      = "./data/annotated/dataset_asc.json"

LEARNING_RATE = 2e-5
BATCH_SIZE    = 8
MAX_EPOCHS    = 5
MAX_LENGTH    = 128
NUM_LABELS    = 3  # O, B-ASP, I-ASP

def decode_predictions(preds_ids, labels_ids):
    """Convert ID ke label string, abaikan -100."""
    pred_seqs, label_seqs = [], []
    
    for pred_row, label_row in zip(preds_ids, labels_ids):
        p_seq, l_seq = [], []
        for p, l in zip(pred_row, label_row):
            if l == -100:
                continue
            p_seq.append(ID_TO_BIO.get(p, "O"))
            l_seq.append(ID_TO_BIO.get(l, "O"))
        pred_seqs.append(p_seq)
        label_seqs.append(l_seq)
    
    return pred_seqs, label_seqs

def train_ate():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[ATE TRAINER] Device: {device}")
    
    dataset_full = DatasetATE(DATA_PATH, INDOBERT_BASE, MAX_LENGTH)
    print(f"[ATE TRAINER] Total samples: {len(dataset_full)}")
    
    n_val   = max(1, int(len(dataset_full) * 0.15))
    n_train = len(dataset_full) - n_val
    train_ds, val_ds = random_split(dataset_full, [n_train, n_val])
    
    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
    val_loader   = DataLoader(val_ds,   batch_size=BATCH_SIZE)
    
    model = AutoModelForTokenClassification.from_pretrained(
        INDOBERT_BASE,
        num_labels=NUM_LABELS,
        ignore_mismatched_sizes=True
    ).to(device)
    
    optimizer = AdamW(model.parameters(), lr=LEARNING_RATE, weight_decay=0.01)
    total_steps = len(train_loader) * MAX_EPOCHS
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=total_steps // 10,
        num_training_steps=total_steps
    )
    
    best_f1 = 0.0
    
    for epoch in range(MAX_EPOCHS):
        # ── Training ──────────────────────────────────────
        model.train()
        total_loss = 0
        
        for batch in train_loader:
            input_ids      = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels         = batch["labels"].to(device)
            
            optimizer.zero_grad()
            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels
            )
            outputs.loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            scheduler.step()
            total_loss += outputs.loss.item()
        
        # ── Evaluasi ──────────────────────────────────────
        model.eval()
        all_preds, all_labels = [], []
        
        with torch.no_grad():
            for batch in val_loader:
                input_ids      = batch["input_ids"].to(device)
                attention_mask = batch["attention_mask"].to(device)
                labels         = batch["labels"].to(device)
                
                outputs = model(input_ids=input_ids, attention_mask=attention_mask)
                preds   = torch.argmax(outputs.logits, dim=2)
                
                all_preds.extend(preds.cpu().numpy().tolist())
                all_labels.extend(labels.cpu().numpy().tolist())
        
        pred_seqs, label_seqs = decode_predictions(all_preds, all_labels)
        
        try:
            f1 = seq_f1(label_seqs, pred_seqs)
        except Exception:
            f1 = 0.0
        
        avg_loss = total_loss / len(train_loader)
        print(f"  Epoch {epoch+1}/{MAX_EPOCHS} | Loss: {avg_loss:.4f} | ATE F1: {f1:.4f}")
        
        if f1 > best_f1:
            best_f1 = f1
            os.makedirs(MODEL_ATE_PATH, exist_ok=True)
            model.save_pretrained(MODEL_ATE_PATH)
            print(f"  ✅ ATE Model terbaik disimpan (F1={best_f1:.4f})")
    
    print(f"\n[ATE TRAINER] Selesai. Best F1: {best_f1:.4f}")
    return best_f1

if __name__ == "__main__":
    train_ate()