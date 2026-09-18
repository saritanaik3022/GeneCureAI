"""
Inference wrapper for trained CRISPR XGBoost model.
"""
import os
from typing import List, Optional
import numpy as np

from ml.xgboost.model import CRISPRXGBoostModel
from ml.features.feature_engineering import FeatureExtractor105


class XGBoostInferenceService:
    """Loads trained XGBoost model from disk and computes predictions from 30-nt sequences or feature matrices."""

    def __init__(self, model_path: str = "ml/models/xgboost/xgboost_model.json"):
        self.model_path = model_path
        self.model: Optional[CRISPRXGBoostModel] = None
        self._load_model()

    def _load_model(self):
        if not os.path.exists(self.model_path):
            return
        self.model = CRISPRXGBoostModel()
        self.model.load(self.model_path)

    @property
    def is_ready(self) -> bool:
        return self.model is not None and self.model.model is not None

    def predict_sequences(self, sequences: List[str]) -> np.ndarray:
        """Extracts 105 features and predicts on-target scores."""
        if not self.is_ready:
            raise RuntimeError(f"XGBoost Model is not ready. Weights not found at '{self.model_path}'.")
        X = FeatureExtractor105.extract_matrix(sequences)
        return self.model.predict(X)

    def predict_features(self, feature_matrix: np.ndarray) -> np.ndarray:
        """Predicts directly from precomputed (N, 105) matrix."""
        if not self.is_ready:
            raise RuntimeError(f"XGBoost Model is not ready. Weights not found at '{self.model_path}'.")
        return self.model.predict(feature_matrix)
