"""
XGBoost Model configuration and wrapper for 105 engineered features.
"""
from typing import Dict, Any, Optional
import os
import numpy as np
import xgboost as xgb
from ml.features.feature_schema import TOTAL_FEATURES, FEATURE_NAMES


class CRISPRXGBoostModel:
    """
    XGBoost Regressor wrapper configured for exactly 105 bio-physicochemical features.
    """
    def __init__(self, params: Optional[Dict[str, Any]] = None):
        self.params = params or {
            "n_estimators": 450,
            "learning_rate": 0.035,
            "max_depth": 5,
            "subsample": 0.85,
            "colsample_bytree": 0.75,
            "random_state": 42,
            "n_jobs": -1,
            "objective": "reg:squarederror"
        }
        self.model: Optional[xgb.XGBRegressor] = None

    def fit(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        eval_set: Optional[list] = None,
        verbose: bool = False
    ):
        """Fits the XGBoost regressor on the N x 105 feature matrix."""
        if X_train.shape[1] != TOTAL_FEATURES:
            raise ValueError(f"Expected {TOTAL_FEATURES} features, got {X_train.shape[1]}")
        
        self.model = xgb.XGBRegressor(**self.params)
        self.model.fit(X_train, y_train, eval_set=eval_set, verbose=verbose)
        return self

    def predict(self, feature_matrix: np.ndarray) -> np.ndarray:
        """Runs prediction on N x 105 feature matrix."""
        if feature_matrix.shape[1] != TOTAL_FEATURES:
            raise ValueError(f"Feature matrix must have {TOTAL_FEATURES} columns, got {feature_matrix.shape[1]}.")
        if self.model is None:
            raise RuntimeError("XGBoost model is not trained or loaded.")
        preds = self.model.predict(feature_matrix)
        # Clip to valid [0.0, 1.0] range
        return np.clip(preds, 0.0, 1.0)

    def save(self, filepath: str = "ml/models/xgboost/xgboost_model.json"):
        """Saves the booster artifact to JSON."""
        if self.model is None:
            raise RuntimeError("Cannot save untrained model.")
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        self.model.save_model(filepath)

    def load(self, filepath: str = "ml/models/xgboost/xgboost_model.json"):
        """Loads booster artifact from JSON."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found at '{filepath}'")
        self.model = xgb.XGBRegressor()
        self.model.load_model(filepath)
