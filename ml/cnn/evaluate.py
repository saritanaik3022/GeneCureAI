"""
Evaluation and inference utilities for trained 1D-CNN.
"""
from typing import List, Dict, Any, Optional
import torch
import numpy as np

from ml.cnn.model import CRISPR1DCNN
from ml.cnn.dataset import create_dataloader
from ml.evaluation.metrics import evaluate_regression_metrics


def evaluate_cnn(
    model: CRISPR1DCNN,
    test_seqs: List[str],
    test_targets: List[float],
    device: Optional[torch.device] = None,
    batch_size: int = 128
) -> Dict[str, float]:
    """
    Evaluates the CNN model on test sequences and computes standard regression metrics.
    """
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = model.to(device)
    model.eval()

    loader = create_dataloader(test_seqs, batch_size=batch_size, shuffle=False)
    preds = []

    with torch.no_grad():
        for x_batch in loader:
            x_batch = x_batch.to(device)
            out = model(x_batch)
            preds.extend(out.cpu().numpy().flatten())

    y_pred = np.array(preds, dtype=np.float32)
    y_true = np.array(test_targets, dtype=np.float32)

    return evaluate_regression_metrics(y_true, y_pred)


def predict_cnn(
    model: CRISPR1DCNN,
    sequences: List[str],
    device: Optional[torch.device] = None,
    batch_size: int = 128
) -> np.ndarray:
    """Generates on-target efficiency predictions from 30-nt sequences."""
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = model.to(device)
    model.eval()

    loader = create_dataloader(sequences, batch_size=batch_size, shuffle=False)
    preds = []

    with torch.no_grad():
        for x_batch in loader:
            x_batch = x_batch.to(device)
            out = model(x_batch)
            preds.extend(out.cpu().numpy().flatten())

    return np.array(preds, dtype=np.float32)


def extract_cnn_embeddings(
    model: CRISPR1DCNN,
    sequences: List[str],
    device: Optional[torch.device] = None,
    batch_size: int = 128
) -> np.ndarray:
    """Extracts dense sequence embeddings (N, embedding_dim) from trained CNN."""
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = model.to(device)
    model.eval()

    loader = create_dataloader(sequences, batch_size=batch_size, shuffle=False)
    embeddings = []

    with torch.no_grad():
        for x_batch in loader:
            x_batch = x_batch.to(device)
            emb = model.forward_features(x_batch)
            embeddings.append(emb.cpu().numpy())

    return np.vstack(embeddings).astype(np.float32)
