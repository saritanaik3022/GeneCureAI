"""
Stage 2: Guide RNA Identification endpoints — REAL_MODE + DEMO_MODE.
"""
import logging
import time
from typing import List, Union
from fastapi import APIRouter, HTTPException
from app.schemas.guide_rna import GuideRNAScanRequest, GuideRNAResponse, GuideDesignScanResponse
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger("genecure.guide_design")

# Deterministic demo fixtures (DEMO_MODE only)
DEMO_GUIDES = [
    {
        "id": "demo-guide-001",
        "protospacer_sequence": "GTCACCTTGTCACCTTGAGG",
        "pam_sequence": "TGG",
        "context_30nt_sequence": "ACGTGTCACCTTGTCACCTTGAGGTGGATC",
        "strand": "+",
        "genomic_start": 43045000,
        "genomic_end": 43045023,
        "exon_number": 2,
        "gc_percentage": 55.0,
        "has_poly_t_terminator": False,
        "self_complementarity_score": 0.12,
    },
    {
        "id": "demo-guide-002",
        "protospacer_sequence": "TCCTTCCTTGCAGGAAACCA",
        "pam_sequence": "CGG",
        "context_30nt_sequence": "GAATTCCTTCCTTGCAGGAAACCACGGCCA",
        "strand": "+",
        "genomic_start": 43045150,
        "genomic_end": 43045173,
        "exon_number": 3,
        "gc_percentage": 50.0,
        "has_poly_t_terminator": False,
        "self_complementarity_score": 0.08,
    },
    {
        "id": "demo-guide-003",
        "protospacer_sequence": "GCTATTGAAAATCATTTGTG",
        "pam_sequence": "AGG",
        "context_30nt_sequence": "CAAGGCTATTGAAAATCATTTGTGAGGTTT",
        "strand": "-",
        "genomic_start": 43045300,
        "genomic_end": 43045323,
        "exon_number": 4,
        "gc_percentage": 35.0,
        "has_poly_t_terminator": False,
        "self_complementarity_score": 0.20,
    },
]


@router.post(
    "/scan",
    response_model=Union[GuideDesignScanResponse, List[GuideRNAResponse]],
    tags=["Stage 2: Guide RNA Design"],
)
async def scan_candidate_guides(request: GuideRNAScanRequest):
    """
    Scans forward and reverse-complement DNA strands for SpCas9 PAM (5'-NGG-3') motifs
    and extracts candidate 20-nt protospacers with 30-nt context.

    In REAL_MODE: uses actual GENCODE v46 + GRCh38 datasets.
    In DEMO_MODE: returns deterministic fixture guides.
    """

    # ---- DEMO MODE ----
    if settings.EXECUTION_MODE == "DEMO_MODE":
        logger.info("DEMO_MODE: returning fixture guides")
        return DEMO_GUIDES

    # ---- REAL MODE ----
    gene_symbol = request.gene_symbol
    if not gene_symbol:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "GENE_SYMBOL_REQUIRED",
                "message": "gene_symbol is required in REAL_MODE (custom sequence scanning not yet implemented).",
            },
        )

    # Validate resources are available — never silently fall back
    if not settings.GENOME_FASTA.exists():
        raise HTTPException(
            status_code=503,
            detail={
                "code": "GENOME_NOT_AVAILABLE",
                "message": f"GRCh38 genome FASTA not found at {settings.GENOME_FASTA}. "
                           "Cannot run REAL_MODE without the reference genome.",
            },
        )
    if not settings.GENCODE_GTF.exists():
        raise HTTPException(
            status_code=503,
            detail={
                "code": "GENCODE_NOT_AVAILABLE",
                "message": f"GENCODE v46 GTF not found at {settings.GENCODE_GTF}. "
                           "Cannot run REAL_MODE without the gene annotation.",
            },
        )

    try:
        from app.services.bioinformatics_service import bioinformatics_service

        t0 = time.time()
        result = bioinformatics_service.scan_candidates(
            gene_symbol=gene_symbol,
            gc_min=request.gc_min,
            gc_max=request.gc_max,
            exclude_poly_t=request.exclude_poly_t,
        )
        duration_ms = int((time.time() - t0) * 1000)

        logger.info(
            "REAL_MODE scan complete: gene=%s, transcript=%s, exons=%d, candidates=%d, duration=%dms",
            result.gene_symbol,
            result.transcript_id,
            result.total_exons_scanned,
            result.total_candidates_identified,
            duration_ms,
        )

        candidates_out = []
        for c in result.candidates:
            candidates_out.append(
                GuideRNAResponse(
                    id=c.candidate_id,
                    protospacer_sequence=c.protospacer_sequence,
                    pam_sequence=c.pam_sequence,
                    context_30nt_sequence=c.context_30nt_sequence,
                    strand=c.strand,
                    genomic_start=c.genomic_start,
                    genomic_end=c.genomic_end,
                    exon_number=c.exon_number,
                    gc_percentage=c.gc_percentage,
                    has_poly_t_terminator=c.has_poly_t_terminator,
                    self_complementarity_score=c.self_complementarity_score,
                    gene_id=c.gene_id,
                    chromosome=c.chromosome,
                    reference_assembly=c.reference_assembly,
                    annotation_source=c.annotation_source,
                    sequence_type=c.sequence_type,
                    cleavage_coordinate=c.cleavage_coordinate,
                )
            )

        return GuideDesignScanResponse(
            mode="REAL",
            gene=result.gene_symbol,
            gene_id=result.gene_id,
            genome="GRCh38",
            annotation="GENCODE v46",
            transcript=result.transcript_id,
            chromosome=result.chromosome,
            strand=result.strand,
            sequence_type="EXONIC_CDS",
            total_exons_scanned=result.total_exons_scanned,
            cds_length_scanned=result.cds_length_scanned,
            candidate_count=result.total_candidates_identified,
            candidates=candidates_out,
            filter_summary=result.filter_summary,
        )

    except KeyError as e:
        raise HTTPException(
            status_code=404,
            detail={"code": "GENE_NOT_FOUND", "message": str(e)},
        )
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=503,
            detail={"code": "RESOURCE_NOT_AVAILABLE", "message": str(e)},
        )
    except Exception as e:
        logger.exception("Unexpected error during REAL_MODE guide design scan")
        raise HTTPException(
            status_code=500,
            detail={"code": "INTERNAL_ERROR", "message": str(e)},
        )
