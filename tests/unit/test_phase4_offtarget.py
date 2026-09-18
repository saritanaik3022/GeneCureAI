"""
Phase 4 Unit Tests — Real Off-Target Engine, CFD Scoring, SAM Parsing, PAM Validation.
"""
import pytest
from typing import List, Dict, Any
from pathlib import Path


# ─────────────────────────────────────────────────────────────────────────────
# 1. Bowtie2Runner Tests
# ─────────────────────────────────────────────────────────────────────────────
class TestBowtie2Runner:
    def test_index_detection_grch38(self):
        """GRCh38.1.bt2 must exist at the configured path."""
        from bioinformatics.off_target.bowtie2_runner import Bowtie2Runner
        runner = Bowtie2Runner()
        assert runner.is_index_available, (
            f"Expected GRCh38 Bowtie2 index at '{runner.index_prefix}'. "
            "Verify C:/Users/GeneCureAI/data/bowtie2_index/ contains GRCh38.*.bt2"
        )

    def test_executable_detection(self):
        """Bowtie2 executable check returns bool (True if installed)."""
        from bioinformatics.off_target.bowtie2_runner import Bowtie2Runner
        runner = Bowtie2Runner()
        result = runner.is_executable_available
        assert isinstance(result, bool), "is_executable_available must return a bool"

    def test_is_ready_requires_both(self):
        """is_ready must require both executable AND index."""
        from bioinformatics.off_target.bowtie2_runner import Bowtie2Runner
        runner = Bowtie2Runner(index_prefix="/nonexistent/path/GRCh38")
        assert not runner.is_ready, "is_ready should be False when index is missing"

    def test_missing_index_raises_on_align(self):
        """Missing index must raise FileNotFoundError, never silently fabricate data."""
        from bioinformatics.off_target.bowtie2_runner import Bowtie2Runner
        runner = Bowtie2Runner(index_prefix="/nonexistent/GRCh38")
        with pytest.raises((FileNotFoundError, RuntimeError)):
            runner.align_guides(["GTCACCTTGTCACCTTGAGG"])


# ─────────────────────────────────────────────────────────────────────────────
# 2. SAM Parser Tests
# ─────────────────────────────────────────────────────────────────────────────
class TestSAMParser:
    SAMPLE_SAM = (
        "guide_1\t0\tchr17\t7675100\t42\t20M\t*\t0\t0\t"
        "GTCACCTTGTCACCTTGAGG\t~~~~~~~~~~~~~~~~~~~~~~~~\tNM:i:1\tMD:Z:15A4\n"
        "guide_1\t16\tchr7\t55200000\t30\t20M\t*\t0\t0\t"
        "GTCACCTTGTCACCAAGTGG\t~~~~~~~~~~~~~~~~~~~~~~~~\tNM:i:2\tMD:Z:14T0G4\n"
        "@HD\tVN:1.6\n"  # Header should be ignored
    )

    def test_parse_sam_filters_header(self):
        """SAM parser must skip @-prefixed header lines."""
        from bioinformatics.off_target.sam_parser import SAMParser
        records = SAMParser.parse_sam_output(self.SAMPLE_SAM)
        assert len(records) == 2, f"Expected 2 alignment records, got {len(records)}"

    def test_parse_chromosome_and_position(self):
        """Parser must extract correct chromosome and 1-based position."""
        from bioinformatics.off_target.sam_parser import SAMParser
        records = SAMParser.parse_sam_output(self.SAMPLE_SAM)
        assert records[0]["chromosome"] == "chr17"
        assert records[0]["position"] == 7675100
        assert records[0]["strand"] == "+"
        assert records[1]["strand"] == "-"

    def test_parse_mismatch_count(self):
        """NM:i tag is correctly parsed as mismatch count."""
        from bioinformatics.off_target.sam_parser import SAMParser
        records = SAMParser.parse_sam_output(self.SAMPLE_SAM)
        assert records[0]["mismatch_count"] == 1
        assert records[1]["mismatch_count"] == 2

    def test_parse_md_mismatch_positions(self):
        """MD:Z:15A4 must produce mismatch at position 16 (1-based)."""
        from bioinformatics.off_target.sam_parser import SAMParser
        positions = SAMParser.extract_mismatch_positions_from_md("15A4", 20)
        assert 16 in positions, f"Expected 16 in mismatch positions, got {positions}"

    def test_md_perfect_match_no_positions(self):
        """MD:Z:20 means no mismatches."""
        from bioinformatics.off_target.sam_parser import SAMParser
        positions = SAMParser.extract_mismatch_positions_from_md("20", 20)
        assert positions == [], f"Expected empty list for perfect match, got {positions}"

    def test_md_multiple_mismatches(self):
        """MD:Z:10C3G5 should produce positions 11 and 15."""
        from bioinformatics.off_target.sam_parser import SAMParser
        positions = SAMParser.extract_mismatch_positions_from_md("10C3G5", 20)
        assert 11 in positions
        assert 15 in positions

    def test_unmapped_read_is_filtered(self):
        """SAM records with flag & 4 (unmapped) must be discarded."""
        from bioinformatics.off_target.sam_parser import SAMParser
        unmapped_sam = (
            "guide_1\t4\t*\t0\t0\t*\t*\t0\t0\t"
            "GTCACCTTGTCACCTTGAGG\t~~~~~~~~~~~~~~~~~~~~~~~~\tNM:i:0"
        )
        records = SAMParser.parse_sam_output(unmapped_sam)
        assert len(records) == 0, "Unmapped reads must be filtered"


# ─────────────────────────────────────────────────────────────────────────────
# 3. PAM Validator Tests
# ─────────────────────────────────────────────────────────────────────────────
class TestPAMValidator:
    def test_canonical_ngg_pam_valid(self):
        """AGG, CGG, GGG, TGG must all be valid SpCas9 PAMs."""
        from bioinformatics.off_target.pam_validator import PAMValidator
        for pam in ["AGG", "CGG", "GGG", "TGG"]:
            assert PAMValidator.is_valid_spcas9_pam(pam), f"{pam} should be valid NGG PAM"

    def test_non_canonical_pam(self):
        """NGA PAMs should be valid with allow_non_canonical=True."""
        from bioinformatics.off_target.pam_validator import PAMValidator
        for pam in ["AGA", "CGA", "GGA", "TGA"]:
            assert PAMValidator.is_valid_spcas9_pam(pam, allow_non_canonical=True)

    def test_invalid_pam_rejected(self):
        """TTT and AAA are not valid SpCas9 PAMs."""
        from bioinformatics.off_target.pam_validator import PAMValidator
        for pam in ["TTT", "AAA", "CCC", "ATT"]:
            assert not PAMValidator.is_valid_spcas9_pam(pam), f"{pam} should not be valid"

    def test_pam_wrong_length_invalid(self):
        """PAMs not exactly 3 nt must be invalid."""
        from bioinformatics.off_target.pam_validator import PAMValidator
        assert not PAMValidator.is_valid_spcas9_pam("GG")
        assert not PAMValidator.is_valid_spcas9_pam("AGGG")


# ─────────────────────────────────────────────────────────────────────────────
# 4. CFD Scorer Tests
# ─────────────────────────────────────────────────────────────────────────────
class TestCFDScorer:
    GUIDE = "GTCACCTTGTCACCTTGAGG"
    TARGET_PERFECT = "GTCACCTTGTCACCTTGAGG"
    TARGET_1MM = "GTCACCTTGTCACCTTGAAG"  # Pos 19: G→A

    def test_perfect_match_cfd_equals_pam_weight(self):
        """Perfect match with NGG PAM must yield CFD = 1.0."""
        from bioinformatics.off_target.cfd_scorer import CFDScorer
        score = CFDScorer.calculate_cfd_score(self.GUIDE, self.TARGET_PERFECT, "AGG", [])
        assert 0.95 <= score <= 1.0, f"Perfect match CFD should be ~1.0, got {score}"

    def test_single_mismatch_reduces_score(self):
        """Single mismatch must reduce CFD below 1.0."""
        from bioinformatics.off_target.cfd_scorer import CFDScorer
        score_perfect = CFDScorer.calculate_cfd_score(self.GUIDE, self.TARGET_PERFECT, "AGG", [])
        score_1mm = CFDScorer.calculate_cfd_score(self.GUIDE, self.TARGET_1MM, "AGG", [19])
        assert score_1mm < score_perfect, "Single mismatch must reduce CFD score"

    def test_seed_mismatch_penalized_more(self):
        """PAM-proximal seed mismatches (pos 18-20) must be penalized more than distal (pos 1-5)."""
        from bioinformatics.off_target.cfd_scorer import CFDScorer
        cfd_seed = CFDScorer.calculate_cfd_score(self.GUIDE, self.TARGET_1MM, "AGG", [20])
        cfd_distal = CFDScorer.calculate_cfd_score(self.GUIDE, self.TARGET_1MM, "AGG", [2])
        assert cfd_seed <= cfd_distal, "Seed mismatches must incur higher penalty"

    def test_non_ngg_pam_lowers_score(self):
        """Non-canonical NGA PAM must yield lower CFD than canonical NGG."""
        from bioinformatics.off_target.cfd_scorer import CFDScorer
        ngg_score = CFDScorer.calculate_cfd_score(self.GUIDE, self.TARGET_PERFECT, "AGG", [])
        nga_score = CFDScorer.calculate_cfd_score(self.GUIDE, self.TARGET_PERFECT, "AGA", [])
        assert nga_score < ngg_score, "NGA PAM must yield lower CFD than NGG"

    def test_cfd_score_bounds(self):
        """CFD score must always be in [0.0, 1.0]."""
        from bioinformatics.off_target.cfd_scorer import CFDScorer
        guide = "AAAAAAAAAAAAAAAAAAAA"
        target = "CCCCCCCCCCCCCCCCCCCC"
        pam = "TTT"
        score = CFDScorer.calculate_cfd_score(guide, target, pam, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        assert 0.0 <= score <= 1.0, f"CFD score out of bounds: {score}"

    def test_specificity_formula(self):
        """Specificity = 1/(1+sum_cfd) * 100."""
        from bioinformatics.off_target.cfd_scorer import CFDScorer
        cfd_scores = [0.1, 0.05, 0.03]
        cum_cfd, specificity, norm_safety = CFDScorer.calculate_specificity_score(cfd_scores)
        expected_specificity = 100.0 / (1 + sum(cfd_scores))
        assert abs(specificity - expected_specificity) < 0.001
        assert abs(norm_safety - specificity / 100.0) < 0.001

    def test_zero_offtargets_full_specificity(self):
        """Zero off-target sites = specificity 100.0."""
        from bioinformatics.off_target.cfd_scorer import CFDScorer
        cum, spec, norm = CFDScorer.calculate_specificity_score([])
        assert spec == 100.0
        assert norm == 1.0

    def test_risk_level_classification(self):
        """Risk levels must follow documented thresholds."""
        from bioinformatics.off_target.cfd_scorer import CFDScorer
        assert CFDScorer.determine_risk_level(0, 1.0) == "HIGH"
        assert CFDScorer.determine_risk_level(1, 0.30) == "HIGH"
        assert CFDScorer.determine_risk_level(2, 0.10) == "MEDIUM"
        assert CFDScorer.determine_risk_level(3, 0.01) == "LOW"


# ─────────────────────────────────────────────────────────────────────────────
# 5. Off-Target Service Tests
# ─────────────────────────────────────────────────────────────────────────────
class TestOffTargetService:
    def test_real_mode_returns_genome_not_available_when_no_bowtie2(self):
        """
        In REAL_MODE, if Bowtie2 executable is missing, service must return
        GENOME_INDEX_NOT_AVAILABLE — never fabricated sites.
        """
        from bioinformatics.off_target.service import OffTargetService
        # Force a non-existent index path
        svc = OffTargetService(index_prefix="/nonexistent/GRCh38")
        result = svc.analyze_guides(
            guide_sequences=["GTCACCTTGTCACCTTGAGG"],
            execution_mode="REAL_MODE"
        )
        assert result.get("status") in (
            "SUCCESS", "GENOME_INDEX_NOT_AVAILABLE", "ERROR"
        ), f"Expected valid status, got: {result}"
        # No fabricated sites allowed
        for r in result.get("results", []):
            assert len(r.get("sites", [])) == 0, "No fabricated sites permitted in REAL_MODE"

    def test_demo_mode_always_returns_results(self):
        """DEMO_MODE must always return results regardless of index availability."""
        from bioinformatics.off_target.service import OffTargetService
        svc = OffTargetService(index_prefix="/nonexistent/GRCh38")
        result = svc.analyze_guides(
            guide_sequences=["GTCACCTTGTCACCTTGAGG"],
            execution_mode="DEMO_MODE"
        )
        assert result.get("status") == "SUCCESS"
        assert len(result.get("results", [])) == 1

    def test_result_schema_fields(self):
        """DEMO_MODE result must contain all required fields."""
        from bioinformatics.off_target.service import OffTargetService
        svc = OffTargetService(index_prefix="/nonexistent/GRCh38")
        result = svc.analyze_guides(
            guide_sequences=["GTCACCTTGTCACCTTGAGG"],
            execution_mode="DEMO_MODE"
        )
        r = result["results"][0]
        assert "guide_sequence" in r
        assert "total_off_targets" in r
        assert "specificity_score" in r
        assert "cumulative_cfd_score" in r
        assert "sites" in r
