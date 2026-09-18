"""
Integration tests for Phase 2 Real Bioinformatics Engine against actual GENCODE v46 + GRCh38.
"""
import pytest
from app.services.bioinformatics_service import bioinformatics_service
from bioinformatics.gene_selection.gene_lookup import GeneLookup
from bioinformatics.grna_design.candidate_generator import CandidateGenerator


TARGET_GENES = ["BRCA1", "HER2", "TP53", "EGFR", "KRAS", "ALK", "CTNNB1", "AXIN1", "TERT"]


def test_gene_lookup_all_nine_genes():
    """Verify all 9 curated cancer target genes resolve deterministically in GENCODE v46."""
    lookup = GeneLookup(gtf_path=bioinformatics_service.gtf_parser.gtf_path)
    for gene in TARGET_GENES:
        resolved = lookup.get_gene_details(gene)
        assert resolved.gene_symbol in (gene, "ERBB2" if gene == "HER2" else gene)
        assert resolved.transcript_id.startswith("ENST")
        assert len(resolved.exons) > 0
        assert resolved.total_cds_length > 0


def test_real_sequence_extraction_and_scanning_brca1():
    """Verify BRCA1 sequence extraction and SpCas9 candidate identification."""
    generator = CandidateGenerator()
    result = generator.generate_candidates_for_gene("BRCA1", gc_min=20.0, gc_max=80.0, exclude_poly_t=True)
    
    assert result.gene_symbol == "BRCA1"
    assert result.chromosome in ("chr17", "17")
    assert result.strand == "-"
    assert result.total_exons_scanned == 22  # 22 CDS exons in canonical transcript ENST00000357654.9
    assert result.total_candidates_identified > 300
    
    # Check top candidate structure
    top = result.candidates[0]
    assert len(top.protospacer_sequence) == 20
    assert top.pam_sequence.endswith("GG")
    assert len(top.context_30nt_sequence) == 30
    assert 20.0 <= top.gc_percentage <= 80.0
    assert top.has_poly_t_terminator is False
    assert top.genomic_start > 0
    assert top.genomic_end > top.genomic_start
    assert top.cleavage_coordinate is not None


def test_real_sequence_extraction_and_scanning_her2():
    """Verify HER2/ERBB2 resolves and yields candidate guides."""
    generator = CandidateGenerator()
    result = generator.generate_candidates_for_gene("HER2", gc_min=20.0, gc_max=80.0, exclude_poly_t=True)
    assert result.gene_symbol in ("HER2", "ERBB2")
    assert result.total_candidates_identified > 200


def test_real_sequence_extraction_and_scanning_all_targets():
    """Verify candidate generation succeeds for every one of the 9 target cancer genes."""
    generator = CandidateGenerator()
    for gene in TARGET_GENES:
        result = generator.generate_candidates_for_gene(gene, gc_min=20.0, gc_max=80.0, exclude_poly_t=True)
        assert result.total_candidates_identified > 0, f"No candidates found for {gene}!"
        assert result.cds_length_scanned > 0, f"CDS length is 0 for {gene}!"
        assert result.total_exons_scanned > 0, f"No exons scanned for {gene}!"


def test_bioinformatics_service_cancer_genes_metadata():
    """Verify bioinformatics service returns full cancer gene metadata with sequence."""
    genes = bioinformatics_service.get_all_cancer_genes()
    assert len(genes) == 9
    symbols = {g["symbol"] for g in genes}
    assert symbols == set(TARGET_GENES)
    
    for g in genes:
        assert len(g["cds_sequence"]) > 0
        assert g["cds_length"] == len(g["cds_sequence"])
        assert g["canonical_transcript_id"].startswith("ENST")
