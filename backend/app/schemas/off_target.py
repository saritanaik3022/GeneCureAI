"""
Pydantic schemas for Off-Target Safety and Specificity Analysis.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class OffTargetSite(BaseModel):
    chromosome: str
    position: int
    strand: str
    sequence: str
    pam: str
    mismatches: int
    mismatch_positions: List[int]
    cfd_score: float
    annotation: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class OffTargetAnalysisRequest(BaseModel):
    guide_sequences: List[str] = Field(..., min_length=1)
    max_mismatches: int = Field(default=3, ge=0, le=5)
    tool_preference: str = Field(default="Bowtie2", description="Bowtie2 or BLAST+")


class SingleGuideOffTargetResult(BaseModel):
    guide_sequence: str
    total_off_targets: int
    mismatch_counts: Dict[str, int]
    cumulative_cfd_score: float
    specificity_score: float = Field(..., ge=0.0, le=100.0)
    normalized_safety_score: float = Field(..., ge=0.0, le=1.0)
    sites: List[OffTargetSite] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)


class OffTargetAnalysisResponse(BaseModel):
    reference_genome: str = "GRCh38.p14"
    search_tool: str
    execution_mode: str
    results: List[SingleGuideOffTargetResult]
    model_config = ConfigDict(from_attributes=True)
