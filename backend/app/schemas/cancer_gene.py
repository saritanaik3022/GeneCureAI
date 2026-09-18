"""
Pydantic schemas for Cancer Target Genes.
"""
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class CancerGeneBase(BaseModel):
    symbol: str = Field(...)
    name: str = Field(...)
    cancer_types: List[str] = Field(...)
    ncbi_gene_id: str = Field(...)
    ensembl_id: str = Field(...)
    hgnc_id: str = Field(...)
    chromosome: str = Field(...)
    strand: str = Field(...)
    genomic_start: int = Field(...)
    genomic_end: int = Field(...)
    canonical_transcript_id: str = Field(...)
    cancer_relevance_summary: str = Field(...)
    depmap_dependency_score: Optional[float] = Field(None)


class CancerGeneCreate(CancerGeneBase):
    cds_sequence: str
    full_transcript_sequence: str


class CancerGeneResponse(CancerGeneBase):
    id: str
    cds_length: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)


class CancerGeneDetailResponse(CancerGeneBase):
    id: str
    cds_sequence: str
    full_transcript_sequence: str
    cds_length: int
    model_config = ConfigDict(from_attributes=True)
