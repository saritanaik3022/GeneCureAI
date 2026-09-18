"""
Hybrid CRISPR Model Architecture.
Combines PyTorch 1D-CNN sequence embeddings (64 dimensions)
with 105 engineered biophysical features into an XGBoost stacking meta-learner (169 total dimensions).
"""
import os
import json
from typing import Dict, Any, Optional, List, Tuple
import numpy as np
import xgboost as xgb
import torch

from ml.cnn.model import CRISPR1DCNN
from ml.cnn.evaluate import extract_cnn_embeddings
from ml.features.feature_engineering import FeatureExtractor105


class CRISPRHybridModel:
    """
    Hybrid Deep Sequence + Biophysical Stacking Regressor.
    """
    def __init__(
        self,
        cnn_model: Optional[CRISPR1DCNN] = None,
        meta_params: Optional[Dict[str, Any]] = None,
        device: Optional[torch.device] = None
    ):
        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.cnn_model = cnn_model.to(self.device) if cnn_model else None
        self.meta_params = meta_params or {
            "n_estimators": 500,
            "learning_rate": 0.03,
            "max_depth": 5,
            "subsample": 0.85,
            "colsample_bytree": 0.80,
            "random_state": 42,
            "n_jobs": -1,
            "objective": "reg:squarederror"
        }
        self.meta_booster: Optional[xgb.XGBRegressor] = None

    def construct_hybrid_matrix(self, sequences: List[str], precomputed_features: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Constructs the (N, 169) hybrid representation:
        64-dimensional CNN sequence embeddings concatenated with 105 engineered biophysical features.
        """
        if self.cnn_model is None:
            raise RuntimeError("CNN model must be loaded to extract sequence embeddings.")
        
        # 1. Extract 64-dim CNN embeddings
        cnn_embeddings = extract_cnn_embeddings(self.cnn_model, sequences, device=self.device)
        
        # 2. Extract or use precomputed 105 biophysical features
        if precomputed_features is None:
            bio_features = FeatureExtractor105.extract_matrix(sequences)
        else:
            bio_features = precomputed_features
            
        if bio_features.shape[1] != 105:
            raise ValueError(f"Expected 105 engineered features, got {bio_features.shape[1]}")
            
        # 3. Concatenate along feature axis -> (N, 169)
        hybrid_matrix = np.hstack([cnn_embeddings, bio_features]).astype(np.float32)
        assert hybrid_matrix.shape[1] == 169, f"Expected 169 hybrid features, got {hybrid_matrix.shape[1]}"
        return hybrid_matrix

    def fit(
        self,
        train_sequences: List[str],
        train_targets: np.ndarray,
        val_sequences: List[str],
        val_targets: np.ndarray,
        X_train_105: Optional[np.ndarray] = None,
        X_val_105: Optional[np.ndarray] = None,
        verbose: bool = False
    ):
        """Fits the hybrid stacking booster on concatenated 169-dimensional representation."""
        X_train_hybrid = self.construct_hybrid_matrix(train_sequences, X_train_105)
        X_val_hybrid = self.construct_hybrid_matrix(val_sequences, X_val_105)

        self.meta_booster = xgb.XGBRegressor(**self.meta_params)
        eval_set = [(X_train_hybrid, train_targets), (X_val_hybrid, val_targets)]
        self.meta_booster.fit(X_train_hybrid, train_targets, eval_set=eval_set, verbose=verbose)
        return self

    def predict(self, sequences: List[str], precomputed_features: Optional[np.ndarray] = None) -> np.ndarray:
        """Predicts on-target activity for input 30-nt sequences."""
        if self.meta_booster is None:
            raise RuntimeError("Hybrid meta booster is not fitted or loaded.")
        X_hybrid = self.construct_hybrid_matrix(sequences, precomputed_features)
        preds = self.meta_booster.predict(X_hybrid)
        return np.clip(preds, 0.0, 1.0)

    def save(self, filepath: str = "ml/models/hybrid/hybrid_model.json"):
        """Saves the meta-booster artifact."""
        if self.meta_booster is None:
            raise RuntimeError("Cannot save unfitted hybrid model.")
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        self.meta_booster.save_model(filepath)

    def load(self, filepath: str = "ml/models/hybrid/hybrid_model.json", cnn_model: Optional[CRISPR1DCNN] = None):
        """Loads the meta-booster artifact and attaches CNN."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Hybrid model not found at '{filepath}'")
        if cnn_model is not None:
            self.cnn_model = cnn_model.to(self.device)
        self.meta_booster = xgb.XGBRegressor()
        self.meta_booster.load_model(filepath)
