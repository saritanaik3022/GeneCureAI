"""
Unified Real Machine Learning Inference Engine.
Orchestrates CNN, XGBoost, and Hybrid models for predicting on-target CRISPR guide RNA efficiency.
Strictly requires real sequence context (30-nt: 4nt 5' + 20nt guide + 3nt PAM + 3nt 3').
Returns INSUFFICIENT_SEQUENCE_CONTEXT if context is incomplete.
Returns MODEL_NOT_READY if model weights are missing in REAL_MODE.
"""
import os
import json
from typing import List, Dict, Any, Optional, Union
import numpy as np
import torch

from ml.features.feature_engineering import FeatureExtractor105
from ml.features.feature_schema import FEATURE_VERSION, TOTAL_FEATURES
from ml.cnn.inference import CNNInferenceService
from ml.xgboost.inference import XGBoostInferenceService
from ml.hybrid.inference import HybridInferenceService

DEFAULT_CNN_WEIGHTS = "ml/models/cnn/cnn_best.pt"
DEFAULT_XGB_WEIGHTS = "ml/models/xgboost/xgboost_model.json"
DEFAULT_HYBRID_WEIGHTS = "ml/models/hybrid/hybrid_model.json"
DEFAULT_METADATA_PATH = "ml/models/model_metadata.json"


class MLInferenceEngine:
    """
    Production-grade inference engine serving CNN, XGBoost, and Hybrid on-target models.
    """

    def __init__(
        self,
        cnn_path: str = DEFAULT_CNN_WEIGHTS,
        xgb_path: str = DEFAULT_XGB_WEIGHTS,
        hybrid_path: str = DEFAULT_HYBRID_WEIGHTS,
        metadata_path: str = DEFAULT_METADATA_PATH,
        device: Optional[torch.device] = None
    ):
        self.cnn_path = cnn_path
        self.xgb_path = xgb_path
        self.hybrid_path = hybrid_path
        self.metadata_path = metadata_path
        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.cnn_service = CNNInferenceService(weights_path=cnn_path, device=self.device)
        self.xgb_service = XGBoostInferenceService(model_path=xgb_path)
        self.hybrid_service = HybridInferenceService(
            cnn_weights_path=cnn_path,
            hybrid_weights_path=hybrid_path,
            device=self.device
        )

    def reload(self):
        """Reloads all model artifacts from disk."""
        self.cnn_service = CNNInferenceService(weights_path=self.cnn_path, device=self.device)
        self.xgb_service = XGBoostInferenceService(model_path=self.xgb_path)
        self.hybrid_service = HybridInferenceService(
            cnn_weights_path=self.cnn_path,
            hybrid_weights_path=self.hybrid_path,
            device=self.device
        )

    @property
    def is_ready(self) -> bool:
        """Returns True only if all required model artifacts exist and are loaded."""
        return (
            self.cnn_service.is_ready and
            self.xgb_service.is_ready and
            self.hybrid_service.is_ready
        )

    def get_metadata(self) -> Dict[str, Any]:
        """Loads and returns saved model performance metadata."""
        if os.path.exists(self.metadata_path):
            with open(self.metadata_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "status": "MODEL_NOT_READY",
            "message": "Model training metadata not found."
        }

    def predict_single_guide(
        self,
        sequence_30nt: str,
        preferred_model: str = "hybrid"
    ) -> Dict[str, Any]:
        """
        Predicts on-target efficiency for a single 30-nt sequence.
        """
        seq = sequence_30nt.strip().upper()
        if len(seq) != 30:
            return {
                "error": "INSUFFICIENT_SEQUENCE_CONTEXT",
                "message": f"Expected 30-nt sequence (4nt 5' + 20nt guide + 3nt PAM + 3nt 3'), got {len(seq)} nt.",
                "sequence_provided": seq
            }

        valid_dna = set("ACGT")
        if not set(seq).issubset(valid_dna):
            return {
                "error": "INVALID_DNA_SEQUENCE",
                "message": f"Sequence contains non-canonical nucleotides: {seq}",
                "sequence_provided": seq
            }

        if not self.is_ready:
            return {
                "error": "MODEL_NOT_READY",
                "message": "Real ML models have not been trained or model artifacts are missing."
            }

        guide_20 = seq[4:24]
        pam = seq[24:27]

        # Extract 105 engineered features
        features_105 = FeatureExtractor105.extract_features(seq)
        features_matrix = features_105.reshape(1, 105)

        # Run predictions across models
        cnn_score = float(self.cnn_service.predict([seq])[0])
        xgb_score = float(self.xgb_service.predict_features(features_matrix)[0])
        hybrid_score = float(self.hybrid_service.predict([seq], precomputed_features=features_matrix)[0])

        # Top biological drivers
        positive_features = []
        negative_features = []
        gc_seed = features_105[85]
        gc_guide = features_105[84]
        if 0.40 <= gc_guide <= 0.60:
            positive_features.append(f"Balanced Guide GC ({gc_guide*100:.0f}%)")
        else:
            negative_features.append(f"Suboptimal Guide GC ({gc_guide*100:.0f}%)")

        if features_105[104] == 1.0:
            positive_features.append("Favorable PAM-proximal GG motif")
        if features_105[100] == 1.0:
            negative_features.append("Pol III terminator motif (TTTT)")
        if features_105[101] == 1.0:
            negative_features.append("G-quadruplex risk motif (GGGG)")

        confidence_tier = "High" if hybrid_score >= 0.70 else ("Moderate" if hybrid_score >= 0.45 else "Low")

        return {
            "mode": "REAL",
            "sequence_30nt": seq,
            "guide_20nt": guide_20,
            "pam": pam,
            "feature_version": FEATURE_VERSION,
            "cnn_score": round(cnn_score, 4),
            "xgboost_score": round(xgb_score, 4),
            "hybrid_score": round(hybrid_score, 4),
            "predicted_on_target_efficiency": round(hybrid_score, 4),
            "confidence_tier": confidence_tier,
            "top_positive_features": positive_features or ["Canonical cleavage kinetics"],
            "top_negative_features": negative_features or ["None detected"]
        }

    def predict_batch(
        self,
        sequences_30nt: List[str],
        preferred_model: str = "hybrid"
    ) -> List[Dict[str, Any]]:
        """
        Batch prediction for a list of 30-nt sequences.
        """
        results = []
        for seq in sequences_30nt:
            results.append(self.predict_single_guide(seq, preferred_model=preferred_model))
        return results


# Global singleton instance
inference_engine = MLInferenceEngine()
