"""
Data Models for Candidate Guide RNA Identification and Biophysical Properties.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class CandidateGuideRNA:
    candidate_id: str
    gene_symbol: str
    gene_id: str
    transcript_id: str
    chromosome: str
    strand: str # '+' or '-' (target strand)
    protospacer_sequence: str # 20 nt (5' -> 3')
    pam_sequence: str # 3 nt (5' -> 3', e.g. TGG, CGG, AGG, GGG)
    context_30nt_sequence: str # 30 nt (4-nt 5' flank + 20-nt guide + 3-nt PAM + 3-nt 3' flank)
    genomic_start: int # 1-based inclusive
    genomic_end: int # 1-based inclusive
    exon_number: Optional[int]
    gc_percentage: float
    has_poly_t_terminator: bool
    self_complementarity_score: float
    reference_assembly: str = "GRCh38"
    annotation_source: str = "GENCODE v46"
    sequence_source: str = "GRCh38.primary_assembly.genome.fa"
    sequence_type: str = "EXONIC_CDS"
    relative_position_in_cds: Optional[int] = None
    cleavage_coordinate: Optional[int] = None # Predicted cut site 3 bp upstream of PAM


@dataclass
class GuideDesignScanResult:
    gene_symbol: str
    gene_id: str
    transcript_id: str
    chromosome: str
    strand: str
    reference_assembly: str
    annotation_source: str
    total_candidates_identified: int
    total_exons_scanned: int
    cds_length_scanned: int
    execution_mode: str
    candidates: List[CandidateGuideRNA] = field(default_factory=list)
    filter_summary: Dict[str, int] = field(default_factory=dict)
