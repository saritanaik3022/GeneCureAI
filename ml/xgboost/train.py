"""
Training pipeline for XGBoost on 105 engineered features.
"""
import os
from typing import Dict, Any, Tuple, Optional
import numpy as np

from ml.xgboost.model import CRISPRXGBoostModel
from ml.features.feature_engineering import FeatureExtractor105
from ml.evaluation.metrics import evaluate_regression_metrics


def train_xgboost_model(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
    y_val: np.ndarray,
    params: Optional[Dict[str, Any]] = None,
    save_path: str = "ml/models/xgboost/xgboost_model.json"
) -> Tuple[CRISPRXGBoostModel, Dict[str, Any]]:
    """
    Trains the XGBoost regressor on the 105 engineered features.
    Saves model artifact to disk.
    """
    model = CRISPRXGBoostModel(params=params)
    eval_set = [(X_train, y_train), (X_val, y_val)]
    model.fit(X_train, y_train, eval_set=eval_set, verbose=False)

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    model.save(save_path)

    val_preds = model.predict(X_val)
    val_metrics = evaluate_regression_metrics(y_val, val_preds)

    summary = {
        "params": model.params,
        "val_metrics": val_metrics,
        "save_path": save_path,
        "n_features": 105
    }
    return model, summary
