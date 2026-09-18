"""
Pydantic schemas for candidate Guide RNA design (Phase 2 real bioinformatics).
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class GuideRNABase(BaseModel):
    protospacer_sequence: str = Field(..., min_length=20, max_length=20)
    pam_sequence: str = Field(..., min_length=3, max_length=3)
    context_30nt_sequence: str = Field(..., min_length=23, max_length=40)
    strand: str = Field(..., pattern="^[+-]$")
    genomic_start: int = Field(...)
    genomic_end: int = Field(...)
    exon_number: Optional[int] = Field(None)
    gc_percentage: float = Field(...)
    has_poly_t_terminator: bool = Field(default=False)
    self_complementarity_score: float = Field(default=0.0)


class GuideRNAScanRequest(BaseModel):
    sequence: Optional[str] = Field(None, description="Custom DNA sequence to scan (optional if gene_symbol provided)")
    gene_symbol: Optional[str] = Field(None, description="Target cancer gene symbol (e.g. BRCA1)")
    gc_min: float = Field(default=20.0, ge=0.0, le=100.0)
    gc_max: float = Field(default=80.0, ge=0.0, le=100.0)
    exclude_poly_t: bool = Field(default=True, description="Filter out guides with TTTT Pol-III terminators")


class GuideRNAResponse(GuideRNABase):
    id: str
    gene_id: Optional[str] = None
    run_id: Optional[str] = None
    chromosome: Optional[str] = None
    reference_assembly: Optional[str] = None
    annotation_source: Optional[str] = None
    sequence_type: Optional[str] = None
    cleavage_coordinate: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)


class GuideDesignScanResponse(BaseModel):
    """Full scan result including provenance metadata."""
    mode: str = Field(default="REAL", description="REAL or DEMO")
    gene: str = Field(...)
    gene_id: str = Field(...)
    genome: str = Field(default="GRCh38")
    annotation: str = Field(default="GENCODE v46")
    transcript: str = Field(...)
    chromosome: str = Field(...)
    strand: str = Field(...)
    sequence_type: str = Field(default="EXONIC_CDS")
    total_exons_scanned: int = Field(...)
    cds_length_scanned: int = Field(...)
    candidate_count: int = Field(...)
    candidates: List[GuideRNAResponse] = Field(default_factory=list)
    filter_summary: Dict[str, Any] = Field(default_factory=dict)
