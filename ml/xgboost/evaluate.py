"""
Evaluation module for CRISPR XGBoost model.
"""
from typing import Dict, Any
import numpy as np

from ml.xgboost.model import CRISPRXGBoostModel
from ml.evaluation.metrics import evaluate_regression_metrics


def evaluate_xgboost(
    model: CRISPRXGBoostModel,
    X_test: np.ndarray,
    y_test: np.ndarray
) -> Dict[str, float]:
    """Evaluates XGBoost model on held-out test feature matrix."""
    y_pred = model.predict(X_test)
    return evaluate_regression_metrics(y_test, y_pred)
