"""
Phase 6 — FastAPI Integration Tests (TestClient HTTP layer).
Validates all 7 endpoint groups against the full ASGI application stack.
Tests run in REAL_MODE with the live GENCODE v46 + ML model stack.

Coverage:
  - /api/health
  - /api/v1/cancer-genes
  - /api/v1/guide-design/scan
  - /api/v1/on-target/predict + /performance
  - /api/v1/off-target/analyze  (REAL_MODE: 503 when Bowtie2 absent)
  - /api/v1/topsis/rank
  - /api/v1/pipeline/execute + /history + /{run_id}

Actual CancerGeneResponse fields (from cancer_gene.py):
  id, symbol, name, cancer_types (List[str]), ncbi_gene_id, ensembl_id,
  hgnc_id, chromosome, strand, genomic_start, genomic_end,
  canonical_transcript_id, cancer_relevance_summary, depmap_dependency_score,
  cds_length
"""
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    """Create a synchronous TestClient for the FastAPI app."""
    from app.main import app
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c


# =============================================================================
# 1. Health Endpoint
# =============================================================================

class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        r = client.get("/api/health")
        assert r.status_code == 200

    def test_health_response_schema(self, client):
        body = client.get("/api/health").json()
        assert body["status"] == "healthy"
        assert body["service"] == "gene-cure-ai"
        assert "version" in body
        assert "execution_mode" in body
        assert "grch38_available" in body
        assert "models_loaded" in body

    def test_health_execution_mode_valid(self, client):
        mode = client.get("/api/health").json()["execution_mode"]
        assert mode in ("REAL_MODE", "DEMO_MODE")

    def test_root_endpoint_returns_metadata(self, client):
        r = client.get("/")
        assert r.status_code == 200
        body = r.json()
        assert "name" in body
        assert "version" in body
        assert "mode" in body
        assert "disclaimer" in body


# =============================================================================
# 2. Cancer Genes Endpoint  (Stage 1)
# =============================================================================

class TestCancerGenesEndpoint:
    def test_list_all_cancer_genes(self, client):
        r = client.get("/api/v1/cancer-genes")
        assert r.status_code == 200
        genes = r.json()
        assert isinstance(genes, list)
        assert len(genes) == 9

    def test_all_9_target_symbols_present(self, client):
        genes = client.get("/api/v1/cancer-genes").json()
        symbols = {g["symbol"] for g in genes}
        expected = {"BRCA1", "HER2", "TP53", "EGFR", "KRAS", "ALK", "CTNNB1", "AXIN1", "TERT"}
        assert expected == symbols

    def test_cancer_gene_has_required_fields(self, client):
        gene = client.get("/api/v1/cancer-genes").json()[0]
        for field in ["symbol", "name", "cancer_types", "ncbi_gene_id",
                      "ensembl_id", "canonical_transcript_id", "chromosome"]:
            assert field in gene, f"Missing field: {field}"

    def test_filter_by_breast_cancer(self, client):
        r = client.get("/api/v1/cancer-genes?cancer_type=Breast")
        assert r.status_code == 200
        genes = r.json()
        assert len(genes) > 0
        for g in genes:
            assert any("Breast" in ct for ct in g["cancer_types"])

    def test_filter_by_lung_cancer(self, client):
        genes = client.get("/api/v1/cancer-genes?cancer_type=Lung").json()
        symbols = {g["symbol"] for g in genes}
        assert {"EGFR", "KRAS", "ALK"}.issubset(symbols)

    def test_filter_by_liver_cancer(self, client):
        genes = client.get("/api/v1/cancer-genes?cancer_type=Liver").json()
        symbols = {g["symbol"] for g in genes}
        assert {"CTNNB1", "AXIN1", "TERT"}.issubset(symbols)

    def test_get_single_gene_brca1(self, client):
        r = client.get("/api/v1/cancer-genes/BRCA1")
        assert r.status_code == 200
        body = r.json()
        assert body["symbol"] in ("BRCA1",)
        assert body["chromosome"] in ("chr17", "17")

    def test_get_single_gene_her2_alias(self, client):
        r = client.get("/api/v1/cancer-genes/HER2")
        assert r.status_code in (200, 404)  # May resolve ERBB2 alias

    def test_get_unknown_gene_returns_404(self, client):
        r = client.get("/api/v1/cancer-genes/UNKNOWN_GENE_XYZ")
        assert r.status_code == 404


# =============================================================================
# 3. Guide RNA Design Endpoint  (Stage 2)
# =============================================================================

class TestGuideScanEndpoint:
    def test_scan_brca1_returns_candidates(self, client):
        r = client.post("/api/v1/guide-design/scan", json={"gene_symbol": "BRCA1"})
        assert r.status_code == 200
        body = r.json()
        # Accept either list or dict with candidates
        if isinstance(body, list):
            candidates = body
        else:
            candidates = body.get("candidates", [])
        assert len(candidates) > 0

    def test_scan_candidate_structure(self, client):
        r = client.post("/api/v1/guide-design/scan", json={"gene_symbol": "EGFR"})
        assert r.status_code == 200
        body = r.json()
        candidates = body if isinstance(body, list) else body.get("candidates", [])
        c = candidates[0]
        assert len(c["protospacer_sequence"]) == 20
        assert c["pam_sequence"].endswith("GG")
        assert len(c["context_30nt_sequence"]) == 30
        assert 0.0 <= c["gc_percentage"] <= 100.0

    def test_scan_gc_filter_applied(self, client):
        r = client.post("/api/v1/guide-design/scan",
                        json={"gene_symbol": "TP53", "gc_min": 40.0, "gc_max": 70.0})
        assert r.status_code == 200
        body = r.json()
        candidates = body if isinstance(body, list) else body.get("candidates", [])
        for c in candidates:
            assert 40.0 <= c["gc_percentage"] <= 70.0

    def test_scan_egfr_returns_candidates(self, client):
        r = client.post("/api/v1/guide-design/scan", json={"gene_symbol": "EGFR"})
        assert r.status_code == 200


# =============================================================================
# 4. On-Target Prediction Endpoint  (Stage 3)
# =============================================================================

VALID_30NT_CONTEXTS = [
    "ACGTACGTACGTACGTACGTACGTACGTGG",  # 30-nt test context
    "GCATGCATGCATGCATGCATGCATGCATGG",
    "TTTTCAGCAGCAGCAGCAGCAGCAGCAGGG",
]


class TestOnTargetEndpoint:
    def test_predict_single_guide(self, client):
        r = client.post("/api/v1/on-target/predict",
                        json={"guides_30nt": [VALID_30NT_CONTEXTS[0]]})
        assert r.status_code == 200
        body = r.json()
        assert "predictions" in body
        assert len(body["predictions"]) == 1
        pred = body["predictions"][0]
        assert "hybrid_score" in pred or "predicted_on_target_efficiency" in pred or "ensemble_score" in pred

    def test_predict_batch_three_guides(self, client):
        r = client.post("/api/v1/on-target/predict",
                        json={"guides_30nt": VALID_30NT_CONTEXTS})
        assert r.status_code == 200
        preds = r.json()["predictions"]
        assert len(preds) == 3

    def test_predict_scores_in_valid_range(self, client):
        r = client.post("/api/v1/on-target/predict",
                        json={"guides_30nt": VALID_30NT_CONTEXTS})
        assert r.status_code == 200
        for pred in r.json()["predictions"]:
            score = pred.get("hybrid_score") or pred.get("predicted_on_target_efficiency") or pred.get("ensemble_score", 0.5)
            assert 0.0 <= score <= 1.0, f"Score {score} out of [0,1] range"

    def test_predict_short_sequence_returns_error(self, client):
        r = client.post("/api/v1/on-target/predict", json={"guides_30nt": ["ACGT"]})
        assert r.status_code in (400, 422)

    def test_performance_endpoint(self, client):
        r = client.get("/api/v1/on-target/performance")
        assert r.status_code == 200
        body = r.json()
        assert "status" in body
        assert body["status"] in ("READY", "MODEL_NOT_READY")

    def test_performance_shows_metrics_when_ready(self, client):
        body = client.get("/api/v1/on-target/performance").json()
        if body["status"] == "READY":
            assert "metadata" in body
            assert "metrics" in body["metadata"]
            metrics = body["metadata"]["metrics"]
            assert "Hybrid" in metrics
            hybrid = metrics["Hybrid"]
            assert "spearman_rho" in hybrid
            assert 0.0 <= hybrid["spearman_rho"] <= 1.0


# =============================================================================
# 5. Off-Target Analysis Endpoint  (Stage 4)
# =============================================================================

class TestOffTargetEndpoint:
    def test_analyze_single_guide(self, client):
        r = client.post("/api/v1/off-target/analyze",
                        json={"guide_sequences": ["GCAGCCAGATGCCTGGACAG"]})
        assert r.status_code in (200, 503)

    def test_analyze_response_schema(self, client):
        r = client.post("/api/v1/off-target/analyze",
                        json={"guide_sequences": ["GCAGCCAGATGCCTGGACAG"]})
        if r.status_code == 200:
            body = r.json()
            assert "results" in body
            assert len(body["results"]) == 1
            result = body["results"][0]
            for field in ["guide_sequence", "specificity_score", "cumulative_cfd_score",
                          "total_off_targets", "sites"]:
                assert field in result, f"Missing field: {field}"
        else:
            assert r.status_code == 503
            assert "GENOME_INDEX_NOT_AVAILABLE" in r.json().get("detail", {}).get("error", "")

    def test_specificity_score_in_valid_range(self, client):
        r = client.post("/api/v1/off-target/analyze",
                        json={"guide_sequences": ["GCAGCCAGATGCCTGGACAG"]})
        if r.status_code == 200:
            result = r.json()["results"][0]
            assert 0.0 <= result["specificity_score"] <= 100.0
            assert 0.0 <= result["normalized_safety_score"] <= 1.0
        else:
            assert r.status_code == 503

    def test_analyze_multiple_guides(self, client):
        r = client.post("/api/v1/off-target/analyze",
                        json={"guide_sequences": ["GCAGCCAGATGCCTGGACAG",
                                                   "TCCTTCCTTGCAGGAAACCA"]})
        assert r.status_code in (200, 503)
        if r.status_code == 200:
            assert len(r.json()["results"]) == 2


# =============================================================================
# 6. TOPSIS Ranking Endpoint  (Stage 5)
# =============================================================================

TOPSIS_CANDIDATES = [
    {
        "guide_id": "g1", "protospacer_sequence": "GCAGCCAGATGCCTGGACAG",
        "pam": "TGG", "strand": "+", "chromosome": "17",
        "genomic_start": 43044000, "genomic_end": 43044020,
        "exon_number": 2, "gc_percentage": 55.0,
        "on_target_score": 0.85, "off_target_safety_score": 0.92,
        "cancer_relevance_score": 0.80, "gc_optimality_score": 1.0,
        "context_30nt": "ACGTGCAGCCAGATGCCTGGACAGTGGAC",
    },
    {
        "guide_id": "g2", "protospacer_sequence": "TCCTTCCTTGCAGGAAACCA",
        "pam": "CGG", "strand": "+", "chromosome": "17",
        "genomic_start": 43044150, "genomic_end": 43044170,
        "exon_number": 3, "gc_percentage": 45.0,
        "on_target_score": 0.70, "off_target_safety_score": 0.75,
        "cancer_relevance_score": 0.65, "gc_optimality_score": 0.90,
        "context_30nt": "ATCCTCCTTCCTTGCAGGAAACCACGGCA",
    },
    {
        "guide_id": "g3", "protospacer_sequence": "GCTATTGAAAATCATTTGTG",
        "pam": "AGG", "strand": "-", "chromosome": "17",
        "genomic_start": 43044300, "genomic_end": 43044320,
        "exon_number": 4, "gc_percentage": 35.0,
        "on_target_score": 0.55, "off_target_safety_score": 0.60,
        "cancer_relevance_score": 0.50, "gc_optimality_score": 0.70,
        "context_30nt": "CAAGGCTATTGAAAATCATTTGTGAGGTT",
    },
]

DEFAULT_WEIGHTS = {
    "w_on_target": 0.35, "w_off_target": 0.30,
    "w_cancer_relevance": 0.20, "w_gc_optimality": 0.15
}


class TestTOPSISEndpoint:
    def test_rank_three_candidates(self, client):
        r = client.post("/api/v1/topsis/rank",
                        json={"candidates": TOPSIS_CANDIDATES, "weights": DEFAULT_WEIGHTS})
        assert r.status_code == 200

    def test_ranking_returns_correct_count(self, client):
        body = client.post("/api/v1/topsis/rank",
                           json={"candidates": TOPSIS_CANDIDATES, "weights": DEFAULT_WEIGHTS}).json()
        assert body["total_ranked"] == 3
        assert len(body["ranked_guides"]) == 3

    def test_top_ranked_guide_is_dominant(self, client):
        """Guide g1 dominates (highest across all criteria) — must be rank 1."""
        body = client.post("/api/v1/topsis/rank",
                           json={"candidates": TOPSIS_CANDIDATES, "weights": DEFAULT_WEIGHTS}).json()
        ranked = sorted(body["ranked_guides"], key=lambda x: x["rank"])
        assert ranked[0]["guide_id"] == "g1"
        assert ranked[0]["rank"] == 1

    def test_ranks_are_unique_sequential(self, client):
        body = client.post("/api/v1/topsis/rank",
                           json={"candidates": TOPSIS_CANDIDATES, "weights": DEFAULT_WEIGHTS}).json()
        ranks = [g["rank"] for g in body["ranked_guides"]]
        assert sorted(ranks) == [1, 2, 3]

    def test_closeness_scores_in_range(self, client):
        body = client.post("/api/v1/topsis/rank",
                           json={"candidates": TOPSIS_CANDIDATES, "weights": DEFAULT_WEIGHTS}).json()
        for g in body["ranked_guides"]:
            assert 0.0 <= g["closeness_score"] <= 1.0

    def test_weights_applied_field_in_response(self, client):
        body = client.post("/api/v1/topsis/rank",
                           json={"candidates": TOPSIS_CANDIDATES, "weights": DEFAULT_WEIGHTS}).json()
        assert "weights_applied" in body

    def test_empty_candidates_returns_zero_ranked(self, client):
        body = client.post("/api/v1/topsis/rank",
                           json={"candidates": [], "weights": DEFAULT_WEIGHTS}).json()
        assert body["total_ranked"] == 0
        assert body["ranked_guides"] == []


# =============================================================================
# 7. Full Pipeline Execution Endpoint  (All 5 Stages)
# =============================================================================

class TestPipelineEndpoint:
    def test_execute_pipeline_brca1(self, client):
        r = client.post("/api/v1/pipeline/execute",
                        json={"gene_symbol": "BRCA1", "top_n": 5})
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "COMPLETED"

    def test_pipeline_response_schema(self, client):
        body = client.post("/api/v1/pipeline/execute",
                           json={"gene_symbol": "TP53", "top_n": 3}).json()
        for field in ["run_id", "gene_symbol", "cancer_type", "execution_mode",
                      "status", "total_guides_scanned", "ranked_guides",
                      "stage_summaries", "total_execution_time_ms"]:
            assert field in body, f"Missing pipeline response field: {field}"

    def test_pipeline_has_five_stage_summaries(self, client):
        body = client.post("/api/v1/pipeline/execute",
                           json={"gene_symbol": "EGFR", "top_n": 3}).json()
        assert len(body["stage_summaries"]) == 5
        stage_nums = [s["stage_number"] for s in body["stage_summaries"]]
        assert stage_nums == [1, 2, 3, 4, 5]

    def test_pipeline_ranked_guides_count(self, client):
        body = client.post("/api/v1/pipeline/execute",
                           json={"gene_symbol": "KRAS", "top_n": 5}).json()
        assert len(body["ranked_guides"]) <= 5
        assert body["total_guides_scanned"] > 0

    def test_ranked_guide_has_topsis_fields(self, client):
        body = client.post("/api/v1/pipeline/execute",
                           json={"gene_symbol": "CTNNB1", "top_n": 3}).json()
        guide = body["ranked_guides"][0]
        for field in ["rank", "protospacer_sequence", "closeness_score",
                      "on_target_criterion", "off_target_criterion",
                      "cancer_relevance_criterion", "gc_optimality_criterion"]:
            assert field in guide, f"Missing ranked guide field: {field}"
        assert guide["rank"] == 1
        assert 0.0 <= guide["closeness_score"] <= 1.0

    def test_pipeline_run_id_stored_in_history(self, client):
        body = client.post("/api/v1/pipeline/execute",
                           json={"gene_symbol": "ALK", "top_n": 3}).json()
        run_id = body["run_id"]
        # Retrieve from history
        hist = client.get("/api/v1/pipeline/history").json()
        run_ids_in_history = [h["run_id"] for h in hist]
        assert run_id in run_ids_in_history

    def test_pipeline_run_retrievable_by_id(self, client):
        body = client.post("/api/v1/pipeline/execute",
                           json={"gene_symbol": "AXIN1", "top_n": 3}).json()
        run_id = body["run_id"]
        r = client.get(f"/api/v1/pipeline/{run_id}")
        assert r.status_code == 200
        assert r.json()["run_id"] == run_id

    def test_pipeline_unknown_run_id_returns_404(self, client):
        r = client.get("/api/v1/pipeline/run-nonexistent-xyz")
        assert r.status_code == 404

    def test_pipeline_custom_weights(self, client):
        """Custom TOPSIS weights must be accepted and reflected in response."""
        body = client.post("/api/v1/pipeline/execute", json={
            "gene_symbol": "TERT",
            "top_n": 3,
            "weights": {
                "w_on_target": 0.50, "w_off_target": 0.25,
                "w_cancer_relevance": 0.15, "w_gc_optimality": 0.10
            }
        }).json()
        assert body["status"] == "COMPLETED"
        w = body.get("weights_applied", {})
        if w:
            assert abs(w.get("w_on_target", 0) - 0.50) < 0.01
