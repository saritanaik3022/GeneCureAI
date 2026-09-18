"""
Pydantic schemas for TOPSIS Multi-Criteria Decision Ranking.
"""
from typing import List, Optional, Dict
from pydantic import BaseModel, Field, model_validator, ConfigDict


class TOPSISWeights(BaseModel):
    w_on_target: float = Field(default=0.35, ge=0.0, le=1.0)
    w_off_target: float = Field(default=0.30, ge=0.0, le=1.0)
    w_cancer_relevance: float = Field(default=0.20, ge=0.0, le=1.0)
    w_gc_optimality: float = Field(default=0.15, ge=0.0, le=1.0)

    @model_validator(mode="after")
    def check_weights_sum(self):
        total = self.w_on_target + self.w_off_target + self.w_cancer_relevance + self.w_gc_optimality
        if not (0.99 <= total <= 1.01):
            raise ValueError(f"Weights must sum to 1.0. Current sum: {total:.3f}")
        return self


class TOPSISCandidateInput(BaseModel):
    guide_id: str
    protospacer_sequence: str
    pam: str
    strand: Optional[str] = "+"
    chromosome: Optional[str] = ""
    genomic_start: Optional[int] = None
    genomic_end: Optional[int] = None
    exon_number: Optional[int] = None
    gc_percentage: float
    on_target_score: float
    off_target_safety_score: float
    cancer_relevance_score: float
    gc_optimality_score: Optional[float] = None
    context_30nt: Optional[str] = None
    cleavage_coordinate: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)


class TOPSISRankRequest(BaseModel):
    candidates: List[TOPSISCandidateInput] = Field(default_factory=list)
    weights: TOPSISWeights = Field(default_factory=TOPSISWeights)


class TOPSISRankedItem(BaseModel):
    rank: int
    guide_id: str
    protospacer_sequence: str
    pam: str
    strand: Optional[str] = "+"
    chromosome: Optional[str] = ""
    genomic_start: Optional[int] = None
    genomic_end: Optional[int] = None
    exon_number: Optional[int] = None
    gc_content: Optional[float] = None
    closeness_score: float = Field(..., ge=0.0, le=1.0)
    distance_positive_ideal: float
    distance_negative_ideal: float
    on_target_criterion: float
    off_target_criterion: float
    cancer_relevance_criterion: float
    gc_optimality_criterion: float
    context_30nt: Optional[str] = None
    cleavage_coordinate: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)


class TOPSISRankResponse(BaseModel):
    total_ranked: int
    weights_applied: TOPSISWeights
    ranked_guides: List[TOPSISRankedItem]
    model_config = ConfigDict(from_attributes=True)
