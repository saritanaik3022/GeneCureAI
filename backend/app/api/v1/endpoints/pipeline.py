"""
End-to-End Pipeline Execution endpoints.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any

from app.schemas.pipeline import PipelineExecutionRequest, PipelineExecutionResponse
from app.core.config import settings
try:
    from backend.app.services.pipeline_orchestrator import pipeline_orchestrator
except ImportError:
    from app.services.pipeline_orchestrator import pipeline_orchestrator

router = APIRouter()

# In-memory session run store for fast lookup
_PIPELINE_RUNS_CACHE: Dict[str, Dict[str, Any]] = {}


@router.post("/execute", response_model=PipelineExecutionResponse, tags=["5-Stage Pipeline"])
async def execute_full_pipeline(request: PipelineExecutionRequest):
    """
    Executes the full 5-stage automated CRISPR guide RNA design pipeline
    for the selected cancer gene using genuine biological computation.
    """
    custom_w = None
    if request.weights:
        custom_w = {
            "w_on_target": request.weights.w_on_target,
            "w_off_target": request.weights.w_off_target,
            "w_cancer_relevance": request.weights.w_cancer_relevance,
            "w_gc_optimality": request.weights.w_gc_optimality,
        }

    # Infer cancer type from gene if not explicitly provided
    cancer_type = request.cancer_type or "Breast"
    gene_upper = request.gene_symbol.upper()
    if not request.cancer_type:
        if gene_upper in ["EGFR", "KRAS", "ALK"]:
            cancer_type = "Lung"
        elif gene_upper in ["CTNNB1", "AXIN1", "TERT"]:
            cancer_type = "Liver"

    result = pipeline_orchestrator.execute_pipeline(
        cancer_type=cancer_type,
        gene_symbol=request.gene_symbol,
        execution_mode=settings.EXECUTION_MODE,
        top_n=request.top_n,
        custom_weights=custom_w,
        custom_sequence=request.custom_sequence
    )

    if result.get("status") == "FAILED":
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "Pipeline execution failed.")
        )

    # Store in session cache
    _PIPELINE_RUNS_CACHE[result["run_id"]] = result

    return result


@router.get("/history", tags=["5-Stage Pipeline"])
async def get_pipeline_history():
    """Returns recent pipeline execution history (most recent first)."""
    return list(_PIPELINE_RUNS_CACHE.values())[::-1]


@router.get("/{run_id}", tags=["5-Stage Pipeline"])
async def get_pipeline_run(run_id: str):
    """Retrieves specific pipeline execution run details."""
    if run_id not in _PIPELINE_RUNS_CACHE:
        raise HTTPException(status_code=404, detail=f"Pipeline run '{run_id}' not found.")
    return _PIPELINE_RUNS_CACHE[run_id]
