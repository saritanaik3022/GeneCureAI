"""
Pydantic schemas for 5-stage End-to-End Pipeline Execution.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.topsis import TOPSISWeights, TOPSISRankedItem


class PipelineExecutionRequest(BaseModel):
    gene_symbol: str = Field(...)
    cancer_type: Optional[str] = None
    custom_sequence: Optional[str] = None
    weights: Optional[TOPSISWeights] = None
    top_n: int = Field(default=10, ge=1, le=50)


class StageSummary(BaseModel):
    stage_number: int
    stage_name: str
    status: str
    summary: str
    duration_ms: int
    model_config = ConfigDict(from_attributes=True)


class PipelineExecutionResponse(BaseModel):
    run_id: str
    gene_symbol: str
    cancer_type: Optional[str] = None
    execution_mode: str
    status: str
    total_guides_scanned: int
    ranked_count: Optional[int] = None
    ranked_guides: List[TOPSISRankedItem]
    stage_summaries: List[StageSummary]
    weights_applied: Optional[Dict[str, float]] = None
    custom_sequence: Optional[str] = None
    total_execution_time_ms: int
    disclaimer: str = (
        "This platform provides in-silico computational predictions and is not a substitute "
        "for experimental validation in molecular biology or clinical laboratories."
    )
    model_config = ConfigDict(from_attributes=True)
