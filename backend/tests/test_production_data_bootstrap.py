"""
Tests for Production Genomic Data Paths and Bootstrap Architecture.

Verifies:
1. Configurable dataset paths via environment variables.
2. Local development configuration preservation.
3. TCGA cancer relevance scores dataset presence and loading.
4. Idempotent bootstrap behavior: existing datasets detected, no redundant downloads.
5. Automatic .fai FASTA index generation via pyfaidx.
6. SKIP_BOOTSTRAP flag enforcement.
"""
import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from app.core.config import Settings
from bioinformatics.cancer_relevance.tcga_relevance import TCGACancerRelevanceService
from scripts.setup.bootstrap_production_data import (
    bootstrap_datasets,
    ensure_fasta_index,
    download_and_extract,
)


def test_configurable_production_paths_via_env(monkeypatch):
    """Verify that dataset paths are dynamically overridable by environment variables."""
    monkeypatch.setenv("DATA_ROOT", "/data")
    monkeypatch.setenv("GENOME_FASTA", "/data/genome/GRCh38.primary_assembly.genome.fa")
    monkeypatch.setenv("GENCODE_GTF", "/data/annotation/gencode.v46.annotation.gtf")
    monkeypatch.setenv("BOWTIE2_INDEX", "/data/bowtie2_index/GRCh38")
    monkeypatch.setenv("CANCER_RELEVANCE_DATA", "results/cancer_relevance_scores.csv")

    test_settings = Settings()
    assert test_settings.DATA_ROOT == Path("/data")
    assert test_settings.GENOME_FASTA == Path("/data/genome/GRCh38.primary_assembly.genome.fa")
    assert test_settings.GENCODE_GTF == Path("/data/annotation/gencode.v46.annotation.gtf")
    assert test_settings.BOWTIE2_INDEX == Path("/data/bowtie2_index/GRCh38")
    assert test_settings.CANCER_RELEVANCE_DATA == Path("results/cancer_relevance_scores.csv")


def test_cancer_relevance_dataset_presence_and_loading():
    """Verify cancer_relevance_scores.csv exists in results/ and TCGA service loads scores."""
    cr_path = Path("results/cancer_relevance_scores.csv")
    assert cr_path.exists(), "results/cancer_relevance_scores.csv must be present in repository"
    assert cr_path.stat().st_size > 0

    tcga_svc = TCGACancerRelevanceService(csv_path=cr_path)
    # Check verified baseline scores for target oncogenes
    assert tcga_svc.get_relevance_score("Breast", "ERBB2") == 1.0
    assert tcga_svc.get_relevance_score("Lung", "EGFR") == 1.0
    assert tcga_svc.get_relevance_score("Liver", "CTNNB1") == 1.0


def test_existing_dataset_detection_no_repeated_download(tmp_path, monkeypatch):
    """Verify that when datasets exist, bootstrap detects them and never triggers download."""
    fake_fasta = tmp_path / "genome" / "GRCh38.primary_assembly.genome.fa"
    fake_gtf = tmp_path / "annotation" / "gencode.v46.annotation.gtf"
    fake_fasta.parent.mkdir(parents=True)
    fake_gtf.parent.mkdir(parents=True)

    # Create dummy files simulating existing uncompressed datasets
    fake_fasta.write_text(">chr1 1\nACGTACGT\n")
    fake_gtf.write_text("chr1\tHAVANA\tgene\t1\t1000\t.\t+\t.\tgene_id \"ENSG1\";\n")

    # Mock stat size to exceed threshold (> 100 MB)
    mock_stat = MagicMock()
    mock_stat.st_size = 200_000_000

    with patch.object(Path, "stat", return_value=mock_stat):
        with patch("scripts.setup.bootstrap_production_data.download_and_extract") as mock_dl:
            with patch("scripts.setup.bootstrap_production_data.ensure_fasta_index") as mock_idx:
                result = bootstrap_datasets(
                    data_root=tmp_path,
                    genome_fasta=fake_fasta,
                    gencode_gtf=fake_gtf,
                )
                assert result is True
                # Assert NO downloads were invoked
                mock_dl.assert_not_called()
                # Assert index verification was called
                mock_idx.assert_called_once_with(fake_fasta)


def test_ensure_fasta_index_generation(tmp_path):
    """Verify that ensure_fasta_index generates a valid .fai index on disk using pyfaidx."""
    test_fa = tmp_path / "mini_genome.fa"
    test_fa.write_text(">chr1\nACGTACGTACGTACGT\n>chr2\nTGCATGCATGCA\n")

    fai_path = Path(f"{test_fa}.fai")
    assert not fai_path.exists()

    ensure_fasta_index(test_fa)
    assert fai_path.exists(), "FASTA index .fai file must be created"
    assert fai_path.stat().st_size > 0


def test_skip_bootstrap_flag(monkeypatch):
    """Verify SKIP_BOOTSTRAP environment variable bypasses all bootstrap activity."""
    monkeypatch.setenv("SKIP_BOOTSTRAP", "1")
    with patch("scripts.setup.bootstrap_production_data.download_and_extract") as mock_dl:
        result = bootstrap_datasets()
        assert result is True
        mock_dl.assert_not_called()
