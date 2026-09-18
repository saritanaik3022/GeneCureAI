"""
Training pipeline for CRISPR Hybrid (CNN + XGBoost) model.
"""
import os
from typing import Dict, Any, Tuple, Optional, List
import numpy as np
import torch

from ml.cnn.model import CRISPR1DCNN
from ml.hybrid.model import CRISPRHybridModel
from ml.evaluation.metrics import evaluate_regression_metrics


def train_hybrid_model(
    cnn_model: CRISPR1DCNN,
    train_sequences: List[str],
    train_targets: np.ndarray,
    val_sequences: List[str],
    val_targets: np.ndarray,
    X_train_105: Optional[np.ndarray] = None,
    X_val_105: Optional[np.ndarray] = None,
    params: Optional[Dict[str, Any]] = None,
    device: Optional[torch.device] = None,
    save_path: str = "ml/models/hybrid/hybrid_model.json"
) -> Tuple[CRISPRHybridModel, Dict[str, Any]]:
    """
    Trains the hybrid model by combining CNN embeddings with 105 engineered features.
    """
    hybrid = CRISPRHybridModel(cnn_model=cnn_model, meta_params=params, device=device)
    hybrid.fit(
        train_sequences=train_sequences,
        train_targets=train_targets,
        val_sequences=val_sequences,
        val_targets=val_targets,
        X_train_105=X_train_105,
        X_val_105=X_val_105,
        verbose=False
    )

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    hybrid.save(save_path)

    val_preds = hybrid.predict(val_sequences, precomputed_features=X_val_105)
    val_metrics = evaluate_regression_metrics(val_targets, val_preds)

    summary = {
        "hybrid_features_total": 169,
        "cnn_embedding_dim": 64,
        "bio_features_dim": 105,
        "val_metrics": val_metrics,
        "save_path": save_path
    }
    return hybrid, summary
