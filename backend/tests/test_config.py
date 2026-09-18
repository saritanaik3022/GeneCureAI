"""
Tests for application settings and configuration.
"""
from app.core.config import Settings


def test_default_settings():
    settings = Settings()
    assert settings.APP_NAME == "Gene-Cure AI"
    assert settings.EXECUTION_MODE in ["DEMO_MODE", "REAL_MODE"]
    assert len(settings.SUPPORTED_CANCERS) == 3
    assert len(settings.INITIAL_GENE_SET) == 9
    assert round(settings.WEIGHT_ON_TARGET + settings.WEIGHT_OFF_TARGET_SAFETY + settings.WEIGHT_CANCER_RELEVANCE + settings.WEIGHT_GC_OPTIMALITY, 2) == 1.0


def test_supported_cancer_genes():
    settings = Settings()
    expected_genes = {"BRCA1", "HER2", "TP53", "EGFR", "KRAS", "ALK", "CTNNB1", "AXIN1", "TERT"}
    assert set(settings.INITIAL_GENE_SET) == expected_genes
