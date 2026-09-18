"""
105-Feature Vector Extraction Strategy for CRISPR sgRNA On-Target Activity.
Strictly extracts exactly 105 engineered features following Doench 2016 Rule Set 2.
Delegates to ml.features.feature_engineering.FeatureExtractor105.
"""
from ml.features.feature_engineering import FeatureExtractor105
from ml.features.feature_schema import FEATURE_VERSION, FEATURE_NAMES, FEATURE_SCHEMA

__all__ = ["FeatureExtractor105", "FEATURE_VERSION", "FEATURE_NAMES", "FEATURE_SCHEMA"]
