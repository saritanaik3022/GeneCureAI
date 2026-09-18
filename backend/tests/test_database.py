"""
Tests for database models and session factory.
"""
import pytest
from app.models.cancer_gene import CancerGene
from app.models.guide_rna import GuideRNA
from app.database import AsyncSessionLocal


@pytest.mark.asyncio
async def test_database_model_creation():
    async with AsyncSessionLocal() as session:
        gene = CancerGene(
            symbol="TEST_GENE",
            name="Test Gene for Testing",
            cancer_types=["Breast cancer"],
            ncbi_gene_id="99999",
            ensembl_id="ENSG99999999999",
            hgnc_id="HGNC:99999",
            chromosome="1",
            strand="+",
            genomic_start=1000,
            genomic_end=2000,
            canonical_transcript_id="ENST99999999999",
            cds_sequence="ATGCCC",
            full_transcript_sequence="ATGCCC",
            cancer_relevance_summary="Test summary"
        )
        session.add(gene)
        await session.commit()
        await session.refresh(gene)
        assert gene.id is not None
        assert gene.symbol == "TEST_GENE"
