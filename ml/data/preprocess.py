"""
Data Preprocessing Pipeline for CRISPR sgRNA Models.
Includes feature extraction, StandardScaler fitted ONLY on training split,
and one-hot sequence matrix encoding.
"""
from typing import Tuple, Dict, Any, Optional
import numpy as np
from sklearn.preprocessing import StandardScaler
from ml.features.feature_engineering import FeatureExtractor105


def one_hot_encode_sequence(sequence: str) -> np.ndarray:
    """
    Encodes nucleotide sequence of length L into (4, L) one-hot binary float32 matrix [A, C, G, T].
    """
    mapping = {'A': 0, 'C': 1, 'G': 2, 'T': 3}
    seq_upper = sequence.upper().strip()
    encoding = np.zeros((4, len(seq_upper)), dtype=np.float32)
    for i, base in enumerate(seq_upper):
        if base in mapping:
            encoding[mapping[base], i] = 1.0
    return encoding


def batch_one_hot_encode(sequences: list) -> np.ndarray:
    """
    Batch one-hot encodes a list of N sequences into an (N, 4, L) float32 tensor.
    """
    if not sequences:
        return np.empty((0, 4, 0), dtype=np.float32)
    seq_len = len(sequences[0].strip())
    tensor = np.zeros((len(sequences), 4, seq_len), dtype=np.float32)
    for i, seq in enumerate(sequences):
        tensor[i] = one_hot_encode_sequence(seq)
    return tensor


class PreprocessingPipeline:
    """
    Fits feature scaling strictly on training set and transforms feature vectors.
    """

    def __init__(self, with_scaling: bool = False):
        # Tree-based models (XGBoost) do not strictly require scaling,
        # but we provide StandardScaler option when combined with linear layers.
        self.with_scaling = with_scaling
        self.scaler: Optional[StandardScaler] = StandardScaler() if with_scaling else None
        self.is_fitted: bool = False

    def fit_transform_features(self, X_train_raw: np.ndarray) -> np.ndarray:
        """Fits scaler on training set and returns transformed features."""
        if self.with_scaling and self.scaler is not None:
            X_scaled = self.scaler.fit_transform(X_train_raw)
            self.is_fitted = True
            return X_scaled.astype(np.float32)
        self.is_fitted = True
        return X_train_raw.astype(np.float32)

    def transform_features(self, X_raw: np.ndarray) -> np.ndarray:
        """Transforms validation/test features using fitted scaler."""
        if not self.is_fitted:
            raise RuntimeError("PreprocessingPipeline must be fitted on training data before transforming test data.")
        if self.with_scaling and self.scaler is not None:
            return self.scaler.transform(X_raw).astype(np.float32)
        return X_raw.astype(np.float32)
