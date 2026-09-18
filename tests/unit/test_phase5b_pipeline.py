"""
Phase 5B Integration Tests — End-to-End Pipeline & TCGA Relevance Lookup.
"""
import pytest
from bioinformatics.cancer_relevance.tcga_relevance import tcga_relevance_service
from backend.app.services.pipeline_orchestrator import pipeline_orchestrator


class TestTCGACancerRelevanceService:
    def test_relevance_dataset_loaded(self):
        """TCGA dataset must load all 9 records."""
        assert tcga_relevance_service.is_available, "TCGA Cancer relevance service should be available"

    def test_all_9_cancer_genes_mapped(self):
        """All 9 genes must return valid floats in [0.0, 1.0]."""
        test_cases = [
            ("Breast", "BRCA1", 0.0000),
            ("Breast", "ERBB2", 1.0000),
            ("Breast", "HER2", 1.0000), # Alias test
            ("Breast", "TP53", 0.0795),
            ("Lung", "EGFR", 1.0000),
            ("Lung", "KRAS", 0.2392),
            ("Lung", "ALK", 0.0000),
            ("Liver", "CTNNB1", 1.0000),
            ("Liver", "AXIN1", 0.0917),
            ("Liver", "TERT", 0.0000),
        ]
        for c_type, gene, expected in test_cases:
            score = tcga_relevance_service.get_relevance_score(c_type, gene)
            assert score is not None, f"Score for ({c_type}, {gene}) should not be None"
            assert abs(score - expected) < 0.001, f"Expected {expected} for ({c_type}, {gene}), got {score}"

    def test_unsupported_gene_returns_none(self):
        """Unknown gene should return None, not fake score."""
        assert tcga_relevance_service.get_relevance_score("Breast", "UNKNOWN_GENE_123") is None


class TestPipelineOrchestrator:
    def test_execute_pipeline_brca1_real(self):
        """Executes full pipeline for BRCA1 in Breast Cancer."""
        result = pipeline_orchestrator.execute_pipeline(
            cancer_type="Breast",
            gene_symbol="BRCA1",
            top_n=5
        )
        assert result["status"] == "COMPLETED"
        assert result["gene_symbol"] == "BRCA1"
        assert result["total_guides_scanned"] > 0
        assert len(result["ranked_guides"]) <= 5
        assert len(result["stage_summaries"]) == 5

        # Check top-ranked guide fields
        top_guide = result["ranked_guides"][0]
        assert top_guide["rank"] == 1
        assert "protospacer_sequence" in top_guide
        assert "closeness_score" in top_guide
        assert "on_target_criterion" in top_guide
        assert "off_target_criterion" in top_guide
        assert "cancer_relevance_criterion" in top_guide
        assert "gc_optimality_criterion" in top_guide
        assert 0.0 <= top_guide["closeness_score"] <= 1.0

    def test_execute_pipeline_tert_liver(self):
        """Executes full pipeline for TERT in Liver Cancer."""
        result = pipeline_orchestrator.execute_pipeline(
            cancer_type="Liver",
            gene_symbol="TERT",
            top_n=3
        )
        assert result["status"] == "COMPLETED"
        assert result["total_guides_scanned"] > 0
        assert len(result["ranked_guides"]) <= 3
