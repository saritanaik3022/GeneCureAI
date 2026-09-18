"""
SQLAlchemy ORM model for Cancer Target Genes.
"""
from sqlalchemy import Column, String, BigInteger, Float, Text, JSON
from sqlalchemy.orm import relationship
from app.models.base import TimeStampedModel


class CancerGene(TimeStampedModel):
    """
    Stores curated cancer genes with genomic coordinates and database provenance.
    """
    __tablename__ = "cancer_genes"

    symbol = Column(String(30), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    cancer_types = Column(JSON, nullable=False)  # List of strings e.g. ["Breast cancer"]
    ncbi_gene_id = Column(String(50), nullable=False)
    ensembl_id = Column(String(50), nullable=False)
    hgnc_id = Column(String(50), nullable=False)
    chromosome = Column(String(10), nullable=False)
    strand = Column(String(1), nullable=False)  # '+' or '-'
    genomic_start = Column(BigInteger, nullable=False)
    genomic_end = Column(BigInteger, nullable=False)
    canonical_transcript_id = Column(String(50), nullable=False)
    cds_sequence = Column(Text, nullable=False)
    full_transcript_sequence = Column(Text, nullable=False)
    cancer_relevance_summary = Column(Text, nullable=False)
    depmap_dependency_score = Column(Float, nullable=True)

    # Relationships
    guide_rnas = relationship("GuideRNA", back_populates="gene", cascade="all, delete-orphan")
    pipeline_runs = relationship("PipelineRun", back_populates="gene", cascade="all, delete-orphan")
