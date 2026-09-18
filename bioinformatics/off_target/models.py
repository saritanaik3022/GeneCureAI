"""
Data models for off-target genomic alignments, CFD scoring, and specificity aggregation.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class OffTargetSite:
    """
    Represents a verified genomic off-target alignment in GRCh38.
    """
    chromosome: str
    position: int # 1-based genomic start position
    strand: str # '+' or '-'
    aligned_sequence: str # Aligned genomic sequence (20 nt protospacer)
    pam: str # Genomic PAM sequence (e.g. 'NGG', 'NAG', 'NGA')
    mismatches: int # Number of nucleotide mismatches (0..3+)
    mismatch_positions: List[int] # 1-based mismatch coordinates relative to 5' (1 to 20)
    cigar: str # CIGAR string (e.g. '20M')
    cfd_score: Optional[float] = None # Cutting Frequency Determination score [0.0, 1.0]
    annotation: str = "Intergenic" # 'Exonic' / 'Intronic' / 'Intergenic' / 'Promoter'
    risk_level: str = "LOW" # 'HIGH' (0-1 mm) / 'MEDIUM' (2 mm) / 'LOW' (3+ mm)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chromosome": self.chromosome,
            "position": self.position,
            "strand": self.strand,
            "sequence": self.aligned_sequence,
            "pam": self.pam,
            "mismatches": self.mismatches,
            "mismatch_positions": self.mismatch_positions,
            "cfd_score": round(self.cfd_score, 4) if self.cfd_score is not None else None,
            "annotation": self.annotation,
            "risk_level": self.risk_level
        }


@dataclass
class GuideOffTargetSummary:
    """
    Summary of all off-target alignments and specificity scores for a candidate guide.
    """
    guide_sequence: str # 20-nt protospacer sequence
    total_off_targets: int
    mismatch_counts: Dict[str, int] # e.g. {"0_mismatch": 0, "1_mismatch": 1, ...}
    cumulative_cfd_score: Optional[float]
    specificity_score: Optional[float] # Scale 0.0 - 100.0
    normalized_safety_score: Optional[float] # Scale 0.0 - 1.0
    sites: List[OffTargetSite] = field(default_factory=list)
    analysis_mode: str = "REAL"
    search_tool: str = "Bowtie2"
    reference_assembly: str = "GRCh38.p14"
    index_version: str = "GRCh38"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "guide_sequence": self.guide_sequence,
            "total_off_targets": self.total_off_targets,
            "mismatch_counts": self.mismatch_counts,
            "cumulative_cfd_score": round(self.cumulative_cfd_score, 4) if self.cumulative_cfd_score is not None else None,
            "specificity_score": round(self.specificity_score, 2) if self.specificity_score is not None else None,
            "normalized_safety_score": round(self.normalized_safety_score, 4) if self.normalized_safety_score is not None else None,
            "sites": [s.to_dict() for s in self.sites],
            "analysis_mode": self.analysis_mode,
            "search_tool": self.search_tool,
            "reference_genome": self.reference_assembly,
            "index_version": self.index_version
        }
