"""
Standalone TOPSIS (Technique for Order Preference by Similarity to Ideal Solution) Engine
"""
import numpy as np
from typing import List, Dict, Any, Tuple


def calculate_topsis_scores(
    decision_matrix: np.ndarray,
    weights: List[float],
    benefit_criteria: List[bool] = [True, True, True, True]
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Computes TOPSIS rankings for multi-criteria candidate evaluation.

    Args:
        decision_matrix: 2D numpy array of shape (m candidates, n criteria)
        weights: List of floats summing to 1.0
        benefit_criteria: List of booleans indicating if criterion is benefit (True) or cost (False)

    Returns:
        Tuple of (closeness_scores, distance_to_positive_ideal, distance_to_negative_ideal)
    """
    matrix = np.array(decision_matrix, dtype=float)
    w = np.array(weights, dtype=float)
    
    if matrix.ndim != 2:
        raise ValueError("Decision matrix must be 2-dimensional.")
    
    m, n = matrix.shape
    if len(w) != n:
        raise ValueError(f"Weights length ({len(w)}) must match number of criteria ({n}).")
    
    # 1. Vector Normalization
    col_norms = np.sqrt(np.sum(matrix ** 2, axis=0))
    col_norms[col_norms == 0] = 1.0
    r_matrix = matrix / col_norms

    # 2. Weighted Normalized Decision Matrix
    v_matrix = r_matrix * w

    # 3. Determine Positive (A+) and Negative (A-) Ideal Solutions
    a_pos = np.zeros(n)
    a_neg = np.zeros(n)
    for j in range(n):
        if benefit_criteria[j]:
            a_pos[j] = np.max(v_matrix[:, j])
            a_neg[j] = np.min(v_matrix[:, j])
        else:
            a_pos[j] = np.min(v_matrix[:, j])
            a_neg[j] = np.max(v_matrix[:, j])

    # 4. Calculate Euclidean Separation Distances
    s_pos = np.sqrt(np.sum((v_matrix - a_pos) ** 2, axis=1))
    s_neg = np.sqrt(np.sum((v_matrix - a_neg) ** 2, axis=1))

    # 5. Relative Closeness to Ideal Solution
    denom = s_pos + s_neg
    closeness = np.where(denom == 0, 0.5, s_neg / denom)

    return closeness, s_pos, s_neg
