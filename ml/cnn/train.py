"""
Training Pipeline for CRISPR PyTorch 1D-CNN.
"""
import os
import time
from typing import Dict, Any, Tuple, Optional
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

from ml.cnn.model import CRISPR1DCNN
from ml.cnn.dataset import create_dataloader
from ml.evaluation.metrics import evaluate_regression_metrics


def set_seed(seed: int = 42):
    """Sets random seeds for reproducibility."""
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)


def train_cnn_model(
    train_seqs: list,
    train_targets: list,
    val_seqs: list,
    val_targets: list,
    epochs: int = 35,
    batch_size: int = 64,
    learning_rate: float = 0.001,
    weight_decay: float = 1e-4,
    device: Optional[torch.device] = None,
    save_path: str = "ml/models/cnn/cnn_best.pt",
    seed: int = 42
) -> Tuple[CRISPR1DCNN, Dict[str, Any]]:
    """
    Trains the 1D-CNN model on the sequence dataset.
    Saves best model checkpoint based on validation loss.
    """
    set_seed(seed)
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    train_loader = create_dataloader(train_seqs, train_targets, batch_size=batch_size, shuffle=True)
    val_loader = create_dataloader(val_seqs, val_targets, batch_size=batch_size, shuffle=False)

    model = CRISPR1DCNN(embedding_dim=64).to(device)
    criterion = nn.MSELoss()
    optimizer = optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=weight_decay)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=4)

    best_val_loss = float('inf')
    best_epoch = 0
    history = {"train_loss": [], "val_loss": [], "epoch_times": []}

    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    for epoch in range(1, epochs + 1):
        t0 = time.time()
        model.train()
        running_train_loss = 0.0
        for x_batch, y_batch in train_loader:
            x_batch = x_batch.to(device)
            y_batch = y_batch.to(device)

            optimizer.zero_grad()
            preds = model(x_batch)
            loss = criterion(preds, y_batch)
            loss.backward()
            optimizer.step()

            running_train_loss += loss.item() * x_batch.size(0)

        epoch_train_loss = running_train_loss / len(train_seqs)

        # Validation
        model.eval()
        running_val_loss = 0.0
        val_preds_list = []
        val_targets_list = []

        with torch.no_grad():
            for x_batch, y_batch in val_loader:
                x_batch = x_batch.to(device)
                y_batch = y_batch.to(device)
                preds = model(x_batch)
                loss = criterion(preds, y_batch)
                running_val_loss += loss.item() * x_batch.size(0)

                val_preds_list.extend(preds.cpu().numpy().flatten())
                val_targets_list.extend(y_batch.cpu().numpy().flatten())

        epoch_val_loss = running_val_loss / len(val_seqs)
        scheduler.step(epoch_val_loss)
        epoch_time = time.time() - t0

        history["train_loss"].append(epoch_train_loss)
        history["val_loss"].append(epoch_val_loss)
        history["epoch_times"].append(epoch_time)

        if epoch_val_loss < best_val_loss:
            best_val_loss = epoch_val_loss
            best_epoch = epoch
            torch.save({
                "epoch": epoch,
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "best_val_loss": best_val_loss,
                "embedding_dim": 64,
                "framework": f"PyTorch {torch.__version__}",
                "device": str(device),
            }, save_path)

    # Load best weights
    checkpoint = torch.load(save_path, map_location=device, weights_only=True)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    train_summary = {
        "best_epoch": best_epoch,
        "best_val_loss": float(best_val_loss),
        "total_epochs": epochs,
        "history": history,
        "device": str(device),
        "save_path": save_path
    }
    return model, train_summary
