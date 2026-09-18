"""
Unit tests for TOPSIS ranking algorithm.
"""
import numpy as np
import pytest
from ranking.topsis import calculate_topsis_scores


def test_topsis_basic_ranking():
    # 3 candidates, 4 criteria
    # Criteria: [On-target, Off-target safety, Cancer relevance, GC optimality]
    matrix = np.array([
        [0.90, 0.95, 0.80, 0.90],  # Candidate 1: High overall
        [0.40, 0.50, 0.40, 0.50],  # Candidate 2: Low overall
        [0.85, 0.90, 0.75, 0.85],  # Candidate 3: Medium-high
    ])
    weights = [0.35, 0.30, 0.20, 0.15]

    closeness, s_pos, s_neg = calculate_topsis_scores(matrix, weights)

    assert len(closeness) == 3
    # Candidate 1 should have highest closeness, Candidate 2 lowest
    assert closeness[0] > closeness[2] > closeness[1]
    assert 0.0 <= closeness[0] <= 1.0
    assert 0.0 <= closeness[1] <= 1.0


def test_topsis_dimension_mismatch():
    matrix = np.array([[0.9, 0.8], [0.7, 0.6]])
    weights = [0.35, 0.30, 0.20, 0.15]  # 4 weights for 2 criteria

    with pytest.raises(ValueError):
        calculate_topsis_scores(matrix, weights)
