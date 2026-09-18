"""
Stage 4: Off-Target Analysis & Specificity Scoring Service.
"""
from typing import List, Dict, Any


class OffTargetService:
    """Calculates Cutting Frequency Determination (CFD) and cumulative safety scores."""

    @staticmethod
    def calculate_cumulative_specificity(cfd_scores: List[float]) -> float:
        """
        Computes cumulative specificity score:
        Specificity = 100 / (100 + sum(CFD))
        """
        total_cfd = sum(cfd_scores)
        score = 100.0 / (100.0 + total_cfd)
        return round(score, 4)

    @staticmethod
    def normalize_safety_score(specificity_score: float) -> float:
        """Normalizes 0-100 specificity score to [0.0, 1.0] range for TOPSIS."""
        return round(specificity_score / 100.0, 4)
