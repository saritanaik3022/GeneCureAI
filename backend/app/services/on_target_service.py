"""
Stage 3: Hybrid On-Target ML Efficiency Prediction Service.
Orchestrates CNN, XGBoost, and Hybrid models via MLInferenceEngine.
"""
from typing import List, Dict, Any, Optional
import os
import json
try:
    from backend.app.core.config import settings
    from backend.app.core.logging import logger
except ImportError:
    from app.core.config import settings
    from app.core.logging import logger
from ml.inference.service import inference_engine


class OnTargetService:
    """Orchestrates CNN, XGBoost, and Hybrid models for on-target scoring."""

    @staticmethod
    def predict_guides(guides_30nt: List[str], execution_mode: str = "REAL_MODE") -> Dict[str, Any]:
        """
        Runs on-target efficiency prediction for a list of 30-nt guide contexts.
        In REAL_MODE: strictly uses trained ML models (CNN, XGBoost, Hybrid).
        In DEMO_MODE: provides deterministic fallback fixtures.
        """
        if execution_mode == "REAL_MODE":
            if not inference_engine.is_ready:
                # Try reloading once in case models were just trained
                inference_engine.reload()
                if not inference_engine.is_ready:
                    return {
                        "status": "MODEL_NOT_READY",
                        "error": "MODEL_NOT_READY",
                        "message": "Real ML models have not been trained or model weights are missing.",
                        "predictions": [],
                        "total_evaluated": 0,
                        "execution_mode": execution_mode
                    }

            predictions = inference_engine.predict_batch(guides_30nt)
            
            # Check if any had context errors
            for p in predictions:
                if "error" in p:
                    return {
                        "status": p["error"],
                        "error": p["error"],
                        "message": p.get("message", "Error in sequence evaluation."),
                        "predictions": predictions,
                        "total_evaluated": len(predictions),
                        "execution_mode": execution_mode
                    }

            return {
                "status": "SUCCESS",
                "predictions": predictions,
                "total_evaluated": len(predictions),
                "model_version": "1.0.0",
                "feature_version": "gene-cure-v1-105",
                "execution_mode": execution_mode
            }
        else:
            # Deterministic DEMO_MODE fixture (isolated, never mixed)
            results = []
            for seq in guides_30nt:
                guide = seq[4:24] if len(seq) >= 24 else seq[:20]
                pam = seq[24:27] if len(seq) >= 27 else "NGG"
                results.append({
                    "mode": "DEMO",
                    "sequence_30nt": seq,
                    "guide_20nt": guide,
                    "pam": pam,
                    "cnn_score": 0.78,
                    "xgboost_score": 0.82,
                    "hybrid_score": 0.80,
                    "predicted_on_target_efficiency": 0.80,
                    "confidence_tier": "High",
                    "top_positive_features": ["Demo Seed GC Balance", "Favorable PAM Context"],
                    "top_negative_features": ["None (Demo Mode)"]
                })
            return {
                "status": "SUCCESS",
                "predictions": results,
                "total_evaluated": len(results),
                "model_version": "demo-fixture-v1",
                "feature_version": "demo-105",
                "execution_mode": execution_mode
            }

    @staticmethod
    def get_model_performance() -> Dict[str, Any]:
        """Returns saved model performance metrics from training."""
        metadata_path = "ml/models/model_metadata.json"
        if not os.path.exists(metadata_path):
            return {
                "status": "MODEL_NOT_READY",
                "message": "Model training has not been executed yet. No performance metrics available."
            }
        with open(metadata_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {
            "status": "READY",
            "metadata": data
        }
