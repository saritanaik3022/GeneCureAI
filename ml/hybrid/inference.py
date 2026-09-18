"""
Inference wrapper for trained CRISPR Hybrid (CNN + XGBoost) model.
"""
import os
from typing import List, Optional
import numpy as np
import torch

from ml.cnn.model import CRISPR1DCNN
from ml.cnn.inference import CNNInferenceService
from ml.hybrid.model import CRISPRHybridModel


class HybridInferenceService:
    """Loads saved CNN and Hybrid XGBoost weights and runs real inference."""

    def __init__(
        self,
        cnn_weights_path: str = "ml/models/cnn/cnn_best.pt",
        hybrid_weights_path: str = "ml/models/hybrid/hybrid_model.json",
        device: Optional[torch.device] = None
    ):
        self.cnn_weights_path = cnn_weights_path
        self.hybrid_weights_path = hybrid_weights_path
        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model: Optional[CRISPRHybridModel] = None
        self._load_model()

    def _load_model(self):
        if not os.path.exists(self.cnn_weights_path) or not os.path.exists(self.hybrid_weights_path):
            return
        
        # Load CNN
        checkpoint = torch.load(self.cnn_weights_path, map_location=self.device, weights_only=True)
        embedding_dim = checkpoint.get("embedding_dim", 64)
        cnn = CRISPR1DCNN(embedding_dim=embedding_dim).to(self.device)
        cnn.load_state_dict(checkpoint["model_state_dict"])
        cnn.eval()

        # Load Hybrid
        self.model = CRISPRHybridModel(cnn_model=cnn, device=self.device)
        self.model.load(self.hybrid_weights_path, cnn_model=cnn)

    @property
    def is_ready(self) -> bool:
        return self.model is not None and self.model.meta_booster is not None and self.model.cnn_model is not None

    def predict(self, sequences: List[str], precomputed_features: Optional[np.ndarray] = None) -> np.ndarray:
        """Predicts on-target activity for a list of 30-nt sequences."""
        if not self.is_ready:
            raise RuntimeError(
                f"Hybrid Model is not ready. Weights not found at '{self.cnn_weights_path}' or '{self.hybrid_weights_path}'."
            )
        return self.model.predict(sequences, precomputed_features=precomputed_features)
