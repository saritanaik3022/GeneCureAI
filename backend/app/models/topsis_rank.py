"""
SQLAlchemy ORM model for TOPSIS Multi-Criteria Decision Rankings.
"""
from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import TimeStampedModel


class TOPSISRanking(TimeStampedModel):
    """
    Stores TOPSIS multi-criteria evaluation results and relative closeness rankings.
    """
    __tablename__ = "topsis_rankings"

    run_id = Column(String(36), ForeignKey("pipeline_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    guide_id = Column(String(36), ForeignKey("guide_rnas.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)

    on_target_criterion = Column(Float, nullable=False)
    off_target_criterion = Column(Float, nullable=False)
    cancer_relevance_criterion = Column(Float, nullable=False)
    gc_optimality_criterion = Column(Float, nullable=False)
    distance_positive_ideal = Column(Float, nullable=False)
    distance_negative_ideal = Column(Float, nullable=False)
    closeness_score = Column(Float, nullable=False)  # C_i in [0, 1]
    final_rank = Column(Integer, nullable=False, index=True)

    # Relationships
    guide_rna = relationship("GuideRNA", back_populates="topsis_ranking")
    run = relationship("PipelineRun", back_populates="topsis_rankings")
