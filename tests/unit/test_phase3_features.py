"""
Unit Tests for Phase 3 105-Feature Extraction Pipeline.
"""
import pytest
import numpy as np

from ml.features.feature_schema import FEATURE_VERSION, TOTAL_FEATURES, FEATURE_SCHEMA, FEATURE_NAMES
from ml.features.feature_engineering import FeatureExtractor105
from ml.features.feature_validator import FeatureValidator


def test_feature_count_and_version():
    """Verifies feature schema definitions and version string."""
    assert TOTAL_FEATURES == 105
    assert FEATURE_VERSION == "gene-cure-v1-105"
    assert len(FEATURE_SCHEMA) == 105
    assert len(FEATURE_NAMES) == 105


def test_single_feature_extraction():
    """Verifies feature extraction for a single 30-nt sequence."""
    seq = "CAGAAAAAAAAACACTGCAACAAGAGGGTA"
    features = FeatureExtractor105.extract_features(seq)

    assert isinstance(features, np.ndarray)
    assert features.shape == (105,)
    assert features.dtype == np.float32
    assert not np.isnan(features).any()
    assert not np.isinf(features).any()
    assert np.count_nonzero(features) > 25, "Features should not be empty"


def test_feature_determinism():
    """Verifies that consecutive extractions on identical sequence yield exact same values."""
    seq = "TTTTAAAAAACCTACCGTAAACTCGGGTCA"
    f1 = FeatureExtractor105.extract_features(seq)
    f2 = FeatureExtractor105.extract_features(seq)
    np.testing.assert_array_equal(f1, f2)
    assert FeatureValidator.verify_determinism(seq)


def test_matrix_extraction_and_validation():
    """Verifies batch matrix extraction and feature validator."""
    seqs = [
        "CAGAAAAAAAAACACTGCAACAAGAGGGTA",
        "TTTTAAAAAACCTACCGTAAACTCGGGTCA",
        "TCAGAAAAAGCAGCGTCAGTGGATTGGCCC",
        "AATAAAAAATAGGATTCCCAGCTTTGGAAG",
        "GATGAAAAATATGTAAACAGCATTTGGGAC"
    ]
    matrix = FeatureExtractor105.extract_matrix(seqs)
    assert matrix.shape == (5, 105)

    summary = FeatureValidator.validate_matrix(matrix)
    assert summary["valid"] is True
    assert summary["samples"] == 5
    assert summary["features"] == 105
    assert summary["has_nan"] is False
    assert summary["has_inf"] is False


def test_invalid_sequence_handling():
    """Verifies that invalid length or characters raise ValueError."""
    # Too short
    with pytest.raises(ValueError, match="Expected sequence length 30"):
        FeatureExtractor105.extract_features("ACGTACGT")

    # Non-DNA character
    with pytest.raises(ValueError, match="invalid non-DNA characters"):
        FeatureExtractor105.extract_features("CAGAAAAAAAAACACTGCAACAAGAGGGNX")
