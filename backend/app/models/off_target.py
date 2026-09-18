"""
SQLAlchemy ORM model for Off-Target Safety and Specificity Evaluations.
"""
from sqlalchemy import Column, String, Integer, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import TimeStampedModel


class OffTargetEvaluation(TimeStampedModel):
    """
    Stores genome-wide off-target search results and CFD-based specificity scores.
    """
    __tablename__ = "off_target_evaluations"

    guide_id = Column(String(36), ForeignKey("guide_rnas.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)

    search_tool_used = Column(String(30), nullable=False)  # 'Bowtie2', 'BLAST+', 'DEMO_FIXTURE'
    reference_genome = Column(String(50), default="GRCh38.p14", nullable=False)
    total_off_targets_found = Column(Integer, default=0, nullable=False)
    mismatch_0_count = Column(Integer, default=0, nullable=False)
    mismatch_1_count = Column(Integer, default=0, nullable=False)
    mismatch_2_count = Column(Integer, default=0, nullable=False)
    mismatch_3_count = Column(Integer, default=0, nullable=False)
    cumulative_cfd_score = Column(Float, default=0.0, nullable=False)
    specificity_score = Column(Float, default=100.0, nullable=False)  # 0.0 to 100.0
    normalized_safety_score = Column(Float, default=1.0, nullable=False)  # 0.0 to 1.0
    detailed_sites = Column(JSON, nullable=True)  # List of identified off-target genomic alignments

    # Relationships
    guide_rna = relationship("GuideRNA", back_populates="off_target_evaluation")
