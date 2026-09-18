"""
Gene-Cure AI - FastAPI Main Application Entrypoint
"""
import sys
from pathlib import Path

# Ensure project root directory is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import GeneCureException
from app.database import init_db
from app.api.v1.router import api_router
from app.schemas.health import HealthResponse
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown routines."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION} in {settings.EXECUTION_MODE} mode...")
    try:
        await init_db()
    except Exception as e:
        logger.warning(f"Database initialization deferred or running in lightweight mode: {e}")
    yield
    logger.info("Shutting down Gene-Cure AI service...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "A Deep Learning-Driven Platform for Automated CRISPR Guide RNA Design "
        "Targeting Breast, Lung, and Liver Cancer Therapeutics."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global Exception Handlers
@app.exception_handler(GeneCureException)
async def gene_cure_exception_handler(request: Request, exc: GeneCureException):
    logger.error(f"Application error on {request.url.path}: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
            "details": exc.details
        }
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.critical(f"Unhandled server error on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred while processing your computational request."
        }
    )


# Root and Direct Health Endpoints
@app.get("/", tags=["Root"])
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "mode": settings.EXECUTION_MODE,
        "disclaimer": (
            "This platform provides in-silico computational predictions and is not a substitute "
            "for experimental validation in molecular biology or clinical laboratories."
        ),
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
async def root_health():
    """Simple health check endpoint at /health returning status ok."""
    return {
        "status": "ok",
        "service": "gene-cure-ai",
        "version": settings.APP_VERSION,
        "execution_mode": settings.EXECUTION_MODE
    }


@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
async def direct_api_health():
    """Direct health endpoint at /api/health."""
    grch38_available = settings.is_grch38_available
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
        grch38_available=grch38_available,
        models_loaded=models_loaded
    )


# Mount API v1 Router
app.include_router(api_router, prefix=settings.API_V1_STR)
