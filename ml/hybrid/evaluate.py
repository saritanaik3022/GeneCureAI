"""
Evaluation module for CRISPR Hybrid model.
"""
from typing import Dict, Any, List, Optional
import numpy as np

from ml.hybrid.model import CRISPRHybridModel
from ml.evaluation.metrics import evaluate_regression_metrics


def evaluate_hybrid(
    model: CRISPRHybridModel,
    test_sequences: List[str],
    test_targets: np.ndarray,
    X_test_105: Optional[np.ndarray] = None
) -> Dict[str, float]:
    """Evaluates hybrid model on held-out test sequences."""
    y_pred = model.predict(test_sequences, precomputed_features=X_test_105)
    return evaluate_regression_metrics(test_targets, y_pred)
