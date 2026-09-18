"""
PyTorch 1D-CNN sequence modeling package.
"""
from ml.cnn.model import CRISPR1DCNN
from ml.cnn.dataset import CRISPRSequenceDataset, create_dataloader
from ml.cnn.train import train_cnn_model
from ml.cnn.evaluate import evaluate_cnn, predict_cnn, extract_cnn_embeddings
from ml.cnn.inference import CNNInferenceService

__all__ = [
    "CRISPR1DCNN",
    "CRISPRSequenceDataset",
    "create_dataloader",
    "train_cnn_model",
    "evaluate_cnn",
    "predict_cnn",
    "extract_cnn_embeddings",
    "CNNInferenceService",
]
