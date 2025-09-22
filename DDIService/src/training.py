"""
DDI Model Training Script
Extracted from the UIT challenge notebook
"""
import os
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torch.optim.lr_scheduler import ReduceLROnPlateau
import numpy as np
import pandas as pd
from tqdm import tqdm
from sklearn.metrics import roc_auc_score

from tdc.multi_pred import DDI

from .model import DeepDDIModel, FocalLoss
from .feature_extraction import smiles_to_features


class DDIDataset(Dataset):
    """Dataset class for DDI training data"""
    
    def __init__(self, df, drug2emb, num_labels, multilabel_mode):
        self.df = df.reset_index(drop=True)
        self.drug2emb = drug2emb
        self.num_labels = num_labels
        self.multilabel_mode = multilabel_mode

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        d1, d2, y = row['Drug1'], row['Drug2'], row['Y']
        x1, x2 = np.array(self.drug2emb[d1]), np.array(self.drug2emb[d2])

        if self.multilabel_mode:
            y_vec = np.array(y, dtype=np.float32)
        else:
            # build multi-hot vector from int label
            y_vec = np.zeros(self.num_labels, dtype=np.float32)
            y_vec[int(y)] = 1.0

        return torch.tensor(x1, dtype=torch.float32), torch.tensor(x2, dtype=torch.float32), torch.tensor(y_vec, dtype=np.float32)


def evaluate_auc(model, loader, device):
    """Evaluate model performance using AUROC"""
    model.eval()
    ys, ys_pred = [], []
    with torch.no_grad():
        for x1, x2, y in loader:
            x1, x2, y = x1.to(device), x2.to(device), y.to(device)
            logits = model(x1, x2)
            probs = torch.sigmoid(logits)
            ys.append(y.cpu().numpy())
            ys_pred.append(probs.cpu().numpy())

    ys = np.concatenate(ys, axis=0)
    ys_pred = np.concatenate(ys_pred, axis=0)

    aucs = []
    for i in range(ys.shape[1]):
        if len(np.unique(ys[:, i])) == 2:  # both 0 and 1 present
            auc = roc_auc_score(ys[:, i], ys_pred[:, i])
            aucs.append(auc)

    if len(aucs) == 0:
        return float("nan")
    return np.mean(aucs)


def load_and_prepare_data(dataset_name="TWOSIDES", random_seed=42, n_bits=512):
    """Load TWOSIDES dataset and prepare features"""
    print("Loading TWOSIDES dataset...")
    data = DDI(name=dataset_name)
    split = data.get_split(method="random", seed=random_seed)

    print(f"Train samples: {len(split['train'])}")
    print(f"Valid samples: {len(split['valid'])}")
    print(f"Test samples: {len(split['test'])}")

    # Inspect Y format
    first_Y = split['train']['Y'].iloc[0]
    print(f"Type of first Y: {type(first_Y)}")
    print(f"Value of first Y: {first_Y}")

    if isinstance(first_Y, (list, tuple, np.ndarray)):
        num_labels = len(first_Y)
        multilabel_mode = True
        print(f"Multi-label format detected. Number of side effects = {num_labels}")
    else:
        # fallback: Y is integer labels → compute max label id
        all_y = pd.concat([split['train']['Y'], split['valid']['Y'], split['test']['Y']])
        num_labels = int(all_y.max()) + 1
        multilabel_mode = False
        print(f"Integer label format detected. Will use {num_labels} labels (multi-class → converted to multi-label).")

    # Precompute drug features
    print("Precomputing drug features...")
    all_drugs = set(split['train']['Drug1']).union(split['train']['Drug2']) \
                 .union(split['valid']['Drug1']).union(split['valid']['Drug2']) \
                 .union(split['test']['Drug1']).union(split['test']['Drug2'])

    drug2emb = {drug: smiles_to_features(drug, n_bits=n_bits) for drug in tqdm(all_drugs, desc="Computing features")}
    emb_dim = len(next(iter(drug2emb.values())))
    print(f"Embedding dimension: {emb_dim}")

    return split, drug2emb, num_labels, multilabel_mode, emb_dim


def create_data_loaders(split, drug2emb, num_labels, multilabel_mode, batch_size=256, num_workers=2):
    """Create PyTorch DataLoaders for training, validation, and testing"""
    print("Creating data loaders...")
    
    train_dataset = DDIDataset(split['train'], drug2emb, num_labels, multilabel_mode)
    valid_dataset = DDIDataset(split['valid'], drug2emb, num_labels, multilabel_mode)
    test_dataset = DDIDataset(split['test'], drug2emb, num_labels, multilabel_mode)

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=True
    )

    valid_loader = DataLoader(
        valid_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True
    )

    return train_loader, valid_loader, test_loader, train_dataset


def train_model(
    emb_dim,
    num_labels,
    train_loader,
    valid_loader,
    train_dataset,
    model_save_path="./models/best_ddi_model.pt",
    epochs=10,
    learning_rate=1e-3,
    hidden_dim=1024,
    dropout=0.4,
    focal_alpha=2,
    focal_gamma=2,
    device=None
):
    """Train the DDI model"""
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    print(f"Using device: {device}")
    
    # Initialize model
    model = DeepDDIModel(emb_dim, num_labels, hidden_dim=hidden_dim, dropout=dropout).to(device)
    
    # Initialize loss function and optimizer
    criterion = FocalLoss(alpha=focal_alpha, gamma=focal_gamma, reduction='mean')
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    scheduler = ReduceLROnPlateau(optimizer, mode="max", factor=0.5, patience=2, verbose=True)
    
    print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")
    
    best_val = 0.0
    
    # Create models directory if it doesn't exist
    os.makedirs(os.path.dirname(model_save_path), exist_ok=True)
    
    for epoch in range(1, epochs + 1):
        model.train()
        running_loss = 0.0

        progress_bar = tqdm(train_loader, desc=f"Epoch {epoch}/{epochs}", unit="batch")

        for x1, x2, y in progress_bar:
            x1, x2, y = x1.to(device), x2.to(device), y.to(device)

            optimizer.zero_grad()
            logits = model(x1, x2)
            loss = criterion(logits, y)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * y.size(0)
            progress_bar.set_postfix(loss=loss.item())

        train_loss = running_loss / len(train_dataset)
        val_auc = evaluate_auc(model, valid_loader, device)
        scheduler.step(val_auc)

        print(f"\nEpoch {epoch}/{epochs} | Train loss: {train_loss:.4f} | Val AUROC: {val_auc:.4f}", flush=True)

        if val_auc > best_val:
            best_val = val_auc

            # move model to CPU, detach safely
            cpu_state = {k: v.detach().cpu() for k, v in model.state_dict().items()}

            # overwrite safely (atomic save)
            torch.save(cpu_state, model_save_path)

            print(f"  -> saved best model (AUROC={val_auc:.4f})")

    print(f"Training finished. Best Val AUROC: {best_val}")
    return model, best_val


def evaluate_final_model(model_path, emb_dim, num_labels, train_loader, valid_loader, test_loader, device=None):
    """Load and evaluate the final model on all splits"""
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    print("Loading and evaluating best model...")
    best_model = DeepDDIModel(emb_dim, num_labels).to(device)
    best_model.load_state_dict(torch.load(model_path, map_location=device))

    train_auc = evaluate_auc(best_model, train_loader, device)
    valid_auc = evaluate_auc(best_model, valid_loader, device)
    test_auc = evaluate_auc(best_model, test_loader, device)

    print("Final AUROC scores:")
    print(f"  Train: {train_auc:.4f}")
    print(f"  Valid: {valid_auc:.4f}")
    print(f"  Test: {test_auc:.4f}")

    return train_auc, valid_auc, test_auc


def main():
    """Main training function"""
    # Configuration
    config = {
        "dataset_name": "TWOSIDES",
        "random_seed": 42,
        "n_bits": 512,
        "batch_size": 256,
        "num_workers": 2,
        "epochs": 10,
        "learning_rate": 1e-3,
        "hidden_dim": 1024,
        "dropout": 0.4,
        "focal_alpha": 2,
        "focal_gamma": 2,
        "model_save_path": "./models/best_ddi_model.pt"
    }
    
    print("Starting DDI model training...")
    print(f"Configuration: {config}")
    
    # Load and prepare data
    split, drug2emb, num_labels, multilabel_mode, emb_dim = load_and_prepare_data(
        dataset_name=config["dataset_name"],
        random_seed=config["random_seed"],
        n_bits=config["n_bits"]
    )
    
    # Create data loaders
    train_loader, valid_loader, test_loader, train_dataset = create_data_loaders(
        split, drug2emb, num_labels, multilabel_mode,
        batch_size=config["batch_size"],
        num_workers=config["num_workers"]
    )
    
    # Train model
    model, best_val = train_model(
        emb_dim=emb_dim,
        num_labels=num_labels,
        train_loader=train_loader,
        valid_loader=valid_loader,
        train_dataset=train_dataset,
        model_save_path=config["model_save_path"],
        epochs=config["epochs"],
        learning_rate=config["learning_rate"],
        hidden_dim=config["hidden_dim"],
        dropout=config["dropout"],
        focal_alpha=config["focal_alpha"],
        focal_gamma=config["focal_gamma"]
    )
    
    # Final evaluation
    evaluate_final_model(
        config["model_save_path"],
        emb_dim,
        num_labels,
        train_loader,
        valid_loader,
        test_loader
    )


if __name__ == "__main__":
    main()