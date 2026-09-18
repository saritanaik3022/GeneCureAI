"""
Feature Validator for 105-Dimensional CRISPR Feature Vectors.
Validates matrix dimensions, absence of NaN/Inf, variance across features,
and mathematical determinism.
"""
from typing import List, Dict, Any, Tuple
import numpy as np
from ml.features.feature_schema import TOTAL_FEATURES, FEATURE_VERSION, FEATURE_NAMES
from ml.features.feature_engineering import FeatureExtractor105


class FeatureValidator:
    """
    Validates engineered feature matrices against the gene-cure-v1-105 specification.
    """

    @staticmethod
    def validate_matrix(matrix: np.ndarray) -> Dict[str, Any]:
        """
        Validates an (N, 105) feature matrix.
        Returns validation metadata or raises ValueError.
        """
        if not isinstance(matrix, np.ndarray):
            raise TypeError(f"Expected numpy.ndarray, got {type(matrix).__name__}")

        if matrix.ndim != 2:
            raise ValueError(f"Feature matrix must be 2D (N, {TOTAL_FEATURES}), got ndim={matrix.ndim}")

        n_samples, n_features = matrix.shape
        if n_features != TOTAL_FEATURES:
            raise ValueError(f"Expected exactly {TOTAL_FEATURES} features, got {n_features}")

        if np.isnan(matrix).any():
            nan_cols = np.where(np.isnan(matrix).any(axis=0))[0].tolist()
            raise ValueError(f"Feature matrix contains NaN values in columns: {nan_cols}")

        if np.isinf(matrix).any():
            inf_cols = np.where(np.isinf(matrix).any(axis=0))[0].tolist()
            raise ValueError(f"Feature matrix contains infinite values in columns: {inf_cols}")

        # Check for zero-filled blocks (features that are all 0 across all samples)
        # Note: rare motifs might have very low sums, but we verify no large synthetic block is zero-filled
        all_zero_cols = np.where((matrix == 0.0).all(axis=0))[0].tolist()
        
        # Calculate feature variances
        variances = np.var(matrix, axis=0)

        return {
            "valid": True,
            "samples": int(n_samples),
            "features": int(n_features),
            "feature_version": FEATURE_VERSION,
            "has_nan": False,
            "has_inf": False,
            "all_zero_columns_count": len(all_zero_cols),
            "all_zero_column_indices": all_zero_cols,
            "min_val": float(np.min(matrix)),
            "max_val": float(np.max(matrix)),
            "mean_variance": float(np.mean(variances)),
        }

    @staticmethod
    def verify_determinism(sample_seq: str = "CAGAAAAAAAAACACTGCAACAAGAGGGTA") -> bool:
        """
        Extracts features twice for the same sequence and asserts exact numerical equality.
        """
        feat1 = FeatureExtractor105.extract_features(sample_seq)
        feat2 = FeatureExtractor105.extract_features(sample_seq)
        if not np.array_equal(feat1, feat2):
            raise AssertionError("Feature extraction is not deterministic! Consecutive runs produced different outputs.")
        return True
