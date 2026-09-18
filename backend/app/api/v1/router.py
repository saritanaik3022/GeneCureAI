"""
API v1 Router aggregating all stage endpoints.
"""
from fastapi import APIRouter
from app.api.v1.endpoints import (
    health,
    cancer_genes,
    guide_design,
    on_target,
    off_target,
    topsis,
    pipeline,
)

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(cancer_genes.router, prefix="/cancer-genes", tags=["Stage 1: Cancer Genes"])
api_router.include_router(guide_design.router, prefix="/guide-design", tags=["Stage 2: Guide RNA Design"])
api_router.include_router(on_target.router, prefix="/on-target", tags=["Stage 3: On-Target Prediction"])
api_router.include_router(off_target.router, prefix="/off-target", tags=["Stage 4: Off-Target Analysis"])
api_router.include_router(topsis.router, prefix="/topsis", tags=["Stage 5: TOPSIS Ranking"])
api_router.include_router(pipeline.router, prefix="/pipeline", tags=["5-Stage Pipeline"])
