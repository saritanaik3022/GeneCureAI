"""
SQLAlchemy ORM model for Pipeline Execution Runs.
"""
from sqlalchemy import Column, String, Integer, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import TimeStampedModel


class PipelineRun(TimeStampedModel):
    """
    Stores 5-stage automated pipeline execution status, inputs, and results.
    """
    __tablename__ = "pipeline_runs"

    gene_id = Column(String(36), ForeignKey("cancer_genes.id", ondelete="CASCADE"), nullable=False, index=True)
    execution_mode = Column(String(20), default="DEMO_MODE", nullable=False)  # 'DEMO_MODE' or 'REAL_MODE'
    status = Column(String(30), default="PENDING", nullable=False)  # 'PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'GENOME_NOT_AVAILABLE'
    weights_json = Column(JSON, nullable=False)  # Dictionary of criteria weights
    total_candidates_found = Column(Integer, default=0, nullable=False)
    top_candidates_retained = Column(Integer, default=0, nullable=False)
    execution_time_ms = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)

    # Relationships
    gene = relationship("CancerGene", back_populates="pipeline_runs")
    guide_rnas = relationship("GuideRNA", back_populates="run", cascade="all, delete-orphan")
    topsis_rankings = relationship("TOPSISRanking", back_populates="run", cascade="all, delete-orphan")
