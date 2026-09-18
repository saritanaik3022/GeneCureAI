"""
Phase 5B Unit Tests — TOPSIS Mathematical Engine Validation.
Validates vector normalization, ideal solutions, Euclidean separation distances, and closeness ranking.
"""
import pytest
import numpy as np
from backend.app.services.topsis_service import TOPSISService, topsis_service


class TestTOPSISMathematicalCore:
    def test_default_weights_sum_to_one(self):
        """Default weights (0.35, 0.30, 0.20, 0.15) must sum exactly to 1.0."""
        weights = topsis_service.DEFAULT_WEIGHTS
        assert np.isclose(np.sum(weights), 1.0), f"Weights sum {np.sum(weights)} != 1.0"

    def test_gc_optimality_function(self):
        """Validates linear/triangular GC optimality calculation around 50% target."""
        # 50% GC -> 1.0
        assert TOPSISService.calculate_gc_optimality(50.0) == 1.0
        # 40% GC -> 1.0 - 2 * 0.10 = 0.80
        assert TOPSISService.calculate_gc_optimality(40.0) == 0.80
        # 60% GC -> 1.0 - 2 * 0.10 = 0.80
        assert TOPSISService.calculate_gc_optimality(60.0) == 0.80
        # 30% GC -> 1.0 - 2 * 0.20 = 0.60
        assert TOPSISService.calculate_gc_optimality(30.0) == 0.60
        # 0% and 100% GC -> 0.0
        assert TOPSISService.calculate_gc_optimality(0.0) == 0.0
        assert TOPSISService.calculate_gc_optimality(100.0) == 0.0

    def test_known_reference_matrix_ranking(self):
        """
        Validates TOPSIS execution on a controlled reference matrix.
        Candidate A dominates Candidate B across all benefit criteria.
        """
        # Candidate 1: High scores across all 4 criteria
        # Candidate 2: Moderate scores
        # Candidate 3: Low scores
        matrix = np.array([
            [0.90, 0.95, 0.85, 0.90], # Dominant candidate
            [0.60, 0.70, 0.50, 0.60], # Moderate candidate
            [0.30, 0.40, 0.20, 0.30], # Weak candidate
        ], dtype=float)

        weights = np.array([0.35, 0.30, 0.20, 0.15])
        result = topsis_service.run_topsis(matrix, weights=weights)

        closeness = result["closeness_scores"]
        ranks = result["ranks"]

        # Candidate 1 should be rank 1 with highest closeness
        assert ranks[0] == 1, f"Expected Candidate 1 to be rank 1, got {ranks[0]}"
        assert ranks[1] == 2
        assert ranks[2] == 3

        # Closeness scores must be monotonically decreasing
        assert closeness[0] > closeness[1] > closeness[2]
        assert all(0.0 <= c <= 1.0 for c in closeness)

    def test_closeness_bounds_and_properties(self):
        """Closeness score C_i must strictly reside in [0.0, 1.0]."""
        matrix = np.random.uniform(0.1, 1.0, size=(10, 4))
        result = topsis_service.run_topsis(matrix)

        assert len(result["closeness_scores"]) == 10
        assert all(0.0 <= c <= 1.0 for c in result["closeness_scores"])
        assert len(np.unique(result["ranks"])) == 10 # All ranks 1..10 present

    def test_explain_rank_structure(self):
        """explain_rank must return criterion distances and transparent breakdown."""
        matrix = np.array([
            [0.85, 0.92, 0.78, 0.88],
            [0.65, 0.70, 0.55, 0.60]
        ])
        res = topsis_service.run_topsis(matrix)
        explanation = topsis_service.explain_rank(0, [0.85, 0.92, 0.78, 0.88], res)

        assert "rank" in explanation
        assert "topsis_score" in explanation
        assert "criteria_breakdown" in explanation
        assert len(explanation["criteria_breakdown"]) == 4
