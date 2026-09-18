"""
SQLAlchemy ORM model for Candidate Guide RNAs.
"""
from sqlalchemy import Column, String, BigInteger, Float, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import TimeStampedModel


class GuideRNA(TimeStampedModel):
    """
    Stores identified candidate CRISPR-Cas9 guide RNAs.
    """
    __tablename__ = "guide_rnas"

    gene_id = Column(String(36), ForeignKey("cancer_genes.id", ondelete="CASCADE"), nullable=False, index=True)
    run_id = Column(String(36), ForeignKey("pipeline_runs.id", ondelete="CASCADE"), nullable=True, index=True)

    protospacer_sequence = Column(String(20), nullable=False, index=True)
    pam_sequence = Column(String(3), nullable=False)
    context_30nt_sequence = Column(String(30), nullable=False)
    strand = Column(String(1), nullable=False)  # '+' or '-'
    genomic_start = Column(BigInteger, nullable=False)
    genomic_end = Column(BigInteger, nullable=False)
    exon_number = Column(Integer, nullable=True)
    gc_percentage = Column(Float, nullable=False)
    has_poly_t_terminator = Column(Boolean, default=False, nullable=False)
    self_complementarity_score = Column(Float, default=0.0, nullable=False)

    # Relationships
    gene = relationship("CancerGene", back_populates="guide_rnas")
    run = relationship("PipelineRun", back_populates="guide_rnas")
    on_target_prediction = relationship("OnTargetPrediction", back_populates="guide_rna", uselist=False, cascade="all, delete-orphan")
    off_target_evaluation = relationship("OffTargetEvaluation", back_populates="guide_rna", uselist=False, cascade="all, delete-orphan")
    topsis_ranking = relationship("TOPSISRanking", back_populates="guide_rna", uselist=False, cascade="all, delete-orphan")
