"""
Cancer Genes catalog and metadata endpoints — REAL_MODE + DEMO_MODE.
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.schemas.cancer_gene import CancerGeneResponse, CancerGeneDetailResponse
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger("genecure.cancer_genes")

# Initial curated gene metadata with scientific database provenance (DEMO_MODE)
CURATED_GENE_FIXTURES = [
    {
        "id": "gene-brca1-001",
        "symbol": "BRCA1",
        "name": "BRCA1 DNA repair associated",
        "cancer_types": ["Breast cancer"],
        "ncbi_gene_id": "672",
        "ensembl_id": "ENSG00000012048",
        "hgnc_id": "HGNC:1100",
        "chromosome": "17",
        "strand": "-",
        "genomic_start": 43044295,
        "genomic_end": 43170245,
        "canonical_transcript_id": "ENST00000357654.9",
        "cancer_relevance_summary": "Critical tumor suppressor in homologous recombination repair. Hallmark target in hereditary breast and ovarian carcinomas.",
        "depmap_dependency_score": -0.85,
        "cds_length": 5592
    },
    {
        "id": "gene-her2-002",
        "symbol": "HER2",
        "name": "erb-b2 receptor tyrosine kinase 2 (ERBB2)",
        "cancer_types": ["Breast cancer"],
        "ncbi_gene_id": "2064",
        "ensembl_id": "ENSG00000141736",
        "hgnc_id": "HGNC:3430",
        "chromosome": "17",
        "strand": "+",
        "genomic_start": 39687914,
        "genomic_end": 39730415,
        "canonical_transcript_id": "ENST00000269571.10",
        "cancer_relevance_summary": "Receptor tyrosine kinase frequently amplified and overexpressed in aggressive breast cancers.",
        "depmap_dependency_score": -1.20,
        "cds_length": 3768
    },
    {
        "id": "gene-tp53-003",
        "symbol": "TP53",
        "name": "tumor protein p53",
        "cancer_types": ["Breast cancer", "Lung cancer", "Liver cancer"],
        "ncbi_gene_id": "7157",
        "ensembl_id": "ENSG00000141510",
        "hgnc_id": "HGNC:11998",
        "chromosome": "17",
        "strand": "-",
        "genomic_start": 7668402,
        "genomic_end": 7687550,
        "canonical_transcript_id": "ENST00000269305.9",
        "cancer_relevance_summary": "Guardian of the genome; most frequently mutated tumor suppressor across breast, lung, and liver malignancies.",
        "depmap_dependency_score": -0.42,
        "cds_length": 1182
    },
    {
        "id": "gene-egfr-004",
        "symbol": "EGFR",
        "name": "epidermal growth factor receptor",
        "cancer_types": ["Lung cancer"],
        "ncbi_gene_id": "1956",
        "ensembl_id": "ENSG00000146648",
        "hgnc_id": "HGNC:3236",
        "chromosome": "7",
        "strand": "+",
        "genomic_start": 55019017,
        "genomic_end": 55211628,
        "canonical_transcript_id": "ENST00000275493.7",
        "cancer_relevance_summary": "Driver oncogene in non-small cell lung cancer (NSCLC) harboring activating tyrosine kinase domain mutations.",
        "depmap_dependency_score": -1.15,
        "cds_length": 3633
    },
    {
        "id": "gene-kras-005",
        "symbol": "KRAS",
        "name": "KRAS proto-oncogene, GTPase",
        "cancer_types": ["Lung cancer"],
        "ncbi_gene_id": "3845",
        "ensembl_id": "ENSG00000133703",
        "hgnc_id": "HGNC:6407",
        "chromosome": "12",
        "strand": "-",
        "genomic_start": 25204789,
        "genomic_end": 25250929,
        "canonical_transcript_id": "ENST00000256078.10",
        "cancer_relevance_summary": "GTPase transducing growth factor signals, frequently mutated in codon 12/13 in lung adenocarcinomas.",
        "depmap_dependency_score": -1.45,
        "cds_length": 570
    },
    {
        "id": "gene-alk-006",
        "symbol": "ALK",
        "name": "ALK receptor tyrosine kinase",
        "cancer_types": ["Lung cancer"],
        "ncbi_gene_id": "238",
        "ensembl_id": "ENSG00000171094",
        "hgnc_id": "HGNC:427",
        "chromosome": "2",
        "strand": "-",
        "genomic_start": 29192774,
        "genomic_end": 29479367,
        "canonical_transcript_id": "ENST00000389048.8",
        "cancer_relevance_summary": "Receptor tyrosine kinase participating in oncogenic EML4-ALK gene fusions driving lung carcinogenesis.",
        "depmap_dependency_score": -0.92,
        "cds_length": 4863
    },
    {
        "id": "gene-ctnnb1-007",
        "symbol": "CTNNB1",
        "name": "catenin beta 1",
        "cancer_types": ["Liver cancer"],
        "ncbi_gene_id": "1499",
        "ensembl_id": "ENSG00000168036",
        "hgnc_id": "HGNC:2514",
        "chromosome": "3",
        "strand": "+",
        "genomic_start": 41199505,
        "genomic_end": 41240942,
        "canonical_transcript_id": "ENST00000349496.11",
        "cancer_relevance_summary": "Key downstream effector of canonical Wnt signaling path, hyperactivated in hepatocellular carcinoma.",
        "depmap_dependency_score": -1.10,
        "cds_length": 2346
    },
    {
        "id": "gene-axin1-008",
        "symbol": "AXIN1",
        "name": "axin 1",
        "cancer_types": ["Liver cancer"],
        "ncbi_gene_id": "8312",
        "ensembl_id": "ENSG00000103126",
        "hgnc_id": "HGNC:903",
        "chromosome": "16",
        "strand": "-",
        "genomic_start": 339000,
        "genomic_end": 404000,
        "canonical_transcript_id": "ENST00000262325.8",
        "cancer_relevance_summary": "Negative regulator of Wnt/beta-catenin signaling; loss-of-function driver in liver tumorigenesis.",
        "depmap_dependency_score": -0.38,
        "cds_length": 2589
    },
    {
        "id": "gene-tert-009",
        "symbol": "TERT",
        "name": "telomerase reverse transcriptase",
        "cancer_types": ["Liver cancer"],
        "ncbi_gene_id": "7015",
        "ensembl_id": "ENSG00000164362",
        "hgnc_id": "HGNC:11730",
        "chromosome": "5",
        "strand": "-",
        "genomic_start": 1253147,
        "genomic_end": 1295068,
        "canonical_transcript_id": "ENST00000310581.10",
        "cancer_relevance_summary": "Catalytic subunit of telomerase; promoter mutations are the most frequent somatic alterations in hepatocellular carcinoma.",
        "depmap_dependency_score": -0.78,
        "cds_length": 3399
    }
]

# Cache real gene data after first load
_real_gene_cache: Optional[List[dict]] = None


def _get_real_gene_data() -> List[dict]:
    """Lazily loads real gene data from GENCODE v46 + GRCh38."""
    global _real_gene_cache
    if _real_gene_cache is not None:
        return _real_gene_cache

    try:
        from app.services.bioinformatics_service import bioinformatics_service
        _real_gene_cache = bioinformatics_service.get_all_cancer_genes()
        logger.info("Loaded %d real cancer gene records from GENCODE/GRCh38", len(_real_gene_cache))
        return _real_gene_cache
    except Exception as e:
        logger.error("Failed to load real gene data: %s", e)
        raise


@router.get("", response_model=List[CancerGeneResponse], tags=["Stage 1: Cancer Genes"])
async def list_cancer_genes(cancer_type: Optional[str] = Query(None, description="Filter by cancer type")):
    """List curated cancer-related target genes with provenance."""
    if settings.EXECUTION_MODE == "DEMO_MODE":
        source = CURATED_GENE_FIXTURES
    else:
        try:
            source = _get_real_gene_data()
        except Exception:
            raise HTTPException(
                status_code=503,
                detail={"code": "RESOURCE_NOT_AVAILABLE", "message": "Real genomic resources unavailable."}
            )

    if cancer_type:
        filtered = [g for g in source if any(cancer_type.lower() in ct.lower() for ct in g["cancer_types"])]
        return filtered
    return source


@router.get("/{symbol}", response_model=CancerGeneDetailResponse, tags=["Stage 1: Cancer Genes"])
async def get_cancer_gene_detail(symbol: str):
    """Retrieve detailed genomic coordinates, CDS transcript, and biological provenance."""
    if settings.EXECUTION_MODE == "DEMO_MODE":
        source = CURATED_GENE_FIXTURES
    else:
        try:
            source = _get_real_gene_data()
        except Exception:
            raise HTTPException(
                status_code=503,
                detail={"code": "RESOURCE_NOT_AVAILABLE", "message": "Real genomic resources unavailable."}
            )

    for gene in source:
        if gene["symbol"].upper() == symbol.upper() or (symbol.upper() == "HER2" and gene["symbol"].upper() == "HER2"):
            return {
                **gene,
                "cds_sequence": gene.get("cds_sequence", ""),
                "full_transcript_sequence": gene.get("full_transcript_sequence", ""),
                "cds_length": gene.get("cds_length", 0)
            }

    raise HTTPException(status_code=404, detail=f"Gene '{symbol}' not found in registry.")
