"""
Unit tests for SpCas9 PAM scanning and candidate extraction.
"""
import pytest
from bioinformatics.grna_design.pam_scanner import SpCas9PAMScanner
from bioinformatics.grna_design.filters import GuideSequenceFilters


def test_pam_scanner_forward_strand_basic():
    """Test standard forward strand SpCas9 (NGG) scanning and 20-nt protospacer extraction."""
    scanner = SpCas9PAMScanner()
    protospacer = "ATCGATCGATCGATCGATCG"
    seq = "AAAA" + protospacer + "TGG" + "CCC"
    
    hits = scanner.scan_forward(seq, exon_chrom_start=1000)
    assert len(hits) == 1
    hit = hits[0]
    
    assert hit.protospacer_sequence == protospacer
    assert hit.pam_sequence == "TGG"
    assert hit.strand == "+"
    assert hit.context_30nt_sequence == seq
    assert hit.genomic_start == 1000 + 4
    assert hit.genomic_end == 1000 + 4 + 23 - 1
    assert hit.cleavage_coordinate == 1000 + 4 + 16


def test_pam_scanner_reverse_strand_basic():
    """Test reverse complement strand SpCas9 (CCN) scanning."""
    scanner = SpCas9PAMScanner()
    protospacer = "ATCGATCGATCGATCGATCG" # rev comp: CGATCGATCGATCGATCGAT
    sense_proto_revcomp = "CGATCGATCGATCGATCGAT"
    seq = "GTT" + "CCA" + sense_proto_revcomp + "TTTT"
    
    hits = scanner.scan_reverse(seq, exon_chrom_start=1000)
    assert len(hits) == 1
    hit = hits[0]
    
    assert hit.protospacer_sequence == protospacer
    assert hit.pam_sequence == "TGG"
    assert hit.strand == "-"
    assert hit.genomic_start == 1000 + 3
    assert hit.genomic_end == 1000 + 3 + 23 - 1


def test_pam_scanner_overlapping_pams():
    """Test detection of overlapping PAMs like GGG (giving multiple hits)."""
    scanner = SpCas9PAMScanner()
    # 25 nt upstream + GGG + 5 nt downstream
    seq = "A" * 25 + "GGG" + "C" * 5
    hits_fwd = scanner.scan_forward(seq, exon_chrom_start=1)
    assert len(hits_fwd) == 2
    assert hits_fwd[0].pam_sequence == "AGG"
    assert hits_fwd[1].pam_sequence == "GGG"


def test_biophysical_filters_gc():
    """Test GC percentage filter logic."""
    seq_50 = "ATCGATCGATCGATCGATCG" # 10 GC / 20 = 50%
    assert GuideSequenceFilters.calculate_gc_percentage(seq_50) == 50.0
    passed, _ = GuideSequenceFilters.evaluate_guide(seq_50, gc_min=40.0, gc_max=60.0)
    assert passed is True
    passed_high, _ = GuideSequenceFilters.evaluate_guide(seq_50, gc_min=60.0, gc_max=80.0)
    assert passed_high is False


def test_biophysical_filters_poly_t():
    """Test Poly-T Pol-III terminator detection (TTTT)."""
    assert GuideSequenceFilters.has_poly_t_terminator("ATCGTTTTATCGATCGATCG") is True
    assert GuideSequenceFilters.has_poly_t_terminator("ATCGTTTATCGATCGATCGT") is False


def test_biophysical_filters_self_complementarity():
    """Test self-complementarity hairpin detection."""
    palindromic = "GCGCGCGCGCGCGCGCGCGC"
    score = GuideSequenceFilters.calculate_self_complementarity(palindromic)
    assert score > 0.5
