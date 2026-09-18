"""
Pydantic schemas for health check and system status.
"""
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response schema."""
    status: str = Field(default="healthy", description="Overall health status")
    service: str = Field(default="gene-cure-ai", description="Service identifier")
    version: str = Field(default="1.0.0", description="API version")
    execution_mode: str = Field(default="DEMO_MODE", description="Active runtime mode: DEMO_MODE or REAL_MODE")
    database_connected: bool = Field(default=True, description="Database connection status")
    grch38_available: bool = Field(default=False, description="Whether GRCh38 local genome FASTA is accessible")
    gencode_available: bool = Field(default=False, description="Whether GENCODE v46 GTF is accessible")
    genome_index_available: bool = Field(default=False, description="Whether FASTA .fai index exists")
    models_loaded: bool = Field(default=False, description="Whether ML weights are loaded in memory")
