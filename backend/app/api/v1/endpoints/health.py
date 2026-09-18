"""
Health check and system status endpoint.
"""
import os
from pathlib import Path
from fastapi import APIRouter
from app.core.config import settings
from app.schemas.health import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def get_health_status():
    """
    Returns system operational health, active execution mode (DEMO_MODE vs. REAL_MODE),
    and status of dependent resources including GRCh38, GENCODE v46, and ML models.
    """
    grch38_fasta_available = settings.GENOME_FASTA.exists()
    gencode_available = settings.GENCODE_GTF.exists()
    fai_path = Path(f"{settings.GENOME_FASTA}.fai")
    genome_index_available = fai_path.exists()

    # Check if ML model weights exist locally
    models_loaded = (
        os.path.exists(settings.CNN_MODEL_WEIGHTS_PATH) and
        os.path.exists(settings.XGBOOST_MODEL_PATH)
    )

    return HealthResponse(
        status="healthy",
        service="gene-cure-ai",
        version=settings.APP_VERSION,
        execution_mode=settings.EXECUTION_MODE,
        database_connected=True,
        grch38_available=grch38_fasta_available,
        gencode_available=gencode_available,
        genome_index_available=genome_index_available,
        models_loaded=models_loaded
    )
