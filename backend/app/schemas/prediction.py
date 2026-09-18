"""
Pydantic schemas for On-Target ML Efficiency Predictions.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class OnTargetPredictRequest(BaseModel):
    guides_30nt: List[str] = Field(
        ...,
        min_length=1,
        description="List of 30-nt sequences (4nt 5' + 20nt guide + 3nt PAM + 3nt 3')"
    )


class SingleOnTargetPrediction(BaseModel):
    sequence_30nt: str
    guide_20nt: str
    pam: str
    cnn_score: float = Field(..., ge=0.0, le=1.0)
    xgboost_score: float = Field(..., ge=0.0, le=1.0)
    ensemble_score: float = Field(..., ge=0.0, le=1.0)
    confidence_tier: str = Field(default="Moderate", description="High / Moderate / Low")
    top_positive_features: Optional[List[str]] = None
    top_negative_features: Optional[List[str]] = None
    model_config = ConfigDict(from_attributes=True)


class OnTargetPredictResponse(BaseModel):
    total_evaluated: int
    predictions: List[SingleOnTargetPrediction]
    model_version: str = "1.0.0"
    execution_mode: str = "DEMO_MODE"
    model_config = ConfigDict(from_attributes=True)
