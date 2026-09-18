"""
Inference wrapper for trained CRISPR 1D-CNN model.
"""
import os
from typing import List, Optional
import torch
import numpy as np

from ml.cnn.model import CRISPR1DCNN
from ml.cnn.evaluate import predict_cnn, extract_cnn_embeddings


class CNNInferenceService:
    """Loads saved PyTorch CNN weights from disk and runs inference."""

    def __init__(self, weights_path: str = "ml/models/cnn/cnn_best.pt", device: Optional[torch.device] = None):
        self.weights_path = weights_path
        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model: Optional[CRISPR1DCNN] = None
        self._load_model()

    def _load_model(self):
        if not os.path.exists(self.weights_path):
            return
        checkpoint = torch.load(self.weights_path, map_location=self.device, weights_only=True)
        embedding_dim = checkpoint.get("embedding_dim", 64)
        self.model = CRISPR1DCNN(embedding_dim=embedding_dim).to(self.device)
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.model.eval()

    @property
    def is_ready(self) -> bool:
        return self.model is not None

    def predict(self, sequences: List[str]) -> np.ndarray:
        if not self.is_ready:
            raise RuntimeError(f"CNN Model is not ready. Weights not found at '{self.weights_path}'.")
        return predict_cnn(self.model, sequences, device=self.device)

    def extract_embeddings(self, sequences: List[str]) -> np.ndarray:
        if not self.is_ready:
            raise RuntimeError(f"CNN Model is not ready. Weights not found at '{self.weights_path}'.")
        return extract_cnn_embeddings(self.model, sequences, device=self.device)
