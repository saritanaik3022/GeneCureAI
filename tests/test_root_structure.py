"""
Tests verifying project directory structure and core exports.
"""
import os
import pytest


def test_required_directories_exist():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    expected_dirs = [
        "backend",
        "backend/app",
        "backend/app/models",
        "backend/app/schemas",
        "backend/app/api",
        "backend/app/services",
        "backend/app/core",
        "backend/app/utils",
        "ml",
        "ml/data",
        "ml/preprocessing",
        "ml/features",
        "ml/cnn",
        "ml/xgboost",
        "ml/training",
        "ml/evaluation",
        "ml/inference",
        "ml/models",
        "bioinformatics",
        "bioinformatics/gene_selection",
        "bioinformatics/grna_design",
        "bioinformatics/off_target",
        "bioinformatics/genome",
        "bioinformatics/utils",
        "ranking",
        "frontend",
        "frontend/src",
        "data",
        "data/raw",
        "data/processed",
        "data/demo",
        "data/metadata",
        "scripts",
        "docs"
    ]
    for rel_path in expected_dirs:
        full_path = os.path.join(base_dir, rel_path)
        assert os.path.isdir(full_path), f"Directory {rel_path} is missing!"


def test_105_features_length():
    from ml.features.extractor_105 import FeatureExtractor105
    seq_30nt = "ACGTGTCACCTTGTCACCTTGAGGTGGATC"
    features = FeatureExtractor105.extract_features(seq_30nt)
    assert len(features) == 105
    assert len(FeatureExtractor105.FEATURE_NAMES) == 105
