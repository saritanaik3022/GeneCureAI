"""
Stage 5: TOPSIS Multi-Criteria Ranking Service.
Implements vector normalization, weighted Euclidean distance to ideal solutions,
relative closeness calculation, and criterion contribution explanations.
"""
import numpy as np
from typing import List, Dict, Any, Tuple, Optional


class TOPSISService:
    """
    Implements standard TOPSIS multi-attribute decision analysis
    according to Hwang & Yoon (1981).
    """

    DEFAULT_WEIGHTS = np.array([0.35, 0.30, 0.20, 0.15], dtype=float)

    @staticmethod
    def calculate_gc_optimality(gc_percentage: float) -> float:
        """
        Computes Gene-Cure AI engineered GC optimality score around 50% target.
        Score = 1.0 - min(1.0, 2.0 * abs(GC_fraction - 0.50))
        Returns float in [0.0, 1.0].
        """
        gc_frac = gc_percentage / 100.0
        opt = 1.0 - min(1.0, 2.0 * abs(gc_frac - 0.50))
        return round(float(np.clip(opt, 0.0, 1.0)), 4)

    @classmethod
    def run_topsis(
        cls,
        matrix: np.ndarray,
        weights: Optional[np.ndarray] = None,
        is_benefit: List[bool] = [True, True, True, True]
    ) -> Dict[str, Any]:
        """
        Executes standard TOPSIS algorithm on decision matrix.

        Args:
            matrix: 2D numpy array of shape (m candidates, n criteria)
            weights: 1D numpy array of shape (n,) summing to 1.0
            is_benefit: List of booleans for each criterion (True = benefit, False = cost)

        Returns:
            Dictionary containing:
            - closeness_scores: np.ndarray (m,)
            - distance_pos: np.ndarray (m,)
            - distance_neg: np.ndarray (m,)
            - normalized_matrix: np.ndarray (m, n)
            - weighted_matrix: np.ndarray (m, n)
            - ideal_pos: np.ndarray (n,)
            - ideal_neg: np.ndarray (n,)
            - ranks: np.ndarray (m,) (1-based integer ranks)
        """
        mat = np.array(matrix, dtype=float)
        if mat.ndim != 2:
            raise ValueError("Decision matrix must be 2-dimensional (m candidates x n criteria).")

        m, n = mat.shape
        if m == 0 or n == 0:
            raise ValueError("Decision matrix cannot be empty.")

        w = np.array(weights if weights is not None else cls.DEFAULT_WEIGHTS, dtype=float)
        if len(w) != n:
            raise ValueError(f"Weights length ({len(w)}) must match criteria count ({n}).")

        # Ensure weights sum to 1.0
        w_sum = np.sum(w)
        if abs(w_sum - 1.0) > 1e-4 and w_sum > 0:
            w = w / w_sum

        # Step 1: Vector Normalization
        col_norms = np.sqrt(np.sum(mat ** 2, axis=0))
        col_norms[col_norms == 0] = 1.0 # Handle zero columns
        r_matrix = mat / col_norms

        # Step 2: Weighted Normalized Matrix
        v_matrix = r_matrix * w

        # Step 3: Positive and Negative Ideal Solutions
        a_pos = np.zeros(n)
        a_neg = np.zeros(n)
        for j in range(n):
            if is_benefit[j]:
                a_pos[j] = np.max(v_matrix[:, j])
                a_neg[j] = np.min(v_matrix[:, j])
            else:
                a_pos[j] = np.min(v_matrix[:, j])
                a_neg[j] = np.max(v_matrix[:, j])

        # Step 4: Euclidean Separation Measures
        d_pos = np.sqrt(np.sum((v_matrix - a_pos) ** 2, axis=1))
        d_neg = np.sqrt(np.sum((v_matrix - a_neg) ** 2, axis=1))

        # Step 5: Relative Closeness to Ideal Solution
        total_d = d_pos + d_neg
        closeness = np.where(total_d == 0, 0.5, d_neg / total_d)

        # Step 6: Determine 1-based ranks (descending by closeness)
        order = np.argsort(-closeness)
        ranks = np.empty(m, dtype=int)
        ranks[order] = np.arange(1, m + 1)

        return {
            "closeness_scores": closeness,
            "distance_pos": d_pos,
            "distance_neg": d_neg,
            "normalized_matrix": r_matrix,
            "weighted_matrix": v_matrix,
            "ideal_pos": a_pos,
            "ideal_neg": a_neg,
            "ranks": ranks,
            "weights_applied": w
        }

    @classmethod
    def explain_rank(
        cls,
        candidate_idx: int,
        criteria_values: List[float],
        topsis_result: Dict[str, Any],
        criteria_names: List[str] = [
            "On-Target ML Efficiency",
            "Off-Target Specificity",
            "TCGA Cancer Relevance",
            "GC Content Optimality"
        ]
    ) -> Dict[str, Any]:
        """
        Generates a transparent mathematical explanation for why a guide achieved its rank.
        """
        w_mat = topsis_result["weighted_matrix"][candidate_idx]
        a_pos = topsis_result["ideal_pos"]
        a_neg = topsis_result["ideal_neg"]
        rank = int(topsis_result["ranks"][candidate_idx])
        score = float(topsis_result["closeness_scores"][candidate_idx])

        # Calculate criterion proximity to positive ideal
        criteria_breakdown = []
        for j, name in enumerate(criteria_names):
            val = float(criteria_values[j])
            weighted_val = float(w_mat[j])
            ideal_p = float(a_pos[j])
            ideal_n = float(a_neg[j])
            dist_p = float(abs(weighted_val - ideal_p))

            criteria_breakdown.append({
                "criterion": name,
                "raw_value": round(val, 4),
                "weighted_normalized": round(weighted_val, 4),
                "ideal_positive": round(ideal_p, 4),
                "ideal_negative": round(ideal_n, 4),
                "distance_to_best": round(dist_p, 4)
            })

        return {
            "rank": rank,
            "topsis_score": round(score, 4),
            "distance_to_positive_ideal": round(float(topsis_result["distance_pos"][candidate_idx]), 4),
            "distance_to_negative_ideal": round(float(topsis_result["distance_neg"][candidate_idx]), 4),
            "criteria_breakdown": criteria_breakdown
        }


# Singleton instance
topsis_service = TOPSISService()
