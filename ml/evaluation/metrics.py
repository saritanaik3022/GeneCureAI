"""
Scientific evaluation metrics for on-target CRISPR models:
Spearman correlation, Pearson correlation, MAE, RMSE, R2, ROC-AUC.
"""
from typing import Dict, Any
import numpy as np
from scipy.stats import spearmanr, pearsonr
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def evaluate_regression_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """
    Computes all standard regression metrics for CRISPR efficiency prediction.
    """
    spearman_corr, _ = spearmanr(y_true, y_pred)
    pearson_corr, _ = pearsonr(y_true, y_pred)
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)

    return {
        "spearman_rho": float(spearman_corr),
        "pearson_r": float(pearson_corr),
        "mae": float(mae),
        "rmse": float(rmse),
        "r2": float(r2)
    }
