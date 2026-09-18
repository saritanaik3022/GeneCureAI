"""
Unit Tests for Phase 3 CNN, XGBoost, and Hybrid Models.
"""
import pytest
import os
import torch
import numpy as np

from ml.cnn.model import CRISPR1DCNN
from ml.cnn.inference import CNNInferenceService
from ml.xgboost.model import CRISPRXGBoostModel
from ml.xgboost.inference import XGBoostInferenceService
from ml.hybrid.model import CRISPRHybridModel
from ml.hybrid.inference import HybridInferenceService
from ml.inference.service import MLInferenceEngine


def test_cnn_forward_pass():
    """Verifies PyTorch 1D-CNN tensor shape and output bounds."""
    model = CRISPR1DCNN(embedding_dim=64)
    model.eval()

    # Input shape: (Batch=4, Channels=4, Length=30)
    dummy_input = torch.randn(4, 4, 30)
    with torch.no_grad():
        out = model(dummy_input)
        emb = model.forward_features(dummy_input)

    assert out.shape == (4, 1)
    assert (out >= 0.0).all() and (out <= 1.0).all()
    assert emb.shape == (4, 64)


def test_xgboost_model_predict_and_bounds():
    """Verifies XGBoost model prediction on 105-dim feature matrix."""
    xgb_service = XGBoostInferenceService()
    assert xgb_service.is_ready is True

    seqs = [
        "CAGAAAAAAAAACACTGCAACAAGAGGGTA",
        "TTTTAAAAAACCTACCGTAAACTCGGGTCA"
    ]
    preds = xgb_service.predict_sequences(seqs)
    assert len(preds) == 2
    assert (preds >= 0.0).all() and (preds <= 1.0).all()


def test_hybrid_model_predict():
    """Verifies Hybrid model inference and 169-dimensional embedding handling."""
    hybrid_service = HybridInferenceService()
    assert hybrid_service.is_ready is True

    seqs = [
        "CAGAAAAAAAAACACTGCAACAAGAGGGTA",
        "TCAGAAAAAGCAGCGTCAGTGGATTGGCCC"
    ]
    preds = hybrid_service.predict(seqs)
    assert len(preds) == 2
    assert (preds >= 0.0).all() and (preds <= 1.0).all()


def test_ml_inference_engine_real():
    """Verifies unified MLInferenceEngine on 30-mer context."""
    engine = MLInferenceEngine()
    assert engine.is_ready is True

    seq = "CAGAAAAAAAAACACTGCAACAAGAGGGTA"
    res = engine.predict_single_guide(seq)

    assert res["mode"] == "REAL"
    assert res["sequence_30nt"] == seq
    assert res["guide_20nt"] == "AAAAAAAACACTGCAACAAG"
    assert res["pam"] == "AGG"
    assert "cnn_score" in res
    assert "xgboost_score" in res
    assert "hybrid_score" in res
    assert 0.0 <= res["predicted_on_target_efficiency"] <= 1.0
    assert res["confidence_tier"] in ["High", "Moderate", "Low"]


def test_ml_inference_engine_insufficient_context():
    """Verifies that short sequences return INSUFFICIENT_SEQUENCE_CONTEXT."""
    engine = MLInferenceEngine()
    res = engine.predict_single_guide("ACGTACGT")
    assert res["error"] == "INSUFFICIENT_SEQUENCE_CONTEXT"
