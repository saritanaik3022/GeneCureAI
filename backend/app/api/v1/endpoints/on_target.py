"""
Stage 3: Hybrid On-Target ML Efficiency Prediction endpoints.
"""
from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any
from app.schemas.prediction import OnTargetPredictRequest, OnTargetPredictResponse, SingleOnTargetPrediction
from app.services.on_target_service import OnTargetService
from app.core.config import settings

router = APIRouter()


@router.post("/predict", tags=["Stage 3: On-Target Prediction"])
async def predict_on_target_efficiency(request: OnTargetPredictRequest):
    """
    Computes on-target efficiency using 1D-CNN sequence representations,
    105 engineered bio-physicochemical features, and Hybrid stacking regressor.
    """
    result = OnTargetService.predict_guides(
        guides_30nt=request.guides_30nt,
        execution_mode=settings.EXECUTION_MODE
    )

    if result.get("error") == "MODEL_NOT_READY":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "MODEL_NOT_READY",
                "message": result.get("message", "ML models have not been trained yet.")
            }
        )

    if result.get("error") == "INSUFFICIENT_SEQUENCE_CONTEXT":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "INSUFFICIENT_SEQUENCE_CONTEXT",
                "message": result.get("message", "Expected 30-nt context sequences.")
            }
        )

    return result


@router.get("/performance", tags=["Stage 3: On-Target Prediction"])
async def get_model_performance():
    """
    Returns actual evaluation benchmarks and regression metrics
    for the PyTorch 1D-CNN, XGBoost, and Hybrid models.
    """
    return OnTargetService.get_model_performance()
