"""
Stage 4: Off-Target Analysis & Specificity endpoints.
"""
from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any
from app.schemas.off_target import OffTargetAnalysisRequest, OffTargetAnalysisResponse, SingleGuideOffTargetResult
from app.core.config import settings
from bioinformatics.off_target.service import off_target_service

router = APIRouter()


@router.post("/analyze", tags=["Stage 4: Off-Target Analysis"])
async def analyze_off_target_safety(request: OffTargetAnalysisRequest):
    """
    Evaluates potential off-target binding sites across the human genome (GRCh38)
    and computes Cutting Frequency Determination (CFD) specificity scores.
    """
    result = off_target_service.analyze_guides(
        guide_sequences=request.guide_sequences,
        execution_mode=settings.EXECUTION_MODE,
        tool_preference=request.tool_preference
    )

    if result.get("error") == "GENOME_INDEX_NOT_AVAILABLE":
        # In REAL_MODE, if Bowtie2 index or tool is missing, return 503 status
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "GENOME_INDEX_NOT_AVAILABLE",
                "message": result.get("message", "GRCh38 Bowtie2 index is not available.")
            }
        )

    return result
